"""Bling API client implementation."""
from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Type, TypeVar
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from src.app.core.settings import Settings, get_settings
from src.app.services.bling.oauth import BlingOAuthClient, BlingOAuthError

LOGGER = logging.getLogger(__name__)


class BlingAPIError(RuntimeError):
    """Domain specific error for Bling API interactions."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, payload: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


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
    page_param: str = "pagina"
    limit_param: str = "limite"
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
        rate_limit_per_second: int = 2,
        daily_limit: int = 120_000,
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
        self._rate_limit_per_second = max(rate_limit_per_second, 0)
        self._rate_limit_interval = (60.0 / self._rate_limit_per_second) if self._rate_limit_per_second else 0.0
        self._max_retries = max(1, max_retries)
        self._backoff_factor = max(0.0, backoff_factor)
        self._timeout = timeout
        self._metrics = metrics or BlingMetrics()
        self._logger = logger or LOGGER

        self._oauth_client = BlingOAuthClient(
            settings=self._settings,
            session=self._session,
            timeout=self._timeout,
            logger=self._logger,
        )

        self._rate_lock = threading.Lock()
        self._last_request_ts = 0.0

        self._current_second_start = time.monotonic()
        self._requests_in_current_second = 0

        self._daily_limit = daily_limit
        self._daily_count = 0
        self._daily_reset_date = datetime.now(timezone.utc).date()
        self._daily_lock = threading.Lock()


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
            is_retry = attempt > 1

            # 1) Token + headers
            token = self._obtain_token(force_refresh=force_refresh)
            request_headers = self._build_request_headers(token, headers)

            # 2) Limites (diário e por segundo)
            self._respect_daily_limit()
            self._respect_rate_limit()

            # 3) HTTP request com métricas e tratamento de erros de rede
            try:
                response, duration = self._perform_http_request(
                    method=method,
                    url=url,
                    params=params,
                    json_body=json_body,
                    headers=request_headers,
                    is_retry=is_retry,
                )
            except requests.RequestException as exc:
                last_error = exc
                self._handle_network_exception(exc, url, resource, attempt)
                continue

            # 4) Métricas de resposta bem-sucedida (HTTP nível transporte)
            self._metrics.record_request(
                duration=duration,
                status_code=response.status_code,
                is_retry=is_retry,
            )

            # 5) Lógica de tratamento por status code
            # 401: tenta renovar token uma vez
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

            # Status codes "retriáveis" (408, 425, 429, 5xx)
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

            # 4xx/5xx não tratáveis: levantar erro de domínio
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

        # Se chegou aqui, estourou número de tentativas
        if last_error is not None:  # pragma: no cover - defensive
            raise BlingAPIError("Maximum retries exceeded") from last_error
        raise BlingAPIError("Maximum retries exceeded for request")

    def _obtain_token(self, *, force_refresh: bool):
        """Obtém um token OAuth válido, usando cache quando possível."""
        try:
            # Usa token já carregado se ainda for válido
            if self._oauth_client._token and not self._oauth_client._token.is_expired():
                return self._oauth_client._token
            # Caso contrário, delega para o fluxo normal do OAuthClient
            return self._oauth_client.get_token(force_refresh=force_refresh)
        except BlingOAuthError as exc:
            raise BlingAPIError(f"Failed to obtain OAuth token: {exc}") from exc

    def _build_request_headers(
        self,
        token,
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, str]:
        """Monta os headers da requisição, incluindo Authorization."""
        request_headers: Dict[str, str] = {
            "Authorization": f"Bearer {token.access_token}",
        }

        if extra_headers:
            request_headers.update(extra_headers)

        return request_headers

    def _perform_http_request(
        self,
        *,
        method: str,
        url: str,
        params: Optional[Mapping[str, Any]],
        json_body: Optional[Mapping[str, Any]],
        headers: Mapping[str, str],
        is_retry: bool,
    ) -> Tuple[requests.Response, float]:
        """Executa a chamada HTTP e registra métricas em caso de falha de rede."""
        start = time.perf_counter()

        try:
            response = self._session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            duration = time.perf_counter() - start
            # status_code = 0 para indicar erro de rede (sem resposta HTTP)
            self._metrics.record_request(
                duration=duration,
                status_code=0,
                is_retry=is_retry,
            )
            raise exc

        duration = time.perf_counter() - start
        return response, duration

    def _handle_network_exception(
        self,
        exc: requests.RequestException,
        url: str,
        resource: Optional[str],
        attempt: int,
    ) -> None:
        """Loga erro de rede e decide se deve encerrar ou tentar novamente."""
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
        if attempt >= self._max_retries:
            # Mantém a mensagem original de erro de rede
            raise BlingAPIError("Exceeded maximum retries due to network errors") from exc

    def _respect_rate_limit(self) -> None:
        if self._rate_limit_per_second <= 0:
            return

        with self._rate_lock:
            now = time.monotonic()
            elapsed = now - self._current_second_start

            # Se passou de 1s, reseta a janela
            if elapsed >= 1.0:
                self._current_second_start = now
                self._requests_in_current_second = 0

            # Se já atingiu o limite, espera até virar o segundo
            if self._requests_in_current_second >= self._rate_limit_per_second:
                sleep_for = 1.0 - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
                # Começa nova janela
                self._current_second_start = time.monotonic()
                self._requests_in_current_second = 0

            self._requests_in_current_second += 1

    def _respect_daily_limit(self) -> None:
        if self._daily_limit <= 0:
            return

        with self._daily_lock:
            today = datetime.now(timezone.utc).date()
            if today != self._daily_reset_date:
                # Virou o dia → reseta contador
                self._daily_reset_date = today
                self._daily_count = 0

            if self._daily_count >= self._daily_limit:
                raise BlingAPIError(
                    "Daily API request limit reached in client; aborting to avoid 429 from Bling."
                )

            self._daily_count += 1

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
