# CardioIA — Fase 2: NLP e triagem textual

Esta pasta (**`fase2/`**) concentra a **segunda fase** do projeto acadêmico de Inteligência Artificial em saúde cardiovascular: **processamento de linguagem natural (NLP)** aplicado a relatos de pacientes, com extração de sintomas por regras e classificação de risco por TF-IDF.

O repositório na raiz também inclui a [Fase 1 (dados tabulares, textos e ECG)](../fase1/README.md) e o [README geral](../README.md).

**Aviso:** conteúdo acadêmico e simulado; não substitui avaliação médica.

**Autor:** Gustavo Zanette Martins  
**RM:** 564523

---

## Objetivos (Fase 2)

- **Criar um mapa sintoma–doença** (CSV) com pares de sintomas e a doença cardiovascular associada, para servir de dicionário de referência.
- **Extrair sintomas de relatos textuais** usando correspondência por substring com normalização (remoção de acentos, lowercase) — abordagem de NLP baseada em regras.
- **Classificar frases de pacientes** em *baixo risco* ou *alto risco* usando vetorização TF-IDF e modelo supervisionado (`scikit-learn`).
- **Documentar** a metodologia e os dados simulados usados em cada etapa.

---

## Estrutura desta pasta (`fase2/`)

```
fase2/
├── README.md                                  # Este arquivo
├── dados/
│   ├── frases_sintomas_pacientes.txt          # 10 frases de pacientes (Parte 1)
│   ├── mapa_sintomas_doencas.csv              # Sintoma 1 | Sintoma 2 | Doença Associada
│   └── frases_risco_triagem.csv               # frase | situacao — corpus de treino (Parte 2)
├── src/
│   └── extracao_diagnostico.py                # Script de extração por regras (Parte 1)
└── notebooks/
    └── classificador_risco_tfidf.ipynb        # Notebook TF-IDF de triagem (Parte 2)
```

---

## Fontes de dados

Todos os dados desta fase são **simulados** (redigidos para fins didáticos, sem relação com pacientes reais).

### 1. Frases de pacientes (relatos textuais)

- **Arquivo:** [`dados/frases_sintomas_pacientes.txt`](dados/frases_sintomas_pacientes.txt)
- **Conteúdo:** 10 frases descritivas, cada uma com um ou mais sintomas cardiovasculares em contexto cotidiano.
- **Uso:** entrada para o script de extração por regras (`extracao_diagnostico.py`).

### 2. Mapa sintoma–doença

- **Arquivo:** [`dados/mapa_sintomas_doencas.csv`](dados/mapa_sintomas_doencas.csv)
- **Formato:** CSV com colunas `Sintoma 1`, `Sintoma 2`, `Doença Associada`.
- **Tamanho:** 40 linhas cobrindo infartos, anginas, insuficiência cardíaca, arritmias, hipertensão, entre outras.
- **Uso:** dicionário de referência para o matching por substring — quando um ou ambos os sintomas de uma linha são encontrados na frase, a doença associada é sugerida.

### 3. Corpus de triagem (classificação de risco)

- **Arquivo:** [`dados/frases_risco_triagem.csv`](dados/frases_risco_triagem.csv)
- **Formato:** CSV com colunas `frase`, `situacao` (*baixo risco* ou *alto risco*).
- **Tamanho:** 73 frases (36 de baixo risco, 37 de alto risco), razoavelmente balanceado.
- **Uso:** treino e avaliação do classificador TF-IDF no notebook.

---

## Como funciona

### Parte 1 — Extração por regras (substring matching)

O script [`src/extracao_diagnostico.py`](src/extracao_diagnostico.py) lê as 10 frases do `.txt` e o mapa CSV. Para cada frase:

1. Normaliza o texto (minúsculas + remoção de acentos via `unicodedata`).
2. Percorre cada linha do mapa testando se `Sintoma 1` e/ou `Sintoma 2` aparecem como substring na frase normalizada.
3. Agrupa os sintomas detectados e lista as doenças associadas.

Múltiplas linhas do mapa podem disparar para a mesma frase — todas as doenças são listadas, sem prioridade clínica (é um exercício didático).

### Parte 2 — Classificação de risco com TF-IDF

O notebook [`notebooks/classificador_risco_tfidf.ipynb`](notebooks/classificador_risco_tfidf.ipynb) usa o corpus `frases_risco_triagem.csv`:

1. Converte as frases em vetores numéricos com `TfidfVectorizer` do `scikit-learn`.
2. Treina um modelo de classificação (ex.: `LogisticRegression`) para separar *baixo risco* de *alto risco*.
3. Avalia com métricas de classificação (acurácia, precision, recall) no conjunto de teste.

---

## Requisitos e uso

- **Python 3** com **pandas**, **scikit-learn**, **jupyter** (e demais dependências em [`../requirements.txt`](../requirements.txt)).
- **Ambiente recomendado:** na raiz do repositório, ative o `venv` e instale:

  ```powershell
  cd ..   # raiz do repositório CardioIA (pasta que contém fase2/, venv/, requirements.txt)
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

### Parte 1 — rodar o script de extração

Na raiz do projeto:

```powershell
python fase2/src/extracao_diagnostico.py
```

O script imprime, para cada frase, os sintomas detectados e as doenças sugeridas pelo mapa. Exemplo de saída:

```
--- Frase 1 ---
Há dois dias sinto dor no peito que piora quando subo escadas...
  Sintomas detectados (trechos do mapa):
    - dor no peito
  Doenças sugeridas pelo mapa:
    - Angina estável  [via: dor no peito]
    - Infarto agudo do miocardio  [via: dor no peito]
    ...
```

### Parte 2 — notebook TF-IDF

```powershell
jupyter notebook fase2/notebooks/classificador_risco_tfidf.ipynb
```

Ou abra o `.ipynb` no VS Code e execute as células na ordem.

---

## Vídeo de demonstração (YouTube — não listado)

**Link do vídeo (Fase 2):** `https://youtu.be/JEI_BCRCK6U`

O vídeo mostra a execução do script de extração e do notebook de classificação, explicando a abordagem e os resultados.

---

## Observações

- Todos os dados desta fase são **simulados** — não usar para conclusões clínicas.
- O mapa sintoma–doença é simplificado; na prática, a relação sintoma–diagnóstico depende de contexto, exames e histórico do paciente.
- O classificador TF-IDF é um baseline didático; modelos mais robustos (embeddings, transformers, etc.) teriam melhor desempenho em dados reais.
- O projeto é de cunho **acadêmico e didático**; modelos treinados com esses dados não devem ser usados para decisões clínicas sem validação em dados reais e conformidade regulatória.
