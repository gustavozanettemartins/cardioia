"""
CardioIA Fase 5 — motor de diálogo local (mock do Watson Assistant).

Simula intents, entities e fluxo de triagem cardiológica com sessões em memória.
Reutiliza o mapa sintoma–doença da Fase 2 quando sintomas são detectados.
"""

from __future__ import annotations

import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FASE5_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = FASE5_DIR.parent
FASE2_SRC = REPO_ROOT / "fase2" / "src"
if str(FASE2_SRC) not in sys.path:
    sys.path.insert(0, str(FASE2_SRC))

from extracao_diagnostico import agregar_por_doenca, carregar_mapa, correspondencias  # noqa: E402

from text_utils import normalizar  # noqa: E402

# --- Intents (keywords normalizadas) ---

INTENT_KEYWORDS: dict[str, list[str]] = {
    "emergencia": [
        "nao consigo respirar",
        "falta de ar grave",
        "dor forte no peito",
        "dor intensa no peito",
        "desmaiei",
        "desmaio",
        "perdi a consciencia",
        "samu",
        "192",
        "emergencia",
        "socorro",
        "infarto agudo",
        "dor no peito irradiando",
        "braço esquerdo",
        "braco esquerdo",
    ],
    "saudacao": [
        "ola",
        "oi",
        "bom dia",
        "boa tarde",
        "boa noite",
        "e ai",
        "preciso de ajuda",
        "pode me ajudar",
        "começar",
        "comecar",
    ],
    "despedida": [
        "tchau",
        "ate logo",
        "ate mais",
        "obrigado",
        "obrigada",
        "valeu",
        "encerrar",
        "sair",
    ],
    "agendar_consulta": [
        "marcar consulta",
        "agendar consulta",
        "agendar",
        "marcar",
        "consulta cardiologista",
        "quero consulta",
    ],
    "informacao_geral": [
        "o que e",
        "o que é",
        "como funciona",
        "sintomas de",
        "o que significa",
        "me explique",
        "informacao sobre",
        "informação sobre",
    ],
    "relatar_sintomas": [
        "sinto",
        "tenho",
        "apresento",
        "dor no peito",
        "falta de ar",
        "palpitacao",
        "palpitação",
        "cansaco",
        "cansaço",
        "tontura",
        "inchaco",
        "inchaço",
        "dispneia",
        "aperto no torax",
        "aperto no tórax",
        "fadiga",
        "pressao alta",
        "pressão alta",
    ],
}

SINTOMA_KEYWORDS: list[tuple[str, str]] = [
    ("dor no peito", "dor no peito"),
    ("falta de ar", "falta de ar"),
    ("palpitacao", "palpitações"),
    ("palpitação", "palpitações"),
    ("cansaco", "cansaço"),
    ("cansaço", "cansaço"),
    ("tontura", "tontura"),
    ("inchaco", "inchaço nos tornozelos"),
    ("inchaço", "inchaço nos tornozelos"),
    ("dispneia", "dispneia"),
    ("aperto no torax", "aperto no tórax"),
    ("aperto no tórax", "aperto no tórax"),
    ("fadiga", "fadiga"),
    ("visao turva", "visão turva"),
    ("visão turva", "visão turva"),
    ("dor latejante", "dor latejante na nuca"),
    ("tosse seca", "tosse seca"),
    ("nausea", "náusea"),
    ("náusea", "náusea"),
]

INTENSIDADE_KEYWORDS: dict[str, list[str]] = {
    "forte": ["forte", "intensa", "grave", "insuportavel", "insuportável", "piora muito"],
    "moderada": ["moderada", "media", "média", "regular"],
    "leve": ["leve", "suave", "fraca", "pouco"],
}

DURACAO_PATTERN = re.compile(
    r"(\d+)\s*(hora|horas|dia|dias|semana|semanas|mes|meses|minuto|minutos)",
    re.IGNORECASE,
)

INFO_RESPOSTAS: dict[str, str] = {
    "arritmia": (
        "Arritmia é uma alteração no ritmo dos batimentos cardíacos — podem ficar "
        "rápidos, lentos ou irregulares. Sintomas comuns incluem palpitações, "
        "tontura e fadiga. Este assistente não diagnostica; procure um cardiologista "
        "para avaliação."
    ),
    "infarto": (
        "O infarto do miocárdio ocorre quando há obstrução do fluxo sanguíneo no "
        "coração. Sinais de alerta incluem dor no peito persistente, falta de ar, "
        "náusea e dor irradiando para braço ou mandíbula. Em emergência, ligue 192 (SAMU)."
    ),
    "hipertensao": (
        "A hipertensão arterial é a pressão elevada de forma crônica. Muitas vezes é "
        "assintomática; quando há sintomas, podem incluir dor de cabeça e tontura. "
        "O acompanhamento médico regular é essencial."
    ),
    "default": (
        "Posso ajudar com triagem inicial de sintomas cardiovasculares, orientações "
        "gerais e encaminhamento para consulta. Descreva como você está se sentindo "
        "ou pergunte sobre um tema específico (ex.: arritmia, infarto, hipertensão)."
    ),
}


