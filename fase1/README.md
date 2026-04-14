# CardioIA — Fase 1: dados tabulares, textos e ECG

Esta pasta (**`fase1/`**) concentra a **primeira fase** do projeto acadêmico de Inteligência Artificial em saúde cardiovascular: integração de **dados estruturados simulados**, **textos de referência** para NLP e referência a **imagens de ECG** para visão computacional.

O repositório na raiz também inclui a [Fase 2 (NLP e triagem)](../fase2/README.md), o [README geral](../README.md).

**Autor:** Gustavo Zanette Martins  
**RM:** 564523

---

## Objetivos (Fase 1)

- **Construir e documentar fontes de dados** para modelos de IA em saúde cardiovascular (dados tabulares, textos e imagens de ECG).
- **Gerar um dataset sintético** com variáveis clínicas relevantes (idade, sexo, pressão arterial, colesterol, histórico cardíaco, sintomas, frequência cardíaca) para fins didáticos e de prototipagem.
- **Organizar textos de referência** (literatura clássica e saúde pública) sobre doenças cardíacas, arteriosclerose, hipertensão e tratamento, para apoio a análises de NLP.
- **Incorporar imagens de ECG** como base para algoritmos de visão computacional (detecção de padrões, classificação de ritmo, reconhecimento de anomalias) — imagens obtidas por download externo (Kaggle), conforme abaixo.
- **Documentar** a relevância das variáveis clínicas, o uso de NLP nos textos e a justificativa do uso de visão computacional em imagens de ECG no contexto de IA em saúde.

---

## Estrutura desta pasta (`fase1/`)

```
fase1/
├── README.md                          # Este arquivo
├── main.py                            # Geração do dataset cardiovascular (sintético)
├── dataset_cardiovascular.csv         # Dataset em CSV (gerado por main.py; dados simulados)
├── rep-github.txt                     # Referência ao repositório remoto
├── docs/                              # Documentação e fontes textuais
│   ├── arteriosclerosis_hypertension_blood_pressure.txt
│   ├── disturbances_of_the_heart.txt
│   ├── opas_doenca_cardiovascular_sintomas_prevencao_tratamento.txt
│   ├── variaveis_relevantes_ia_saude.md
│   ├── uso_nlp_textos_saude.md
│   └── justificativa_visao_computacional_ecg.md
└── eletrocardiograma_dataset/         # (Opcional) Criar após baixar o dataset no Kaggle — ver seção Imagens de ECG
    ├── train/
    └── test/
```

A pasta `eletrocardiograma_dataset/` **não** vem versionada por padrão: ela é preenchida localmente após o download das imagens no Kaggle (veja instruções mais abaixo).

---

## Fontes de dados

### 1. Dataset cardiovascular (dados tabulares) — **SIMULADOS**

- **Arquivo:** [`dataset_cardiovascular.csv`](dataset_cardiovascular.csv) (dentro de **`fase1/`**).
- **Geração:** script [`main.py`](main.py) (Python + pandas).
- **Natureza dos dados:** **Totalmente simulados (sintéticos).** Os registros não correspondem a pacientes reais; foram gerados aleatoriamente com distribuições plausíveis para fins de estudo e prototipagem.
- **Variáveis:** idade, sexo, pressão arterial (sistólica/diastólica), colesterol (mg/dL), histórico de doenças cardíacas (Sim/Não), sintomas (categórico), frequência cardíaca (bpm).
- **Tamanho:** 120 linhas (configurável em `main.py`).
- **Uso:** análise exploratória, modelagem preditiva didática, integração com outros dados do projeto. **Não utilizar para conclusões clínicas ou epidemiológicas.**

### 2. Imagens de ECG — **dataset externo (Kaggle)**

