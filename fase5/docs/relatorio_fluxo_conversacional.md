# Relatório — Fluxo conversacional do assistente cardiológico

**Projeto:** CardioIA — Fase 5  
**Autor:** Gustavo Zanette Martins (RM 564523)

## Objetivo

Desenvolver um protótipo de assistente conversacional para triagem inicial em saúde cardiovascular, integrando NLP (IBM Watson Assistant ou mock local) a um backend Flask e interface web de chat.

## Arquitetura

```
┌─────────────┐     POST /api/chat      ┌──────────────┐
│  chat.html  │ ──────────────────────► │  Flask app   │
│  + chat.js  │ ◄────────────────────── │  (porta 5001)│
└─────────────┘     JSON reply+meta     └──────┬───────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │  assistant_client   │
                                    │  (mock ou watson)   │
                                    └──────────┬──────────┘
                                               │
                              ┌────────────────┴────────────────┐
                              ▼                                 ▼
                    mock_assistant.py                  watson_assistant.py
                    (keywords + sessões)               (IBM Cloud API)
```

O frontend envia `{ "message": "...", "session_id": "..." }` e recebe `{ "reply": "...", "session_id": "...", "meta": { "intent", "risco", ... } }`. As credenciais Watson permanecem no servidor (`.env`), nunca expostas ao navegador.

## Modelagem conversacional

### Intents

| Intent | Descrição | Exemplos de utterances |
|--------|-----------|------------------------|
| `saudacao` | Início da conversa | "olá", "bom dia", "preciso de ajuda" |
| `relatar_sintomas` | Usuário descreve queixas | "sinto dor no peito", "tenho falta de ar" |
| `emergencia` | Situação crítica | "dor forte no peito", "não consigo respirar" |
| `informacao_geral` | Perguntas educativas | "o que é arritmia?", "sintomas de infarto" |
| `agendar_consulta` | Pedido de consulta | "quero marcar consulta" |
| `despedida` | Encerramento | "obrigado", "tchau" |
| `anything_else` | Fallback | mensagens não reconhecidas |

### Entities

| Entity | Valores | Uso no diálogo |
|--------|---------|----------------|
| `@sintoma` | dor no peito, falta de ar, palpitações, cansaço, tontura, inchaço | Extração para triagem |
| `@intensidade` | leve, moderada, forte | Classificação de urgência |
| `@duracao` | horas, dias, semanas | Contexto temporal |

### Fluxo de diálogo (dialog nodes)

1. **Welcome** → saudação e pergunta aberta.
2. **Emergência** (prioridade) → orientação SAMU 192, encerra triagem leve.
3. **Coletar sintomas** → registra `@sintoma`, pergunta intensidade e duração.
4. **Recomendação** → avalia risco (baixo/moderado/alto) e sugere conduta.
5. **Informação geral** → respostas educativas sem diagnóstico.
6. **Agendar consulta** → orientações de encaminhamento.
7. **Anything else** → reformulação após falha de compreensão.

O arquivo [`watson/assistant_export.json`](../watson/assistant_export.json) documenta essa estrutura para importação no IBM Watson Assistant.

## Integração com Fase 2

O mock reutiliza o mapa sintoma–doença da Fase 2 (`fase2/dados/mapa_sintomas_doencas.csv`) via `extracao_diagnostico.py`. Quando sintomas são detectados por substring normalizada, o assistente lista possíveis condições associadas de forma **didática**, sem afirmar diagnóstico.

## Modos de operação

| Modo | Variável | Quando usar |
|------|----------|-------------|
| Mock local | `CARDIOIA_ASSISTANT=mock` | Desenvolvimento offline, demo sem IBM Cloud |
| Watson real | `CARDIOIA_ASSISTANT=watson` | Entrega acadêmica com NLP em nuvem |

## Limitações

- Protótipo acadêmico: **não substitui** avaliação médica profissional.
- Mock usa correspondência por keywords (menos robusto que Watson NLP).
- Sessões em memória — reiniciam ao parar o servidor.
- Dados de triagem não são persistidos em banco de dados.

## Como testar

```powershell
python fase5/app/app.py
# Abrir http://127.0.0.1:5001

python fase5/scripts/test_flows.py
```

Cenários validados: saudação, sintomas leves com triagem, emergência (SAMU), fallback e despedida.
