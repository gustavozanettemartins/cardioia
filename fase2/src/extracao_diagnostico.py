"""
Parte 1 — CardioIA Fase 2: leitura de frases sintomáticas, normalização e
correspondência por substring com o mapa sintoma–doença (CSV).

Múltiplas linhas do mapa podem disparar para a mesma frase; todas as
doenças associadas a sintomas detectados são listadas (sem prioridade
clínica — exercício didático).
"""

from __future__ import annotations

import csv
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

FASE2_ROOT = Path(__file__).resolve().parent.parent
DADOS_DIR = FASE2_ROOT / "dados"
ARQUIVO_FRASES = DADOS_DIR / "frases_sintomas_pacientes.txt"
ARQUIVO_MAPA = DADOS_DIR / "mapa_sintomas_doencas.csv"


def normalizar(texto: str) -> str:
    """Minúsculas e remoção de diacríticos para matching robusto."""
    texto = texto.lower().strip()
    nfkd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def limpar_chaves_csv(linha: dict) -> dict:
    return {k.strip().lstrip("\ufeff"): (v or "").strip() for k, v in linha.items()}


def carregar_mapa() -> list[dict]:
    if not ARQUIVO_MAPA.is_file():
        raise FileNotFoundError(f"Mapa não encontrado: {ARQUIVO_MAPA}")

    mapa: list[dict] = []
    with ARQUIVO_MAPA.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = limpar_chaves_csv(raw)
            s1 = row.get("Sintoma 1", "")
            s2 = row.get("Sintoma 2", "")
            doenca = row.get("Doença Associada", "")
            if not doenca:
                continue
            mapa.append(
                {
                    "sintoma_1": s1,
                    "sintoma_2": s2,
                    "s1_n": normalizar(s1) if s1 else "",
                    "s2_n": normalizar(s2) if s2 else "",
                    "doenca": doenca,
                }
            )
    return mapa


def correspondencias(frase_norm: str, mapa: list[dict]) -> list[dict]:
    achados: list[dict] = []
    for m in mapa:
        hit1 = bool(m["s1_n"]) and m["s1_n"] in frase_norm
        hit2 = bool(m["s2_n"]) and m["s2_n"] in frase_norm
        if not (hit1 or hit2):
            continue
        sintomas_detectados: list[str] = []
        if hit1:
            sintomas_detectados.append(m["sintoma_1"])
        if hit2:
            sintomas_detectados.append(m["sintoma_2"])
        achados.append(
            {
                "sintomas": sintomas_detectados,
                "doenca": m["doenca"],
            }
        )
    return achados


def agregar_por_doenca(achados: list[dict]) -> dict[str, set[str]]:
    por_doenca: dict[str, set[str]] = defaultdict(set)
    for a in achados:
        for s in a["sintomas"]:
            por_doenca[a["doenca"]].add(s)
    return dict(por_doenca)


def main() -> int:
    if not ARQUIVO_FRASES.is_file():
        print(f"Arquivo de frases não encontrado: {ARQUIVO_FRASES}", file=sys.stderr)
        return 1

    mapa = carregar_mapa()
    linhas = ARQUIVO_FRASES.read_text(encoding="utf-8").splitlines()

    n = 0
    for line in linhas:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n += 1
        frase_norm = normalizar(line)
        achados = correspondencias(frase_norm, mapa)

        print(f"\n--- Frase {n} ---")
        print(line)

        if not achados:
            print("  (Nenhuma expressão do mapa encontrada como substring na frase.)")
            continue

        agg = agregar_por_doenca(achados)
        vistos: set[str] = set()
        sintomas_ord: list[str] = []
        for a in achados:
            for s in a["sintomas"]:
                ch = normalizar(s)
                if ch not in vistos:
                    vistos.add(ch)
                    sintomas_ord.append(s)

        print("  Sintomas detectados (trechos do mapa):")
        for s in sintomas_ord:
            print(f"    - {s}")
        print("  Doenças sugeridas pelo mapa:")
        for doenca, sints in sorted(agg.items()):
            print(f"    - {doenca}  [via: {', '.join(sorted(sints))}]")

    print(f"\nTotal de frases processadas: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