- **Pasta local esperada:** `fase1/eletrocardiograma_dataset/` (estrutura com `train/` e `test/`; subpastas por classe são opcionais).
- **Fonte:** dataset **ECG Images** do Kaggle.  
  **URL:** https://www.kaggle.com/datasets/analiviafr/ecg-images?resource=download  
  **Autoria/atribuição:** [analiviafr](https://www.kaggle.com/analiviafr) — ECG Images.
- **Natureza:** imagens de traçados de eletrocardiograma (ECG), utilizadas para treino e teste de modelos de visão computacional (classificação de ritmo, detecção de padrões, anomalias).
- **Uso:** desenvolvimento e avaliação de algoritmos de visão computacional aplicados a ECG, em caráter acadêmico e de pesquisa.

### 3. Textos de referência (documentação e corpus para NLP)

| Arquivo | Fonte | Conteúdo |
|--------|--------|----------|
| `docs/arteriosclerosis_hypertension_blood_pressure.txt` | Project Gutenberg (eBook #37675) | Louis M. Warfield — arteriosclerose, hipertensão, pressão arterial (excertos). |
| `docs/disturbances_of_the_heart.txt` | Project Gutenberg (eBook #3731) | Oliver T. Osborne — distúrbios do coração, pressão arterial, tratamento (excertos). |
| `docs/opas_doenca_cardiovascular_sintomas_prevencao_tratamento.txt` | Blog OPAS (opas.org.br) | Doença cardiovascular: sintomas, fatores de risco, prevenção e tratamento (português). |

- **Licença / uso:** Project Gutenberg — domínio público; OPAS — conteúdo de divulgação em saúde. Uso no projeto para fins acadêmicos e de NLP (extração de entidades, classificação de tópicos, etc.), conforme descrito em `docs/uso_nlp_textos_saude.md`.

---

## Resumo: origem e tipo dos dados

| Dado | Origem | Simulado? |
|------|--------|-----------|
| **Dataset cardiovascular (CSV)** | Gerado por `main.py` em `fase1/` | **Sim — 100% simulados** |
| **Imagens de ECG** | Kaggle — [ECG Images (analiviafr)](https://www.kaggle.com/datasets/analiviafr/ecg-images?resource=download) | Não — dataset real de imagens (hospedado no Kaggle) |
| **Textos em `docs/`** | Project Gutenberg e OPAS | Não — fontes públicas/publicadas |

---

## Links públicos para acesso aos dados

**Repositório:** [github.com/gustavozanettemartins/cardioia](https://github.com/gustavozanettemartins/cardioia)

| Tipo de dado | Onde acessar | Link / observação |
|--------------|--------------|-------------------|
| **Dados numéricos** (CSV) | Pasta `fase1/` no GitHub | Arquivo [`fase1/dataset_cardiovascular.csv`](dataset_cardiovascular.csv) (caminho no repositório: **`fase1/dataset_cardiovascular.csv`**). Para download direto no GitHub, use o botão *Raw* na página do arquivo ou clone o repositório. |
| **Textos** (NLP) | `fase1/docs/` | Documentação e `.txt` em [`docs/`](docs/). |
| **Imagens** (ECG) | Armazenamento público (Kaggle) | [**ECG Images — Kaggle**](https://www.kaggle.com/datasets/analiviafr/ecg-images?resource=download) (dataset completo). Acesso público; é necessário login gratuito no Kaggle para download. |

Garanta que o repositório GitHub esteja **público** e que os links acima estejam acessíveis. Se preferir hospedar também o CSV e os textos em Google Drive ou OneDrive, acrescente aqui links com compartilhamento público (qualquer pessoa com o link).

---

## Requisitos e uso

- **Python 3** com **pandas** (e demais dependências do repositório em [`../requirements.txt`](../requirements.txt)).
- **Ambiente recomendado:** na raiz do clone do repositório, ative o `venv` e instale as dependências:

  ```powershell
  cd ..   # raiz do repositório CardioIA (pasta que contém fase1/, venv/, requirements.txt)
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

### Gerar o dataset cardiovascular

O `main.py` grava o CSV no **diretório de trabalho atual** com o nome `dataset_cardiovascular.csv`. Para que o arquivo fique em **`fase1/`** (ao lado do script), execute a partir desta pasta:

```powershell
cd fase1
python main.py
```

O arquivo `dataset_cardiovascular.csv` será criado ou sobrescrito **em `fase1/`**.

> **Nota:** se você rodar `python fase1/main.py` a partir da **raiz** do repositório, o CSV tende a ser gerado na **raiz** (comportamento do `cwd`), e não dentro de `fase1/`. Prefira `cd fase1` antes de executar, alinhado à estrutura descrita neste README.

### Imagens de ECG

Baixe o dataset no link do Kaggle indicado acima e coloque as imagens em `fase1/eletrocardiograma_dataset/`, nas subpastas `train/` e `test/` (mantenha pelo menos cerca de 100 imagens no total, conforme orientação original do projeto).

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
