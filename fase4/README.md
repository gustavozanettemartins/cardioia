# CardioIA — Fase 4: Visão Computacional em ECG

Quarta fase do projeto: **pré-processamento** de imagens de ECG, **classificação com CNN** (modelo simples e transfer learning VGG16), **métricas de avaliação** e **protótipo Flask** para apresentação dos resultados.

**Autor:** Gustavo Zanette Martins  
**RM:** 564523

---

## Resultados (treino com dataset real — Kaggle)

Dataset: **54.613 imagens** em `dataset/ecg_img/` · classes **F, N, Q, S, V** · GPU **RTX 4090 (WSL2)**.

| Modelo | Acurácia (teste) | F1 (macro) |
|--------|------------------|------------|
| CNN simples (3 épocas) | 3,2% | 0,01 |
| **VGG16 transfer learning** | **80,3%** | **0,69** |

O Flask usa o **VGG16** (`fase4/models/ecg_transfer_best.keras`). Detalhes: [docs/relatorio_parte2_cnn_flask.md](docs/relatorio_parte2_cnn_flask.md).

---

## Estrutura

```
fase4/
├── README.md
├── requirements-fase4.txt
├── notebooks/
│   ├── 01_preprocessamento_ecg.ipynb      # Parte 1
│   └── 02_cnn_classificacao_ecg.ipynb     # Parte 2
├── src/
│   ├── preprocessamento.py
│   ├── modelos.py
│   ├── avaliacao.py
│   └── inferencia.py
├── scripts/
│   ├── train_pipeline.py                  # Treino + métricas + figuras
│   ├── venv_gpu_path.sh                   # LD_LIBRARY_PATH para GPU no WSL2
│   ├── download_ecg_dataset.py
│   ├── generate_demo_ecg_dataset.py
│   └── capture_flask_demo.py
├── app/
│   ├── app.py                             # Protótipo Flask
│   ├── templates/index.html
│   └── static/style.css
├── models/                                # .keras (gerados localmente; gitignore)
├── data/processed/                        # splits.json (gitignore)
└── docs/
    ├── relatorio_parte1_preprocessamento.md
    ├── relatorio_parte2_cnn_flask.md
    └── imagens/                           # Prints de métricas e Flask
```

Dataset bruto: [`dataset/ecg_img/`](../dataset/ecg_img/) (não versionado — download Kaggle local).

---

## Ambiente recomendado: WSL2 + GPU (Windows)

TensorFlow **2.11+** no Windows nativo **não usa GPU**. Para treinar com NVIDIA (ex.: RTX 4090), use **Ubuntu no WSL2**.

### Setup inicial (uma vez)

No **PowerShell (Admin)**, se ainda não tiver Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

No **terminal Ubuntu (WSL)**:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3.12-venv

python3 -m venv ~/cardioia-venv
source ~/cardioia-venv/bin/activate

cd /mnt/d/Projetos/FIAP/cardioia
pip install --upgrade pip
pip install -r requirements.txt
pip install "tensorflow[and-cuda]"
```

**GPU no WSL2:** o TensorFlow precisa encontrar as bibliotecas CUDA/cuDNN. Use o script [`scripts/venv_gpu_path.sh`](scripts/venv_gpu_path.sh), que configura o `LD_LIBRARY_PATH`.

Adicione ao final de `~/cardioia-venv/bin/activate` (uma vez):

```bash
if [ -f /mnt/d/Projetos/FIAP/cardioia/fase4/scripts/venv_gpu_path.sh ]; then
  . /mnt/d/Projetos/FIAP/cardioia/fase4/scripts/venv_gpu_path.sh
fi
```

Ou, manualmente em cada sessão, antes de treinar:

```bash
source ~/cardioia-venv/bin/activate
source /mnt/d/Projetos/FIAP/cardioia/fase4/scripts/venv_gpu_path.sh
```

**Testar GPU:**

```bash
source ~/cardioia-venv/bin/activate
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

Esperado: `[PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]`.

### Sessão de trabalho (WSL)

```bash
source ~/cardioia-venv/bin/activate
cd /mnt/d/Projetos/FIAP/cardioia
```

### Alternativa: Windows (CPU ou inferência leve)

```powershell
cd D:\Projetos\FIAP\cardioia
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Treino completo no CPU é **muito lento** (~54k imagens). Flask após treino pode rodar no WSL (recomendado) ou no Windows se TensorFlow estiver instalado.

---

## Dataset ECG

### Download manual (usado neste projeto)

1. [ECG Images — Kaggle (analiviafr)](https://www.kaggle.com/datasets/analiviafr/ecg-images)
2. Extrair em **`dataset/ecg_img/`** na raiz do repositório:

```
dataset/ecg_img/
├── train/   (F, N, Q, S, V)
└── test/    (F, N, Q, S, V)
```

| Pasta | Descrição |
|-------|-----------|
| `N` | Batimento normal |
| `S` | Ectópico supraventricular |
| `V` | Ectópico ventricular |
| `F` | Batimento de fusão |
| `Q` | Desconhecido / estimulado |

### Outras opções

- API Kaggle: `python fase4/scripts/download_ecg_dataset.py`
- Demo sintético (offline): `python fase4/scripts/generate_demo_ecg_dataset.py`

---

## Ordem de execução

### 1. Pré-processamento (Parte 1)

**WSL:**

```bash
jupyter notebook fase4/notebooks/01_preprocessamento_ecg.ipynb
```

Gera metadados em `fase4/data/processed/splits.json`.

Relatório: [docs/relatorio_parte1_preprocessamento.md](docs/relatorio_parte1_preprocessamento.md)

### 2. Treino e métricas (Parte 2)

**WSL (recomendado):**

```bash
python fase4/scripts/train_pipeline.py
```

Saída: modelos em `fase4/models/`, figuras em `fase4/docs/imagens/`, resumo em `metricas_resumo.json`.

Notebook alternativo: `fase4/notebooks/02_cnn_classificacao_ecg.ipynb`

Relatório: [docs/relatorio_parte2_cnn_flask.md](docs/relatorio_parte2_cnn_flask.md)

### 3. Protótipo Flask

**WSL:**

```bash
python fase4/app/app.py
```

Abrir no navegador (Windows): [http://127.0.0.1:5000](http://127.0.0.1:5000)

Modelo padrão: `fase4/models/ecg_transfer_best.keras` (VGG16).

---

## Evidências (prints)

Pasta [`docs/imagens/`](docs/imagens/):

| Arquivo | Descrição |
|---------|-----------|
| `matriz_confusao_cnn_simples.png` | Matriz de confusão — CNN |
| `matriz_confusao_transfer_learning.png` | Matriz de confusão — VGG16 |
| `historico_*.png` | Curvas de treino |
| `metricas_comparacao.png` | Comparação de métricas |
| `flask-demo.png` | Captura do protótipo Flask |

---

## Integração CardioIA

| Fase | Contribuição |
|------|----------------|
| [Fase 1](../fase1/README.md) | Dataset e justificativa de visão computacional em ECG |
| [Fase 2](../fase2/README.md) | Triagem textual (NLP) |
| [Fase 3](../fase3/README.md) | Monitoramento IoT (sinais vitais) |
| **Fase 4** | Classificação visual de ECG (CNN + Flask) |

---

## Aviso legal

Conteúdo **acadêmico**. O protótipo **não substitui** avaliação, diagnóstico ou conduta médica. Modelos não devem ser usados clinicamente sem validação e conformidade regulatória.

---

## Repositório geral

[README.md](../README.md) · [github.com/gustavozanettemartins/cardioia](https://github.com/gustavozanettemartins/cardioia)
