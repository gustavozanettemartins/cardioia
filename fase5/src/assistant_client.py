"""
CardioIA Fase 5 — fábrica de assistente (mock ou Watson).

Variável de ambiente CARDIOIA_ASSISTANT: "mock" (padrão) ou "watson".
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from dotenv import load_dotenv

FASE5_DIR = Path(__file__).resolve().parents[1]
load_dotenv(FASE5_DIR / ".env")


class AssistantProtocol(Protocol):
    def send_message(self, message: str, session_id: str | None = None): ...


_assistant: AssistantProtocol | None = None


def get_assistant() -> AssistantProtocol:
    global _assistant
    if _assistant is not None:
        return _assistant

    provider = os.environ.get("CARDIOIA_ASSISTANT", "mock").lower().strip()

    if provider == "watson":
        from watson_assistant import WatsonAssistant

        _assistant = WatsonAssistant()
    else:
        from mock_assistant import MockAssistant

        _assistant = MockAssistant()

    return _assistant
