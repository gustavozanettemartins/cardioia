# Relatório — Parte 2: classificação CNN, métricas e protótipo Flask

**Projeto:** CardioIA — Fase 4  
**Autor:** Gustavo Zanette Martins (RM 564523)

## Objetivo

Implementar e comparar duas abordagens de visão computacional para classificar imagens de ECG pré-processadas, avaliar com métricas de classificação e expor o resultado em um protótipo web simples (Flask).

## Arquiteturas

### CNN simples (treinada do zero)

- Três blocos Conv2D (32 → 64 → 128 filtros) + MaxPooling.  
- Camada densa 128 unidades, Dropout 0.4, saída softmax (5 classes).  
- Otimizador Adam (`lr=1e-3`), loss `sparse_categorical_crossentropy`.  
- Early stopping (`patience=3`) e checkpoint no melhor `val_accuracy`.

### Transfer Learning (VGG16)

- Base VGG16 ImageNet (`include_top=False`, `pooling=avg`), inicialmente congelada.  
- Head: Dense 256 + Dropout 0.5 + softmax.  
- Adam `lr=1e-4`, mesmos callbacks de parada e checkpoint.

## Ambiente de treino

- **Dataset:** ECG Images (Kaggle) em `dataset/ecg_img/` — 54.613 imagens (37.178 treino + 17.435 teste).  
- **Classes:** `F`, `N`, `Q`, `S`, `V` (batimentos por tipo de arritmia).  
- **Split:** pastas `train/` e `test/` do Kaggle; validação = 15% do treino (`validation_split=0.15`).  
- **Hardware:** NVIDIA GeForce RTX 4090, treino via **WSL2 (Ubuntu 24.04)** + TensorFlow 2.21 com CUDA.  
- **Épocas:** 3 para CNN simples e 3 para VGG16 (`class_weight` para desbalanceamento).  
- **Batch size:** 32 · **Entrada:** 224×224 RGB, pixels normalizados em [0, 1].

## Resultados no conjunto de teste (17.435 imagens)

| Modelo | Acurácia | Precisão (macro) | Recall (macro) | F1 (macro) |
|--------|----------|------------------|----------------|------------|
| CNN simples | 0,032 | 0,006 | 0,200 | 0,012 |
| Transfer Learning (VGG16) | **0,803** | **0,681** | **0,836** | **0,689** |

### Métricas por classe — VGG16 (modelo escolhido para o Flask)

| Classe | Significado | Precision | Recall | F1 | Suporte (teste) |
|--------|-------------|-----------|--------|-----|-----------------|
| F | Batimento de fusão | 0,06 | 0,81 | 0,12 | 161 |
| N | Batimento normal | 0,97 | 0,79 | 0,87 | 13.661 |
| Q | Desconhecido / estimulado | 0,64 | 0,86 | 0,73 | 1.608 |
| S | Ectópico supraventricular | 0,97 | 0,94 | 0,95 | 557 |
| V | Ectópico ventricular | 0,77 | 0,77 | 0,77 | 1.448 |

**Interpretação:** com dados reais e forte desbalanceamento (classe `N` ≈ 78% do teste), a **CNN simples** não convergiu em 3 épocas — tendeu a prever predominantemente a classe `S`. O **VGG16** com pesos ImageNet atingiu **~80% de acurácia** e bons F1 em `N`, `S`, `Q` e `V`. A classe **F** permanece difícil (poucos exemplos e precision baixa), o que deve ser discutido como limitação do protótipo.

Evidências visuais em [`docs/imagens/`](imagens/): matrizes de confusão, curvas de treino (`historico_*.png`) e gráfico comparativo (`metricas_comparacao.png`). Resumo numérico em `metricas_resumo.json`.

## Protótipo Flask

Aplicação em [`fase4/app/app.py`](../app/app.py):

1. Upload de PNG/JPG.  
2. Pré-processamento idêntico ao treino (`load_image` em `preprocessamento.py`).  
3. Inferência com modelo VGG16 salvo (`models/ecg_transfer_best.keras`).  
4. Exibição da classe prevista (rótulo legível), confiança e barras de probabilidade.  
5. Disclaimer de uso acadêmico visível na página.

**Onde executar:** preferir o **terminal WSL (Ubuntu)**, no mesmo ambiente em que o modelo foi treinado:

```bash
source ~/cardioia-venv/bin/activate
cd /mnt/d/Projetos/FIAP/cardioia
python fase4/app/app.py
```

Abrir no navegador (Windows ou WSL): `http://127.0.0.1:5000`.

Também funciona no PowerShell do Windows se o `venv` local tiver TensorFlow instalado, mas o ambiente **WSL é o recomendado** (mesmo venv, GPU configurada, modelos já salvos).

Variável opcional `CARDIOIA_MODEL` aponta para outro arquivo `.keras` (ex.: CNN simples — não recomendado para demo).

## Governança e responsabilidade

- Dados de saúde exigem consentimento, anonimização e validação clínica em cenários reais — aqui usamos o dataset público **ECG Images (Kaggle)**.  
- O protótipo é **ferramenta de apoio simulado**, não dispositivo médico.  
- Decisões clínicas permanecem com profissionais habilitados.

## Conclusão

A Fase 4 demonstra tecnicamente o pipeline completo: pré-processamento → treino CNN → métricas → interface interpretável. No dataset real (54 mil imagens), o **transfer learning (VGG16)** superou claramente a CNN treinada do zero, validando a escolha arquitetural para imagens de ECG. O protótipo Flask expõe o modelo VGG16 de forma acessível, integrando visão computacional ao ecossistema CardioIA (dados Fase 1, NLP Fase 2, monitoramento Fase 3).
