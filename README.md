# CardioIA

Projeto acadêmico de IA aplicada à saúde cardiovascular, organizado em fases.

| Pasta | Conteúdo |
|--------|-----------|
| [fase1/](fase1/README.md) | Dataset sintético tabular, textos de referência para NLP, imagens de ECG (Kaggle) — coleta e documentação de dados (Fase 1) |
| [fase2/](fase2/README.md) | NLP: mapa sintoma–doença, extração por regras (substring), triagem de risco com TF-IDF + scikit-learn (Fase 2) |

**Autor:** Gustavo Zanette Martins  
**RM:** 564523

---

## Ambiente (raiz do projeto)

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Fase 1 (dataset): na pasta `fase1`, execute `python main.py` (gera `dataset_cardiovascular.csv` nessa pasta).
- Fase 2 (extração): `python fase2/src/extracao_diagnostico.py`.
- Fase 2 (notebook): abrir `fase2/notebooks/classificador_risco_tfidf.ipynb`.

Cada pasta tem seu próprio README com instruções detalhadas.

---

## Fase 2 — vídeo no YouTube (não listado)

**Link do vídeo (Fase 2):** `https://youtu.be/JEI_BCRCK6U`

Instruções detalhadas: [fase2/README.md](fase2/README.md).

---

## Repositório

[github.com/gustavozanettemartins/cardioia](https://github.com/gustavozanettemartins/cardioia)
