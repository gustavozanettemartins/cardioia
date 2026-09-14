"""
CardioIA Fase 5 — integração com IBM Watson Assistant.

Suporta API v2 (assistant) e v1 (workspace/dialog skill classic).

Variáveis .env:
  WATSON_API_KEY, WATSON_URL
  v2: WATSON_ASSISTANT_ID (+ WATSON_ENVIRONMENT_ID opcional)
  v1: WATSON_API_VERSION=v1, WATSON_WORKSPACE_ID (Skill ID)
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from typing import Any

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV1, AssistantV2


@dataclass
class AssistantResponse:
    reply: str
    session_id: str
    meta: dict[str, Any] = field(default_factory=dict)


class WatsonAssistant:
    """Cliente IBM Watson Assistant (v1 workspace ou v2 assistant)."""

    def __init__(
        self,
        api_key: str | None = None,
        assistant_id: str | None = None,
        environment_id: str | None = None,
        workspace_id: str | None = None,
        url: str | None = None,
        api_version: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("WATSON_API_KEY", "")
        self.assistant_id = assistant_id or os.environ.get("WATSON_ASSISTANT_ID", "")
        self.environment_id = environment_id or os.environ.get(
            "WATSON_ENVIRONMENT_ID", ""
        )
        self.workspace_id = (
            workspace_id
            or os.environ.get("WATSON_WORKSPACE_ID", "")
            or self.assistant_id
        )
        self.url = url or os.environ.get(
            "WATSON_URL", "https://api.us-south.assistant.watson.cloud.ibm.com"
        )
        self.api_version = (
            api_version or os.environ.get("WATSON_API_VERSION", "")
        ).lower().strip()

        if not self.api_version:
            self.api_version = "v1" if os.environ.get("WATSON_WORKSPACE_ID") else "v2"

        if not self.api_key:
            raise ValueError(
                "WATSON_API_KEY é obrigatório no modo watson. "
                "Configure o arquivo .env ou use CARDIOIA_ASSISTANT=mock."
            )

        authenticator = IAMAuthenticator(self.api_key)

        if self.api_version == "v1":
            if not self.workspace_id:
                raise ValueError(
                    "WATSON_WORKSPACE_ID (Skill ID) é obrigatório com WATSON_API_VERSION=v1."
                )
            self._client_v1 = AssistantV1(
                version="2018-09-20", authenticator=authenticator
            )
            self._client_v1.set_service_url(self.url)
            self._contexts: dict[str, dict[str, Any]] = {}
        else:
            if not self.assistant_id:
                raise ValueError(
                    "WATSON_ASSISTANT_ID é obrigatório com WATSON_API_VERSION=v2."
                )
            self._client = AssistantV2(version="2021-11-27", authenticator=authenticator)
            self._client.set_service_url(self.url)
            self.environment_id = self._resolve_environment_id()
            # Mapeia session_id do frontend → session_id real do Watson
            self._session_map: dict[str, str] = {}

    def _resolve_environment_id(self) -> str:
        if self.environment_id:
            return self.environment_id
        try:
            result = self._client.list_environments(
                assistant_id=self.assistant_id
            ).get_result()
            environments = result.get("environments", [])
            for env in environments:
                if env.get("environment") == "draft":
                    return env["environment_id"]
            if environments:
                return environments[0]["environment_id"]
        except Exception:
            pass
        return self.assistant_id

    def _extract_reply_v1(self, response: dict[str, Any]) -> str:
        output = response.get("output", {})
        generic = output.get("generic", [])
        if generic:
            texts = [item["text"] for item in generic if item.get("text")]
            if texts:
                return "\n".join(texts)
        texts = output.get("text", [])
        if texts:
            return "\n".join(texts)
        return "Não obtive resposta do assistente."

    def _send_message_v1(
        self, message: str, session_id: str | None
    ) -> AssistantResponse:
        if not session_id:
            session_id = str(uuid.uuid4())

        kwargs: dict[str, Any] = {
            "workspace_id": self.workspace_id,
            "input": {"text": message},
            "user_id": session_id,
        }
        if session_id in self._contexts:
            kwargs["context"] = self._contexts[session_id]

        response = self._client_v1.message(**kwargs).get_result()
        self._contexts[session_id] = response.get("context", {})

        intents = response.get("intents", [])
        intent_name = intents[0]["intent"] if intents else "unknown"
        confidence = intents[0].get("confidence", 0) if intents else 0
        entities = [
            {"entity": e["entity"], "value": e.get("value", "")}
            for e in response.get("entities", [])
        ]

        return AssistantResponse(
            reply=self._extract_reply_v1(response),
            session_id=session_id,
            meta={
                "intent": intent_name,
                "confidence": confidence,
                "entities": entities,
                "provider": "watson-v1",
            },
        )

    def _create_watson_session(self, user_id: str) -> str:
        session = self._client.create_session(
            assistant_id=self.assistant_id,
            environment_id=self.environment_id,
        ).get_result()
        return session["session_id"]

    def _call_v2_message(
        self, watson_session_id: str, message: str, user_id: str
    ) -> dict[str, Any]:
        return self._client.message(
            assistant_id=self.assistant_id,
            environment_id=self.environment_id,
            session_id=watson_session_id,
            input={"message_type": "text", "text": message},
            user_id=user_id,
        ).get_result()

    def _get_v2_sessions(
        self, client_session_id: str | None
    ) -> tuple[str, str]:
        """Retorna (client_session_id, watson_session_id)."""
        if not client_session_id:
            client_session_id = str(uuid.uuid4())

        if client_session_id not in self._session_map:
            self._session_map[client_session_id] = self._create_watson_session(
                client_session_id
            )

        return client_session_id, self._session_map[client_session_id]

    def _send_message_v2(
        self, message: str, session_id: str | None
    ) -> AssistantResponse:
        client_session_id, watson_session_id = self._get_v2_sessions(session_id)

        try:
            response = self._call_v2_message(
                watson_session_id, message, client_session_id
            )
        except Exception as exc:
            # Sessão expirou ou ID inválido — cria nova e tenta de novo
            if "session" not in str(exc).lower():
                raise
            self._session_map[client_session_id] = self._create_watson_session(
                client_session_id
            )
            watson_session_id = self._session_map[client_session_id]
            response = self._call_v2_message(
                watson_session_id, message, client_session_id
            )

        output = response.get("output", {})
        generic = output.get("generic", [])
        texts = [item["text"] for item in generic if item.get("text")]
        reply = "\n".join(texts) if texts else "Não obtive resposta do assistente."

        intents = output.get("intents", [])
        intent_name = intents[0]["intent"] if intents else "unknown"
        confidence = intents[0].get("confidence", 0) if intents else 0
        entities = [
            {"entity": e["entity"], "value": e.get("value", "")}
            for e in output.get("entities", [])
        ]

        return AssistantResponse(
            reply=reply,
            session_id=client_session_id,
            meta={
                "intent": intent_name,
                "confidence": confidence,
                "entities": entities,
                "provider": "watson-v2",
            },
        )

    def send_message(
        self, message: str, session_id: str | None = None
    ) -> AssistantResponse:
        if self.api_version == "v1":
            return self._send_message_v1(message, session_id)
        return self._send_message_v2(message, session_id)
