# Projeto de Inteligência Artificial em Saúde Cardiovascular

Projeto acadêmico que integra **dados estruturados**, **textos de referência** e **imagens de ECG** para aplicações de IA na área de saúde cardiovascular, incluindo análise de variáveis clínicas, processamento de linguagem natural (NLP) e visão computacional.

**Autor:** Gustavo Zanette Martins  
**RM:** 564523

---

## Objetivos

- **Construir e documentar fontes de dados** para modelos de IA em saúde cardiovascular (dados tabulares, textos e imagens de ECG).
- **Gerar um dataset sintético** com variáveis clínicas relevantes (idade, sexo, pressão arterial, colesterol, histórico cardíaco, sintomas, frequência cardíaca) para fins didáticos e de prototipagem.
- **Organizar textos de referência** (literatura clássica e saúde pública) sobre doenças cardíacas, arteriosclerose, hipertensão e tratamento, para apoio a análises de NLP.
- **Incorporar imagens de ECG** como base para algoritmos de visão computacional (detecção de padrões, classificação de ritmo, reconhecimento de anomalias).
- **Documentar** a relevância das variáveis clínicas, o uso de NLP nos textos e a justificativa do uso de visão computacional em imagens de ECG no contexto de IA em saúde.

---

## Estrutura do Projeto

```
fase1/
├── README.md                          # Este arquivo
├── main.py                             # Geração do dataset cardiovascular (sintético)
├── dataset_cardiovascular.csv          # Dataset em CSV (dados simulados)
├── docs/                               # Documentação e fontes textuais
│   ├── arteriosclerosis_hypertension_blood_pressure.txt   # Fonte: Project Gutenberg
│   ├── disturbances_of_the_heart.txt                      # Fonte: Project Gutenberg
│   ├── opas_doenca_cardiovascular_sintomas_prevencao_tratamento.txt  # Fonte: OPAS
│   ├── variaveis_relevantes_ia_saude.md                   # Variáveis clínicas e priorização
│   ├── uso_nlp_textos_saude.md                            # NLP nos textos e relevância para IA
│   └── justificativa_visao_computacional_ecg.md           # Visão computacional em ECG
└── eletrocardiograma_dataset/          # Imagens de ECG (fonte: Kaggle — ver abaixo)
    ├── train/
    └── test/
```

---

## Fontes de Dados

### 1. Dataset cardiovascular (dados tabulares) — **SIMULADOS**

- **Arquivo:** `dataset_cardiovascular.csv`
- **Geração:** script `main.py` (Python + pandas).
- **Natureza dos dados:** **Totalmente simulados (sintéticos).** Os registros não correspondem a pacientes reais; foram gerados aleatoriamente com distribuições plausíveis para fins de estudo e prototipagem.
- **Variáveis:** idade, sexo, pressão arterial (sistólica/diastólica), colesterol (mg/dL), histórico de doenças cardíacas (Sim/Não), sintomas (categórico), frequência cardíaca (bpm).
- **Tamanho:** 120 linhas (configurável em `main.py`).
- **Uso:** Análise exploratória, modelagem preditiva didática, integração com outros dados do projeto. **Não utilizar para conclusões clínicas ou epidemiológicas.**

### 2. Imagens de ECG — **dataset externo (Kaggle)**

