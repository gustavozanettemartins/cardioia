"""
CardioIA Fase 4 — protótipo Flask para classificação simulada de imagens ECG.

Uso:
  python fase4/app/app.py
  Abrir http://127.0.0.1:5000
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename

FASE4_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = FASE4_DIR.parent
sys.path.insert(0, str(FASE4_DIR))

from src.inferencia import ECGClassifier  # noqa: E402

UPLOAD_DIR = FASE4_DIR / "app" / "uploads"
DEFAULT_MODEL = FASE4_DIR / "models" / "ecg_transfer_best.keras"
ALLOWED = {".png", ".jpg", ".jpeg"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

_classifier: ECGClassifier | None = None


def get_classifier() -> ECGClassifier:
    global _classifier
    if _classifier is None:
        model_path = os.environ.get("CARDIOIA_MODEL", str(DEFAULT_MODEL))
        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em {model_path}. "
                "Execute: python fase4/scripts/train_pipeline.py"
            )
        _classifier = ECGClassifier(model_path=model_path)
    return _classifier


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED


@app.route("/", methods=["GET", "POST"])
def index():
    erro = None
    resultado = None
    preview_url = None

    if request.method == "POST":
        file = request.files.get("imagem")
        if not file or file.filename == "":
            erro = "Selecione um arquivo de imagem."
        elif not allowed_file(file.filename):
            erro = "Formato não suportado. Use PNG ou JPG."
        else:
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            ext = Path(secure_filename(file.filename)).suffix.lower()
            saved = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
            file.save(saved)
            try:
                resultado = get_classifier().predict(saved)
                preview_url = url_for("uploaded_file", name=saved.name)
            except Exception as exc:  # noqa: BLE001 — feedback amigável na UI
                erro = f"Erro na inferência: {exc}"
            finally:
                if erro and saved.exists():
                    saved.unlink(missing_ok=True)

    return render_template(
        "index.html",
        erro=erro,
        resultado=resultado,
        preview_url=preview_url,
    )


@app.route("/uploads/<name>")
def uploaded_file(name: str):
    from flask import send_from_directory

    return send_from_directory(UPLOAD_DIR, name)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
