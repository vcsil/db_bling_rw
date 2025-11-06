"""Utilitários de autenticação OAuth para a API do Bling."""
from __future__ import annotations

import base64
import json
import logging
import secrets
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Mapping, Optional
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit

import requests
from dotenv import find_dotenv
from pydantic import BaseModel, Field

from app.core.settings import Settings, get_settings, set_settings

LOGGER = logging.getLogger(__name__)


class BlingOAuthError(RuntimeError):
    """Erro de domínio para falhas na autenticação OAuth do Bling."""


class OAuthToken(BaseModel):
    """Representa o payload do token OAuth2 retornado pelo Bling."""

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
        """Retorna o momento exato em que o token expira."""

        return self.obtained_at + timedelta(seconds=self.expires_in)

    def is_expired(self, *, leeway: int = 60) -> bool:
        """Indica se o token já expirou considerando uma folga opcional."""

        return datetime.now(timezone.utc) >= (self.expires_at - timedelta(seconds=leeway))


class BlingOAuthClient:
    """Cliente responsável por todo o fluxo OAuth com o Bling."""

    AUTHORIZE_ENDPOINT = "oauth/authorize"
    TOKEN_ENDPOINT = "oauth/token"

    ENV_ACCESS_TOKEN_KEY = "OAUTH_ACCESS_TOKEN"
    ENV_EXPIRES_IN_KEY = "OAUTH_EXPIRES_IN"
    ENV_EXPIRES_AT_KEY = "OAUTH_HOURS_EXPIRATION"
    ENV_REFRESH_TOKEN_KEY = "OAUTH_REFRESH_TOKEN"
    ENV_SCOPE_KEY = "OAUTH_SCOPE"

    def __init__(
        self,
        *,
        settings: Optional[Settings] = None,
        session: Optional[requests.Session] = None,
        timeout: float = 30.0,
        logger: Optional[logging.Logger] = None,
        env_path: Optional[str] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._session = session or requests.Session()
        self._timeout = timeout
        self._logger = logger or LOGGER
        self._env_path = env_path or self._default_env_path()

        self._token_lock = threading.Lock()
        self._token: Optional[OAuthToken] = None
        self._refresh_token = self._settings.bling_refresh_token

    # ------------------------------------------------------------------
    # Fluxo público
    # ------------------------------------------------------------------
    def build_authorization_url(
        self,
        *,
        state: Optional[str] = None,
        scope: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> str:
        """Monta a URL de autorização conforme a documentação oficial."""

        base_url = urljoin(str(self._settings.oauth_baseurl), self.AUTHORIZE_ENDPOINT)
        params: Dict[str, Any] = {
            "response_type": "code",
            "client_id": self._settings.bling_client_id,
        }
        final_state = state or secrets.token_urlsafe(16)
        params["state"] = final_state
        final_redirect = redirect_uri or (
            str(self._settings.bling_redirect_uri) if self._settings.bling_redirect_uri else None
        )
        if final_redirect:
            params["redirect_uri"] = final_redirect
        final_scope = scope or self._settings.bling_oauth_scope
        if final_scope:
            params["scope"] = final_scope
        query = urlencode(params)
        return f"{base_url}?{query}"

    def exchange_code_for_token(
        self,
        code: str,
        *,
        redirect_uri: Optional[str] = None,
        save_to_env: bool = True,
    ) -> OAuthToken:
        """Troca um authorization code por um access token."""

        payload: Dict[str, Any] = {
            "grant_type": "authorization_code",
            "code": code,
        }
        final_redirect = redirect_uri or (
            str(self._settings.bling_redirect_uri) if self._settings.bling_redirect_uri else None
        )
        if final_redirect:
            payload["redirect_uri"] = final_redirect

        token = self._request_token(payload)
        self._refresh_token = token.refresh_token or self._refresh_token
        if save_to_env:
            self._persist_token(token)
        return token

    def refresh_access_token(self, *, save_to_env: bool = True) -> OAuthToken:
        """Atualiza o access token utilizando o refresh token configurado."""

        refresh_token = self._refresh_token
        if not refresh_token:
            raise BlingOAuthError(
                "Refresh token inexistente. Execute o fluxo de autorização inicial para obtê-lo."
            )
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        token = self._request_token(payload)
        self._refresh_token = token.refresh_token or refresh_token
        if save_to_env:
            self._persist_token(token)
        return token

    def get_token(self, *, force_refresh: bool = False) -> OAuthToken:
        """Retorna um token válido, atualizando-o quando necessário."""

        with self._token_lock:
            if force_refresh:
                self._logger.info(
                    "bling.oauth.refresh",
                    extra={"event": "bling.oauth.refresh", "message": "Forçando renovação do token"},
                )
                self._token = None
            if self._token is None or self._token.is_expired():
                self._logger.info(
                    "bling.oauth.renew",
                    extra={"event": "bling.oauth.renew", "message": "Obtendo novo token via refresh"},
                )
                self._token = self.refresh_access_token()
            return self._token

    def authorize_with_browser(
        self,
        *,
        state: Optional[str] = None,
        scope: Optional[str] = None,
        headless: bool = True,
        save_to_env: bool = True,
    ) -> OAuthToken:
        """Executa o fluxo interativo de autorização via Selenium."""

        try:
            from selenium import webdriver
            from selenium.common.exceptions import NoSuchElementException
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as exc:  # pragma: no cover - dependência opcional
            raise BlingOAuthError("Dependências do Selenium não instaladas") from exc

        options = self._build_chrome_options(headless=headless)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(2)

        final_state = state or secrets.token_urlsafe(16)
        authorization_url = self.build_authorization_url(state=final_state, scope=scope)
        self._logger.info(
            "bling.oauth.browser.start",
            extra={
                "event": "bling.oauth.browser.start",
                "url": authorization_url,
                "state": final_state,
            },
        )
        driver.get(authorization_url)

        driver.find_element(By.XPATH, "/html/body/div/div/div/form/div[2]/input").send_keys(
            self._settings.bling_usuario
        )
        driver.find_element(By.XPATH, "/html/body/div/div/div/form/div[3]/input").send_keys(
            self._settings.bling_senha_usuario
        )
        driver.find_element(By.XPATH, "/html/body/div/div/div/form/div[6]/button").click()

        try:
            driver.find_element(By.XPATH, "/html/body/div/div/div/div/div[6]/form/button[2]").click()
        except NoSuchElementException:
            self._logger.info(
                "bling.oauth.browser.reuse",
                extra={
                    "event": "bling.oauth.browser.reuse",
                    "message": "Sessão previamente autorizada reutilizada",
                },
            )
        finally:
            final_url = driver.current_url
            driver.quit()

        parsed = urlsplit(final_url)
        params = parse_qs(parsed.query)
        codes = params.get("code")
        if not codes:
            raise BlingOAuthError("Código de autorização não encontrado na URL de retorno")

        token = self.exchange_code_for_token(codes[0], save_to_env=save_to_env)
        self._logger.info(
            "bling.oauth.browser.success",
            extra={"event": "bling.oauth.browser.success", "expires_in": token.expires_in},
        )
        return token

    # ------------------------------------------------------------------
    # Implementação interna
    # ------------------------------------------------------------------
    def _request_token(self, payload: Mapping[str, Any]) -> OAuthToken:
        token_url = urljoin(str(self._settings.oauth_baseurl), self.TOKEN_ENDPOINT)
        headers = {
            "Authorization": self._basic_authorization_header(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self._logger.info(
            "bling.oauth.token.request",
            extra={"event": "bling.oauth.token.request", "payload": dict(payload)},
        )
        try:
            response = self._session.post(
                token_url,
                json=dict(payload),
                headers=headers,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - falha de rede
            raise BlingOAuthError("Falha ao se comunicar com o endpoint OAuth do Bling") from exc

        data = self._safe_json(response)
        if response.status_code >= 400:
            self._logger.error(
                "bling.oauth.token.error",
                extra={
                    "event": "bling.oauth.token.error",
                    "status_code": response.status_code,
                    "payload": data,
                },
            )
            raise BlingOAuthError(
                f"Solicitação de token retornou status {response.status_code}",
            )

        if isinstance(data, Mapping):
            data = dict(data)
        else:
            raise BlingOAuthError("Resposta inesperada do endpoint OAuth do Bling")

        data.setdefault("obtained_at", datetime.now(timezone.utc))
        token = OAuthToken.model_validate(data)
        return token

    def _persist_token(self, token: OAuthToken) -> None:
        if not self._env_path:
            return
        try:
            set_settings(
                {
                    self.ENV_ACCESS_TOKEN_KEY: token.access_token,
                    self.ENV_EXPIRES_IN_KEY: str(token.expires_in),
                    self.ENV_REFRESH_TOKEN_KEY: token.refresh_token or "",
                    self.ENV_SCOPE_KEY: token.scope or "",
                    self.ENV_EXPIRES_AT_KEY: token.expires_at.isoformat(),
                },
                env_path=self._env_path,
            )
        except OSError as exc:  # pragma: no cover - ambiente restrito
            self._logger.warning(
                "bling.oauth.persist.failed",
                extra={"event": "bling.oauth.persist.failed", "error": str(exc)},
            )

    def _basic_authorization_header(self) -> str:
        credential = f"{self._settings.bling_client_id}:{self._settings.bling_client_secret}"
        encoded = base64.b64encode(credential.encode("utf-8")).decode("ascii")
        return f"Basic {encoded}"

    def _default_env_path(self) -> Optional[str]:
        path = find_dotenv(usecwd=True)
        return path or None

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            try:
                return json.loads(response.text)
            except ValueError:
                return response.text

    @staticmethod
    def _build_chrome_options(*, headless: bool) -> "Options":  # pragma: no cover - dependência externa
        from selenium.webdriver.chrome.options import Options

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        prefs: Dict[str, Any] = {"profile.default_content_settings": {"images": 2}}
        options.experimental_options["prefs"] = prefs
        return options


__all__ = [
    "BlingOAuthClient",
    "BlingOAuthError",
    "OAuthToken",
]