- **Pasta:** `eletrocardiograma_dataset/` (estrutura tipicamente `train/` e `test/` com subpastas por classe).
- **Fonte:** Dataset **ECG Images** do Kaggle.  
  **URL:** https://www.kaggle.com/datasets/analiviafr/ecg-images?resource=download  
  **Autoria/atribuição:** [analiviafr](https://www.kaggle.com/analiviafr) — ECG Images.
- **Natureza:** Imagens de traçados de eletrocardiograma (ECG), utilizadas para treino e teste de modelos de visão computacional (classificação de ritmo, detecção de padrões, anomalias).
- **Uso:** Desenvolvimento e avaliação de algoritmos de visão computacional aplicados a ECG, em caráter acadêmico e de pesquisa.

### 3. Textos de referência (documentação e corpus para NLP)

| Arquivo | Fonte | Conteúdo |
|--------|--------|----------|
| `arteriosclerosis_hypertension_blood_pressure.txt` | Project Gutenberg (eBook #37675) | Louis M. Warfield — arteriosclerose, hipertensão, pressão arterial (excertos). |
| `disturbances_of_the_heart.txt` | Project Gutenberg (eBook #3731) | Oliver T. Osborne — distúrbios do coração, pressão arterial, tratamento (excertos). |
| `opas_doenca_cardiovascular_sintomas_prevencao_tratamento.txt` | Blog OPAS (opas.org.br) | Doença cardiovascular: sintomas, fatores de risco, prevenção e tratamento (português). |

- **Licença / uso:** Project Gutenberg — domínio público; OPAS — conteúdo de divulgação em saúde. Uso no projeto para fins acadêmicos e de NLP (extração de entidades, classificação de tópicos, etc.), conforme descrito em `docs/uso_nlp_textos_saude.md`.

---

## Resumo: origem e tipo dos dados

| Dado | Origem | Simulado? |
|------|--------|-----------|
| **Dataset cardiovascular (CSV)** | Gerado por `main.py` | **Sim — 100% simulados** |
| **Imagens de ECG** | Kaggle — [ECG Images (analiviafr)](https://www.kaggle.com/datasets/analiviafr/ecg-images?resource=download) | Não — dataset real de imagens |
| **Textos em `docs/`** | Project Gutenberg e OPAS | Não — fontes públicas/publicadas |

---

## Links públicos para acesso aos dados (correção FIAP)

Para que o time da FIAP possa acessar o conjunto completo de dados, seguem os links públicos:

| Tipo de dado | Onde acessar | Link / observação |
|--------------|--------------|-------------------|
| **Dados numéricos** (CSV) | Neste repositório | Arquivo [`dataset_cardiovascular.csv`](dataset_cardiovascular.csv) na raiz do repositório. Para link direto de download no GitHub: use o botão *Raw* na página do arquivo ou clone o repositório. |
| **Textos** (NLP) | Subpasta `docs/` | Os arquivos `.txt` e a documentação estão em [`docs/`](docs/) neste repositório. |
| **Imagens** (ECG) | Armazenamento público | [**ECG Images — Kaggle**](https://www.kaggle.com/datasets/analiviafr/ecg-images?resource=download) (dataset completo, >100 imagens). Acesso público; necessário login gratuito no Kaggle para download. |

Garanta que o repositório GitHub esteja **público** e que os links acima estejam acessíveis. Se preferir hospedar também o CSV e os textos em Google Drive ou OneDrive, adicione aqui os links com compartilhamento público (qualquer pessoa com o link).

---

## Requisitos e uso

- **Python 3** com **pandas** (para executar `main.py` e gerar/regenerar o CSV).
- Para gerar o dataset cardiovascular:  
  `python main.py`  
  O arquivo `dataset_cardiovascular.csv` será criado/sobrescrito na raiz do projeto.
- As imagens de ECG devem ser obtidas pelo download do dataset no link do Kaggle indicado acima e colocadas na pasta `eletrocardiograma_dataset/` conforme a estrutura esperada (train/test e subpastas por classe).

---

## Documentação complementar

- **Variáveis clínicas:** `docs/variaveis_relevantes_ia_saude.md` — priorização das variáveis para modelos de IA em saúde cardiovascular.
- **NLP nos textos:** `docs/uso_nlp_textos_saude.md` — como os textos podem ser explorados por NLP e relevância para IA em saúde.
- **Visão computacional em ECG:** `docs/justificativa_visao_computacional_ecg.md` — detecção de padrões, bordas e anomalias em imagens de ECG e importância para projetos de IA em saúde.

---

## Observações

- Nenhum dado de pacientes reais é utilizado no dataset CSV; todos os registros são **simulados**.
- As imagens de ECG vêm de dataset **público do Kaggle** (atribuição acima); os textos são de **domínio público ou divulgação pública** (Gutenberg, OPAS).
- O projeto é de cunho **acadêmico e didático**; modelos treinados com esses dados não devem ser usados para decisões clínicas sem validação em dados reais e conformidade regulatória.
