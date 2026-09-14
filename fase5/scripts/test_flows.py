"""Testes rápidos do mock assistant — Fase 5."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mock_assistant import MockAssistant  # noqa: E402


def main() -> None:
    assistant = MockAssistant()
    session_id = None

    scenarios = [
        ("saudacao", "ola"),
        ("sintomas", "sinto dor no peito ao subir escadas"),
        ("intensidade", "moderada, ha 3 dias"),
        ("emergencia", "nao consigo respirar"),
        ("fallback", "xyz abc nonsense"),
        ("despedida", "tchau"),
    ]

    for name, msg in scenarios:
        r = assistant.send_message(msg, session_id)
        session_id = r.session_id
        print(f"[{name}] intent={r.meta.get('intent')} etapa={r.meta.get('etapa')}")
        preview = r.reply[:100].encode("ascii", errors="replace").decode("ascii")
        print(f"  reply: {preview}...")
        print()

    print("Todos os cenários executados.")


if __name__ == "__main__":
    main()
