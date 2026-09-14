"""
CardioIA Fase 5 — protótipo Flask do assistente conversacional.

Uso:
  python fase5/app/app.py
  Abrir http://127.0.0.1:5001
"""

from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

FASE5_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FASE5_DIR / "src"))

from assistant_client import get_assistant  # noqa: E402

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("chat.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    session_id = data.get("session_id")

    if not message:
        return jsonify({"error": "Campo 'message' é obrigatório."}), 400

    try:
        assistant = get_assistant()
        response = assistant.send_message(message, session_id=session_id)
        return jsonify(
            {
                "reply": response.reply,
                "session_id": response.session_id,
                "meta": response.meta,
            }
        )
    except Exception as exc:  # noqa: BLE001 — feedback amigável na API
        return jsonify({"error": f"Erro no assistente: {exc}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
