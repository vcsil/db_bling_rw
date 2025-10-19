"""Bling API client implementation."""
from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Type, TypeVar
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field

from app.core.settings import Settings, get_settings

LOGGER = logging.getLogger(__name__)


class BlingAPIError(RuntimeError):
    """Domain specific error for Bling API interactions."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, payload: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class OAuthToken(BaseModel):
    """Represents the OAuth2 token payload returned by Bling."""

    access_token: str = Field(alias="access_token")
    token_type: str = Field(alias="token_type")
    expires_in: int = Field(alias="expires_in")
    scope: Optional[str] = Field(default=None, alias="scope")
    refresh_token: Optional[str] = Field(default=None, alias="refresh_token")
    obtained_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
    }

    @property
    def expires_at(self) -> datetime:
        """Return the moment when the token expires."""

        return self.obtained_at + timedelta(seconds=self.expires_in)

    def is_expired(self, *, leeway: int = 60) -> bool:
        """Check whether the token has expired, considering an optional leeway."""

        return datetime.now(timezone.utc) >= (self.expires_at - timedelta(seconds=leeway))


class BlingBaseModel(BaseModel):
    """Base Pydantic model used by resource specific models."""

    id: Optional[int] = Field(default=None, alias="id")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }


class ContactModel(BlingBaseModel):
    """Representation of a Bling contact."""

    nome: Optional[str] = None
    situacao: Optional[str] = None
    tipo: Optional[str] = None


class ProductModel(BlingBaseModel):
    """Representation of a Bling product."""

    nome: Optional[str] = None
    codigo: Optional[str] = None
    tipo: Optional[str] = None


class OrderModel(BlingBaseModel):
    """Representation of a Bling sales order."""

    numero: Optional[str] = None
    situacao: Optional[str] = None
    data: Optional[str] = None


class AccountModel(BlingBaseModel):
    """Representation of a Bling financial account."""

    descricao: Optional[str] = None
    situacao: Optional[str] = None
    valor: Optional[float] = None


BlingModelT = TypeVar("BlingModelT", bound=BlingBaseModel)


@dataclass(frozen=True)
class BlingResourceConfig:
    """Metadata describing how to paginate and parse a Bling resource."""

    name: str
    path: str
    model: Type[BlingModelT]
    items_path: Tuple[str, ...] = ("data",)
    page_param: str = "page"
    limit_param: str = "limit"
    default_page_size: int = 100

    def extract_items(self, payload: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        """Extract the items list from an API payload."""

        current: Any = payload
        for key in self.items_path:
            if not isinstance(current, Mapping):
                return []
            current = current.get(key)
            if current is None:
                return []
        if isinstance(current, list):
            return current  # type: ignore[return-value]
        if isinstance(current, Mapping) and "data" in current:
            maybe_data = current.get("data")
            if isinstance(maybe_data, list):
                return maybe_data  # type: ignore[return-value]
        return []


class BlingMetrics:
    """In-memory metrics aggregator for Bling API calls."""

    def __init__(self) -> None:
        self.requests_total = 0
        self.errors_total = 0
        self.retries_total = 0
        self.total_latency_seconds = 0.0
        self._lock = threading.Lock()

    def record_request(self, *, duration: float, status_code: int, is_retry: bool) -> None:
        with self._lock:
            self.requests_total += 1
            self.total_latency_seconds += duration
            if is_retry:
                self.retries_total += 1
            if status_code >= 400:
                self.errors_total += 1

    @property
    def average_latency_seconds(self) -> float:
        with self._lock:
            if self.requests_total == 0:
                return 0.0
            return self.total_latency_seconds / self.requests_total


class BlingClient:
    """High level client used to communicate with the Bling REST API."""

    DEFAULT_API_BASE_URL = "https://www.bling.com.br/Api/v3/"
    TOKEN_ENDPOINT = "oauth/token"
    RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}

    RESOURCE_MAP: Dict[str, BlingResourceConfig] = {
        "contatos": BlingResourceConfig(
            name="contatos",
            path="contatos",
            model=ContactModel,
        ),
        "produtos": BlingResourceConfig(
            name="produtos",
            path="produtos",
            model=ProductModel,
        ),
        "pedidos": BlingResourceConfig(
            name="pedidos",
            path="pedidos/vendas",
            model=OrderModel,
        ),
        "contas": BlingResourceConfig(
            name="contas",
            path="contas/pagar-receber",
            model=AccountModel,
        ),
    }

    def __init__(
        self,
        *,
        settings: Optional[Settings] = None,
        session: Optional[requests.Session] = None,
        api_base_url: Optional[str] = None,
        rate_limit_per_minute: int = 60,
        max_retries: int = 5,
        backoff_factor: float = 0.5,
        timeout: float = 30.0,
        metrics: Optional[BlingMetrics] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._session = session or requests.Session()
        self._session.headers.setdefault("Accept", "application/json")
        self._api_base_url = api_base_url or self.DEFAULT_API_BASE_URL
        self._rate_limit_per_minute = max(rate_limit_per_minute, 0)
        self._rate_limit_interval = (60.0 / self._rate_limit_per_minute) if self._rate_limit_per_minute else 0.0
        self._max_retries = max(1, max_retries)
        self._backoff_factor = max(0.0, backoff_factor)
        self._timeout = timeout
        self._metrics = metrics or BlingMetrics()
        self._logger = logger or LOGGER

        self._token_lock = threading.Lock()
        self._token: Optional[OAuthToken] = None
        self._rate_lock = threading.Lock()
        self._last_request_ts = 0.0

    # ------------------------------------------------------------------
    # OAuth token handling
    # ------------------------------------------------------------------
    def _get_token(self, *, force_refresh: bool = False) -> OAuthToken:
        with self._token_lock:
            if force_refresh:
                self._logger.info(
                    "bling.oauth.refresh",
                    extra={
                        "event": "bling.oauth.refresh",
                        "message": "Forcing OAuth token refresh",
                    },
                )
                self._token = None
            if self._token is None or self._token.is_expired():
                self._token = self._fetch_token()
            return self._token

    def _fetch_token(self) -> OAuthToken:
        oauth_url = urljoin(str(self._settings.oauth_baseurl), self.TOKEN_ENDPOINT)
        payload = {
            "grant_type": "password",
            "client_id": self._settings.bling_client_id,
            "client_secret": self._settings.bling_client_secret,
            "username": self._settings.bling_usuario,
            "password": self._settings.bling_senha_usuario,
        }
        self._logger.info(
            "bling.oauth.request",
            extra={
                "event": "bling.oauth.request",
                "url": oauth_url,
            },
        )
        try:
            response = self._session.post(oauth_url, data=payload, timeout=self._timeout)
        except requests.RequestException as exc:  # pragma: no cover - network issues
            raise BlingAPIError("Failed to obtain OAuth token") from exc
        if response.status_code >= 400:
            raise BlingAPIError(
                f"OAuth token request failed with status {response.status_code}",
                status_code=response.status_code,
                payload=self._safe_json(response),
            )
        data = response.json()
        data.setdefault("obtained_at", datetime.now(timezone.utc))
        token = OAuthToken.model_validate(data)
        self._logger.info(
            "bling.oauth.success",
            extra={
                "event": "bling.oauth.success",
                "expires_in": token.expires_in,
            },
        )
        return token

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def metrics(self) -> BlingMetrics:
        return self._metrics

    def fetch_all(self, resource_name: str, params: Optional[MutableMapping[str, Any]] = None) -> List[BlingModelT]:
        """Fetch all items from the given resource as a list."""

        config = self._get_resource_config(resource_name)
        return list(self._paginate(config, params=params))

    def fetch_contatos(self, params: Optional[MutableMapping[str, Any]] = None) -> List[ContactModel]:
        return self.fetch_all("contatos", params=params)

    def fetch_produtos(self, params: Optional[MutableMapping[str, Any]] = None) -> List[ProductModel]:
        return self.fetch_all("produtos", params=params)

    def fetch_pedidos(self, params: Optional[MutableMapping[str, Any]] = None) -> List[OrderModel]:
        return self.fetch_all("pedidos", params=params)

    def fetch_contas(self, params: Optional[MutableMapping[str, Any]] = None) -> List[AccountModel]:
        return self.fetch_all("contas", params=params)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_resource_config(self, resource_name: str) -> BlingResourceConfig:
        try:
            return self.RESOURCE_MAP[resource_name]
        except KeyError as exc:  # pragma: no cover - defensive programming
            raise BlingAPIError(f"Unsupported resource '{resource_name}'") from exc

    def _paginate(
        self,
        config: BlingResourceConfig,
        *,
        params: Optional[MutableMapping[str, Any]] = None,
    ) -> Iterator[BlingModelT]:
        page = 1
        params = dict(params or {})
        while True:
            params[config.page_param] = page
            params.setdefault(config.limit_param, config.default_page_size)
            self._logger.info(
                "bling.fetch.page",
                extra={
                    "event": "bling.fetch.page",
                    "resource": config.name,
                    "page": page,
                    "params": {k: v for k, v in params.items() if k != config.page_param},
                },
            )
            response = self._send_request("GET", config.path, params=params, resource=config.name)
            payload = self._safe_json(response)
            items = config.extract_items(payload)
            if not items:
                break
            for item in items:
                model = config.model.model_validate(item)
                yield model
            if len(items) < params[config.limit_param]:
                break
            page += 1

    def _send_request(
        self,
        method: str,
        path: str,
        *,
        resource: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> requests.Response:
        url = urljoin(self._api_base_url, path)
        attempt = 0
        last_error: Optional[Exception] = None
        force_refresh = False
        while attempt < self._max_retries:
            attempt += 1
            token = self._get_token(force_refresh=force_refresh)
            request_headers = {"Authorization": f"Bearer {token.access_token}"}
            if headers:
                request_headers.update(headers)
            is_retry = attempt > 1
            self._respect_rate_limit()
            start = time.perf_counter()
            try:
                response = self._session.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=request_headers,
                    timeout=self._timeout,
                )
            except requests.RequestException as exc:
                duration = time.perf_counter() - start
                self._metrics.record_request(duration=duration, status_code=0, is_retry=is_retry)
                self._logger.error(
                    "bling.request.error",
                    exc_info=exc,
                    extra={
                        "event": "bling.request.error",
                        "resource": resource,
                        "attempt": attempt,
                        "url": url,
                    },
                )
                last_error = exc
                if attempt >= self._max_retries:
                    raise BlingAPIError("Exceeded maximum retries due to network errors") from exc
                self._sleep_backoff(attempt)
                continue
            duration = time.perf_counter() - start
            self._metrics.record_request(duration=duration, status_code=response.status_code, is_retry=is_retry)

            if response.status_code == 401 and not force_refresh:
                self._logger.warning(
                    "bling.request.unauthorized",
                    extra={
                        "event": "bling.request.unauthorized",
                        "resource": resource,
                        "url": url,
                        "attempt": attempt,
                    },
                )
                force_refresh = True
                self._sleep_backoff(attempt)
                continue

            if response.status_code in self.RETRYABLE_STATUS_CODES:
                self._logger.warning(
                    "bling.request.retry",
                    extra={
                        "event": "bling.request.retry",
                        "resource": resource,
                        "status_code": response.status_code,
                        "attempt": attempt,
                        "url": url,
                    },
                )
                if attempt >= self._max_retries:
                    break
                force_refresh = False
                self._sleep_backoff(attempt)
                continue

            if response.status_code >= 400:
                payload = self._safe_json(response)
                self._logger.error(
                    "bling.request.failed",
                    extra={
                        "event": "bling.request.failed",
                        "resource": resource,
                        "status_code": response.status_code,
                        "payload": payload,
                        "url": url,
                    },
                )
                raise BlingAPIError(
                    f"Bling API call failed with status {response.status_code}",
                    status_code=response.status_code,
                    payload=payload,
                )
            return response

        if last_error is not None:  # pragma: no cover - defensive
            raise BlingAPIError("Maximum retries exceeded") from last_error
        raise BlingAPIError("Maximum retries exceeded for request")

    def _respect_rate_limit(self) -> None:
        if self._rate_limit_interval <= 0:
            return
        with self._rate_lock:
            now = time.monotonic()
            elapsed = now - self._last_request_ts
            wait_time = self._rate_limit_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            self._last_request_ts = time.monotonic()

    def _sleep_backoff(self, attempt: int) -> None:
        if self._backoff_factor == 0:
            return
        sleep_for = self._backoff_factor * (2 ** (attempt - 1))
        time.sleep(min(sleep_for, 60))

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            try:
                return json.loads(response.text)
            except ValueError:
                return response.text


__all__ = [
    "AccountModel",
    "BlingAPIError",
    "BlingBaseModel",
    "BlingClient",
    "BlingMetrics",
    "BlingResourceConfig",
    "ContactModel",
    "OrderModel",
    "ProductModel",
]
