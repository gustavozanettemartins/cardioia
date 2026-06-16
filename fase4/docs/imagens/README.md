# Evidências visuais — Fase 4

Geradas por `python fase4/scripts/train_pipeline.py` (WSL2 + GPU) e captura manual do Flask.

| Arquivo | Descrição |
|---------|-----------|
| `matriz_confusao_cnn_simples.png` | Matriz de confusão — CNN simples |
| `matriz_confusao_transfer_learning.png` | Matriz de confusão — VGG16 |
| `historico_cnn_simples.png` | Curvas acurácia/loss — CNN |
| `historico_transfer_learning.png` | Curvas acurácia/loss — VGG16 |
| `metricas_comparacao.png` | Comparação acurácia, precision, recall, F1 |
| `flask-demo.png` | Protótipo Flask (upload + classificação) |
| `metricas_resumo.json` | Métricas numéricas do último treino |

**Regenerar (WSL):**

```bash
source ~/cardioia-venv/bin/activate
cd /mnt/d/Projetos/FIAP/cardioia
python fase4/scripts/train_pipeline.py
```

**Nota:** arquivos `.keras` em `fase4/models/` não são versionados (gitignore). Quem clonar o repo precisa treinar ou receber os pesos separadamente.
