# Relatório — Parte 1: pré-processamento e organização das imagens ECG

**Projeto:** CardioIA — Fase 4  
**Autor:** Gustavo Zanette Martins (RM 564523)

## Dataset selecionado

Utilizamos o dataset **ECG Images** ([Kaggle — analiviafr](https://www.kaggle.com/datasets/analiviafr/ecg-images)). As imagens representam traçados de ECG organizados por tipo de batimento:

| Pasta | Significado |
|-------|-------------|
| **N** | Batimento normal |
| **S** | Ectópico supraventricular |
| **V** | Ectópico ventricular |
| **F** | Batimento de fusão |
| **Q** | Desconhecido / estimulado |

Para desenvolvimento local, o dataset foi baixado manualmente do Kaggle para **`dataset/ecg_img/`** na raiz do repositório (54.613 imagens, classes `F`, `N`, `Q`, `S`, `V`).

## Pipeline de preparação

1. **Descoberta:** varredura de `dataset/ecg_img/train/` e `test/` (classes `F`, `N`, `Q`, `S`, `V`).
2. **Conversão de formato:** todas as imagens são abertas com Pillow e convertidas para **RGB** (3 canais), garantindo compatibilidade com CNNs pré-treinadas em ImageNet.
3. **Redimensionamento:** `224×224` pixels com interpolação **LANCZOS**, tamanho padrão para VGG16/ResNet50.
4. **Normalização:** divisão dos pixels por 255, resultando em valores no intervalo **[0, 1]** (float32).
5. **Divisão:** uso das pastas `train/` e `test/` do Kaggle; validação interna = **15%** do treino (`validation_split=0.15`).

## Justificativas

| Escolha | Motivo |
|---------|--------|
| RGB em vez de escala de cinza | Permite reutilizar pesos ImageNet no transfer learning sem adaptar canais. |
| 224×224 | Compatível com arquiteturas VGG16/ResNet e reduz custo computacional em ambiente acadêmico. |
| Split estratificado | Evita conjuntos de teste sem representantes de classes minoritárias. |
| Seed fixa | Reprodutibilidade entre notebook, script e Flask. |

## Artefatos gerados

- Código reutilizável: [`fase4/src/preprocessamento.py`](../src/preprocessamento.py)  
- Notebook: [`fase4/notebooks/01_preprocessamento_ecg.ipynb`](../notebooks/01_preprocessamento_ecg.ipynb)  
- Metadados dos splits: `fase4/data/processed/splits.json` (não versionado)

## Limitações

- Imagens reais de ECG exigem mais épocas e balanceamento; a classe `F` é minoritária (~800 amostras no total).  
- O dataset Kaggle completo é desbalanceado; em produção acadêmica recomenda-se `class_weight` ou amostragem balanceada.  
- Este protótipo **não substitui** laudo médico — uso exclusivamente didático e de pesquisa.
