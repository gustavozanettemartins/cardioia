"""Utilitários de normalização de texto (compatível com Fase 2)."""

from __future__ import annotations

import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas e remoção de diacríticos para matching robusto."""
    texto = texto.lower().strip()
    nfkd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
