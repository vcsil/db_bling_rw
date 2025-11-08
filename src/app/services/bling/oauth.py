"""Utilitários de autenticação OAuth para a API do Bling."""
from __future__ import annotations

from urllib.parse import parse_qs, urlencode, urljoin, urlsplit
from datetime import datetime, timedelta
from typing import Any, Dict, Mapping, Optional

from pydantic import BaseModel, Field
import requests

import threading
import logging
import secrets
import json

from app.core.settings import Settings, get_settings, set_settings
from app.core.timeutil import time_now, time_to_business

LOGGER = logging.getLogger(__name__)


class BlingOAuthError(RuntimeError):
    """Erro de domínio para falhas na autenticação OAuth do Bling."""


class OAuthToken(BaseModel):
    """Representa o payload do token OAuth2 retornado pelo Bling."""

    access_token: str = Field(alias="access_token")
    expires_in: int = Field(alias="expires_in")
    token_type: str = Field(alias="token_type")
    scope: Optional[str] = Field(default=None, alias="scope")
    refresh_token: Optional[str] = Field(default=None, alias="refresh_token")
    obtained_at: datetime = Field(default_factory=time_now)

    model_config = {
        "populate_by_name": True,
    }

    @property
    def expires_at(self) -> datetime:
        """Retorna o momento exato em que o token expira."""
        expires_time = self.obtained_at + timedelta(seconds=self.expires_in)

        return time_to_business(expires_time)

    def is_expired(self, *, leeway: int = 60) -> bool:
        """Indica se o token já expirou considerando uma folga opcional."""

        return time_now() >= (self.expires_at - timedelta(seconds=leeway))


class BlingOAuthClient:
    """Cliente responsável por todo o fluxo OAuth com o Bling."""

    AUTHORIZE_ENDPOINT = "oauth/authorize"
    TOKEN_ENDPOINT = "oauth/token"

    ENV_ACCESS_TOKEN_KEY = "BLING_OAUTH_ACCESS_TOKEN"
    ENV_EXPIRES_IN_KEY = "BLING_OAUTH_EXPIRES_IN"
    ENV_EXPIRES_AT_KEY = "BLING_OAUTH_HOURS_EXPIRATION"
    ENV_REFRESH_TOKEN_KEY = "BLING_OAUTH_REFRESH_TOKEN"
    ENV_SCOPE_KEY = "BLING_OAUTH_SCOPE"

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
        self._env_path = env_path or None

        self._token_lock = threading.Lock()
        self._token: Optional[OAuthToken] = None
        self._refresh_token = self._settings.bling_oauth_refresh_token

    # ------------------------------------------------------------------
    # Fluxo público
    # ------------------------------------------------------------------
    def build_authorization_url(
        self,
        *,
        state: Optional[str] = None,
    ) -> str:
        """Monta a URL de autorização conforme a documentação oficial."""

        base_url = urljoin(str(self._settings.bling_baseurl), self.AUTHORIZE_ENDPOINT)
        params: Dict[str, Any] = {
            "response_type": "code",
            "client_id": self._settings.bling_client_id,
        }
        final_state = state or secrets.token_urlsafe(16)
        params["state"] = final_state

        query = urlencode(params)
        return f"{base_url}?{query}"

    def exchange_code_for_token(
        self,
        code: str,
        *,
        save_to_env: bool = True,
    ) -> OAuthToken:
        """Troca um authorization code por um access token."""
        # Monta estrutura da requisição
        payload: Dict[str, Any] = {
            "grant_type": "authorization_code",
            "code": code,
        }

        # Solicita o token
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
                    "Forçando renovação do token",
                    extra={"event": "bling.oauth.refresh"},
                )
                self._token = None
            if self._token is None or self._token.is_expired():
                self._logger.info(
                    "Obtendo novo token via refresh",
                    extra={"event": "bling.oauth.renew"},
                )
                self._token = self.refresh_access_token()
            return self._token

    def authorize_with_browser(
        self,
        *,
        state: Optional[str] = None,
        headless: bool = True,
        save_to_env: bool = True,
    ) -> OAuthToken:
        """Executa o fluxo interativo de autorização via Selenium."""

        try:
            from selenium.common.exceptions import NoSuchElementException
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium import webdriver
        except ImportError as exc:  # pragma: no cover - dependência opcional
            raise BlingOAuthError("Dependências do Selenium não instaladas") from exc

        # Inicia o navegador
        options = self._build_chrome_options(headless=headless)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(2)

        # Construi a url
        final_state = state or secrets.token_urlsafe(16)
        authorization_url = self.build_authorization_url(state=final_state)
        self._logger.info(
            "bling.oauth.browser.start",
            extra={
                "event": "bling.oauth.browser.start",
                "url": authorization_url,
                "state": final_state,
            },
        )

        # Acessa url
        driver.get(authorization_url)

        # campo_usuario
        driver.find_element(
            By.XPATH,"/html/body/div/div/div/form/div[2]/input"
            ).send_keys(self._settings.bling_usuario)

        # campo_senha
        driver.find_element(
            By.XPATH, "/html/body/div/div/div/form/div[3]/input"
            ).send_keys(self._settings.bling_senha_usuario)

        # botao_entrar
        driver.find_element(
            By.XPATH, "/html/body/div/div/div/form/div[6]/button"
            ).click()

        try:
            # botao_autorizar
            driver.find_element(
                By.XPATH, "/html/body/div/div/div/div/div[6]/form/button[2]"
                ).click()
        except NoSuchElementException:
            self._logger.info(
                "Sessão previamente autorizada reutilizada",
                extra={
                    "event": "bling.oauth.browser.reuse",
                },
            )
        finally:
            final_url = driver.current_url
            driver.quit()

        # Pega as pertes necessárias da url de resposta
        parsed = urlsplit(final_url)
        params = parse_qs(parsed.query)
        codes = params.get("code")
        if not codes:
            raise BlingOAuthError("Código de autorização não encontrado na URL de retorno")

        # Pega o token de acesso a partir do código de autorização.
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
        # Monta estrutura de requisição
        token_url = urljoin(str(self._settings.bling_baseurl), self.TOKEN_ENDPOINT)

        # Codifica credenciais em base64
        credentialbs4 = requests.auth.HTTPBasicAuth(
            self._settings.bling_client_id, self._settings.bling_client_secret)

        self._logger.info(
            "bling.oauth.token.request",
            extra={"event": "bling.oauth.token.request", "payload": dict(payload)},
        )
        try:
            # Solicita token de acesso
            response = self._session.post(
                token_url,
                data=payload,
                headers={"Accept": "application/json",},
                auth=credentialbs4,
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

        data.setdefault("obtained_at", time_now())
        # Valida estrutura do token
        token = OAuthToken.model_validate(data)
        return token

    def _persist_token(self, token: OAuthToken) -> None:
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