@dataclass
class SessionState:
    etapa: str = "inicio"
    sintomas: list[str] = field(default_factory=list)
    intensidade: str | None = None
    duracao: str | None = None
    falhas: int = 0
    risco: str | None = None


@dataclass
class AssistantResponse:
    reply: str
    session_id: str
    meta: dict[str, Any] = field(default_factory=dict)


class MockAssistant:
    """Assistente conversacional local que espelha o contrato da API Watson."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._mapa = carregar_mapa()

    def _get_session(self, session_id: str | None) -> tuple[str, SessionState]:
        if not session_id or session_id not in self._sessions:
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = SessionState()
        return session_id, self._sessions[session_id]

    def _detect_intent(self, texto_norm: str) -> str:
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(kw in texto_norm for kw in keywords):
                return intent
        return "anything_else"

    def _extract_sintomas(self, texto_norm: str) -> list[str]:
        found: list[str] = []
        for kw, label in SINTOMA_KEYWORDS:
            if kw in texto_norm and label not in found:
                found.append(label)
        achados = correspondencias(texto_norm, self._mapa)
        for a in achados:
            for s in a["sintomas"]:
                if s not in found:
                    found.append(s)
        return found

    def _extract_intensidade(self, texto_norm: str) -> str | None:
        for nivel, keywords in INTENSIDADE_KEYWORDS.items():
            if any(kw in texto_norm for kw in keywords):
                return nivel
        return None

    def _extract_duracao(self, texto: str) -> str | None:
        match = DURACAO_PATTERN.search(texto)
        if match:
            return f"{match.group(1)} {match.group(2).lower()}"
        return None

    def _avaliar_risco(self, sintomas: list[str], intensidade: str | None) -> str:
        texto_sintomas = " ".join(normalizar(s) for s in sintomas)
        emergencia_sintomas = [
            "dor no peito",
            "falta de ar",
            "dispneia",
            "palpitacao",
            "palpitações",
        ]
        tem_critico = any(
            normalizar(s) in texto_sintomas or any(e in normalizar(s) for e in emergencia_sintomas)
            for s in sintomas
        )
        if intensidade == "forte" or (tem_critico and intensidade != "leve"):
            return "alto"
        if sintomas:
            return "moderado"
        return "baixo"

    def _resposta_emergencia(self) -> str:
        return (
            "⚠️ Pelos sintomas relatados, recomendo buscar atendimento de emergência "
            "**imediatamente**. Ligue para o SAMU: **192** ou dirija-se ao pronto-socorro "
            "mais próximo.\n\n"
            "Este assistente é um protótipo acadêmico e **não substitui** avaliação médica."
        )

    def _resposta_info(self, texto_norm: str) -> str:
        for tema, resposta in INFO_RESPOSTAS.items():
            if tema != "default" and tema in texto_norm:
                return resposta
        return INFO_RESPOSTAS["default"]

    def _formatar_recomendacao(
        self, risco: str, sintomas: list[str], doencas: dict[str, set[str]]
    ) -> str:
        linhas = ["## Resumo da triagem inicial\n"]
        if sintomas:
            linhas.append("**Sintomas relatados:** " + ", ".join(sintomas))
        linhas.append(f"**Nível de atenção sugerido:** {risco.upper()}")

        if doencas:
            linhas.append("\n**Possíveis condições associadas (referência didática):**")
            for doenca, sints in sorted(doencas.items()):
                linhas.append(f"- {doenca} _(via: {', '.join(sorted(sints))})_")

        if risco == "alto":
            linhas.append(
                "\n⚠️ Recomendo procurar atendimento médico **urgente** ou ligar **192 (SAMU)**."
            )
        elif risco == "moderado":
            linhas.append(
                "\n📋 Sugiro agendar consulta com cardiologista nos próximos dias. "
                "Se os sintomas piorarem, procure emergência."
            )
        else:
            linhas.append(
                "\n✅ Mantenha observação dos sintomas. Se persistirem ou piorarem, "
                "consulte um profissional de saúde."
            )

        linhas.append(
            "\n_Lembrete: protótipo acadêmico — não constitui diagnóstico médico._"
        )
        return "\n".join(linhas)

    def send_message(
        self, message: str, session_id: str | None = None
    ) -> AssistantResponse:
        session_id, state = self._get_session(session_id)
        texto = message.strip()
        texto_norm = normalizar(texto)

        if not texto:
            return AssistantResponse(
                reply="Por favor, digite uma mensagem para que eu possa ajudar.",
                session_id=session_id,
                meta={"intent": "anything_else", "etapa": state.etapa},
            )

        intent = self._detect_intent(texto_norm)

        # Emergência tem prioridade absoluta
        if intent == "emergencia":
            state.etapa = "recomendacao"
            state.risco = "alto"
            return AssistantResponse(
                reply=self._resposta_emergencia(),
                session_id=session_id,
                meta={"intent": "emergencia", "risco": "alto", "etapa": state.etapa},
            )

        if intent == "despedida":
            state.etapa = "inicio"
            return AssistantResponse(
                reply=(
                    "Foi um prazer ajudar. Cuide da sua saúde cardiovascular! "
                    "Se precisar, estou por aqui. Até logo! 💙"
                ),
                session_id=session_id,
                meta={"intent": "despedida", "etapa": "inicio"},
            )

        if intent == "agendar_consulta":
            return AssistantResponse(
                reply=(
                    "Para agendar uma consulta cardiológica, você pode:\n"
                    "1. Entrar em contato com seu plano de saúde ou UBS\n"
                    "2. Buscar ambulatório de cardiologia em hospital da sua região\n"
                    "3. Usar aplicativos de telemedicina credenciados\n\n"
                    "Deseja relatar algum sintoma antes de agendar?"
                ),
                session_id=session_id,
                meta={"intent": "agendar_consulta", "etapa": state.etapa},
            )

        if intent == "informacao_geral":
            return AssistantResponse(
                reply=self._resposta_info(texto_norm),
                session_id=session_id,
                meta={"intent": "informacao_geral", "etapa": state.etapa},
            )

        if intent == "saudacao" and state.etapa == "inicio":
            state.etapa = "coletando_sintomas"
            return AssistantResponse(
                reply=(
                    "Olá! Sou o assistente cardiológico do **CardioIA** (protótipo acadêmico).\n\n"
                    "Posso ajudar com:\n"
                    "- Triagem inicial de sintomas cardiovasculares\n"
                    "- Informações gerais sobre condições cardíacas\n"
                    "- Orientação para agendamento de consulta\n\n"
                    "Como você está se sentindo hoje? Descreva seus sintomas com calma."
                ),
                session_id=session_id,
                meta={"intent": "saudacao", "etapa": state.etapa},
            )

        # Fluxo de sintomas
        novos_sintomas = self._extract_sintomas(texto_norm)
        if novos_sintomas:
            for s in novos_sintomas:
                if s not in state.sintomas:
                    state.sintomas.append(s)

        intensidade = self._extract_intensidade(texto_norm)
        if intensidade:
            state.intensidade = intensidade

        duracao = self._extract_duracao(texto)
        if duracao:
            state.duracao = duracao

        if intent == "relatar_sintomas" or state.sintomas:
            if state.etapa in ("inicio", "coletando_sintomas"):
                state.etapa = "coletando_sintomas"
                if not state.intensidade:
                    return AssistantResponse(
                        reply=(
                            f"Entendi. Registrei: **{', '.join(state.sintomas)}**.\n\n"
                            "Qual a **intensidade** dos sintomas? (leve, moderada ou forte)\n"
                            "E há quanto tempo você os sente?"
                        ),
                        session_id=session_id,
                        meta={
                            "intent": "relatar_sintomas",
                            "etapa": state.etapa,
                            "sintomas_detectados": state.sintomas,
                        },
                    )

            if state.etapa == "coletando_sintomas" and state.sintomas:
                state.etapa = "avaliando_risco"
                state.risco = self._avaliar_risco(state.sintomas, state.intensidade)
                achados = correspondencias(texto_norm, self._mapa)
                for s in state.sintomas:
                    achados.extend(correspondencias(normalizar(s), self._mapa))
                doencas = agregar_por_doenca(achados)
                state.etapa = "recomendacao"
                return AssistantResponse(
                    reply=self._formatar_recomendacao(state.risco, state.sintomas, doencas),
                    session_id=session_id,
                    meta={
                        "intent": "relatar_sintomas",
                        "etapa": state.etapa,
                        "risco": state.risco,
                        "sintomas_detectados": state.sintomas,
                        "intensidade": state.intensidade,
                        "duracao": state.duracao,
                    },
                )

        # Fallback
        state.falhas += 1
        if state.falhas >= 2:
            return AssistantResponse(
                reply=(
                    "Não consegui entender bem. Você pode:\n"
                    "- Descrever seus **sintomas** (ex.: dor no peito, falta de ar)\n"
                    "- Perguntar sobre **arritmia**, **infarto** ou **hipertensão**\n"
                    "- Pedir para **agendar consulta**\n"
                    "- Dizer **tchau** para encerrar"
                ),
                session_id=session_id,
                meta={"intent": "anything_else", "etapa": state.etapa, "falhas": state.falhas},
            )

        return AssistantResponse(
            reply=(
                "Desculpe, não entendi completamente. Pode reformular?\n\n"
                "Exemplos: \"sinto dor no peito ao esforço\" ou "
                "\"o que é arritmia?\""
            ),
            session_id=session_id,
            meta={"intent": "anything_else", "etapa": state.etapa, "falhas": state.falhas},
        )
