# CardioIA — Fase 5: Assistente Cardiológico Conversacional

Quinta fase do projeto: **assistente conversacional** com NLP para triagem inicial em saúde cardiovascular, backend **Flask** e interface de **chat HTML**.

**Autor:** Gustavo Zanette Martins  
**RM:** 564523

**Aviso:** protótipo acadêmico e simulado; não substitui avaliação médica.

---

## Objetivos

- Modelar fluxo conversacional com intents, entities e dialog nodes (Watson Assistant).
- Integrar assistente a backend Flask via API REST.
- Oferecer interface web simples para troca de mensagens.
- Reutilizar vocabulário de sintomas da [Fase 2](../fase2/README.md).

---

## Estrutura

```
fase5/
├── README.md
├── requirements-fase5.txt
├── .env.example
├── src/
│   ├── assistant_client.py      # Fábrica mock / watson
│   ├── mock_assistant.py        # Motor de diálogo local
│   ├── watson_assistant.py      # Integração IBM Watson
│   └── text_utils.py
├── watson/
│   └── assistant_export.json      # Export/referência do assistente
├── app/
│   ├── app.py                   # Flask (porta 5001)
│   ├── templates/chat.html
│   └── static/
│       ├── style.css
│       └── chat.js
├── scripts/
│   └── test_flows.py            # Testes dos fluxos conversacionais
└── docs/
    └── relatorio_fluxo_conversacional.md
```

---

## Como executar (modo mock — padrão)

```powershell
# Na raiz do projeto
.\venv\Scripts\Activate.ps1
pip install -r fase5/requirements-fase5.txt

# Iniciar o chat
python fase5/app/app.py
```

Abrir **http://127.0.0.1:5001** no navegador.

### Testar via API (curl / PowerShell)

```powershell
# PowerShell
$body = '{"message":"ola"}' 
Invoke-RestMethod -Uri http://127.0.0.1:5001/api/chat -Method POST -Body $body -ContentType "application/json"
```

```bash
# curl
curl -X POST http://127.0.0.1:5001/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"sinto dor no peito\"}"
```

### Testar fluxos no terminal

```powershell
python fase5/scripts/test_flows.py
```

---

## Modo Watson (IBM Cloud)

1. Criar instância do [Watson Assistant](https://cloud.ibm.com/catalog/services/watson-assistant) no IBM Cloud.
2. Modelar intents/entities/dialog conforme [`watson/assistant_export.json`](watson/assistant_export.json).
3. Exportar o workspace e substituir o JSON em `watson/assistant_export.json`.
4. Copiar `.env.example` para `.env` e preencher:

```env
CARDIOIA_ASSISTANT=watson
WATSON_API_KEY=sua_api_key
WATSON_ASSISTANT_ID=seu_assistant_id
WATSON_ENVIRONMENT_ID=seu_environment_id
WATSON_URL=https://api.us-south.assistant.watson.cloud.ibm.com
```

**Onde encontrar os IDs no Watson:**
- Abra o assistente **CardioIA** → **Settings** (engrenagem) → **API details**
- **Assistant ID** — identificador do assistente
- **Environment ID** — opcional; na experiência Classic com Dialog Skill muitas vezes não aparece. Deixe `WATSON_ENVIRONMENT_ID` vazio no `.env` que o backend resolve automaticamente.

5. Reiniciar o Flask.

---

## Fluxo conversacional

| Intent | Exemplo | Ação |
|--------|---------|------|
| `saudacao` | "olá", "preciso de ajuda" | Boas-vindas + menu de opções |
| `relatar_sintomas` | "sinto dor no peito" | Coleta sintomas, intensidade e duração |
| `emergencia` | "não consigo respirar" | Orientação SAMU 192 |
| `informacao_geral` | "o que é arritmia?" | Resposta educativa |
| `agendar_consulta` | "quero marcar consulta" | Orientação de agendamento |
| `despedida` | "obrigado", "tchau" | Encerramento |
| `anything_else` | mensagem fora do escopo | Fallback com sugestões |

**Entities:** `@sintoma`, `@intensidade`, `@duracao`

Detalhes no [relatório](docs/relatorio_fluxo_conversacional.md).

---

## Arquitetura

```
Usuário (chat.html)
    │ POST /api/chat
    ▼
Flask (app.py)
    │ get_assistant()
    ▼
mock_assistant.py  ou  watson_assistant.py
    │ resposta + meta (intent, risco, sintomas)
    ▼
JSON → chat.js → bolhas na interface
```

---
