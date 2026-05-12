# Relatório — Parte 1: armazenamento e processamento local (Edge)

**Projeto:** CardioIA — Fase 3  
**Autor:** Gustavo Zanette Martins (RM 564523)

## Contexto

Esta etapa implementa o papel do **Edge Computing** em um monitoramento cardiológico simulado: o ESP32 lê sinais vitais de forma periódica, trata **indisponibilidade de rede** sem perder leituras (dentro de um limite acordado) e só então encaminha dados à nuvem quando a conectividade está disponível.

## Sensores e leituras

- **DHT22 (obrigatório):** mede **temperatura** e **umidade relativa**. Pelo enunciado da disciplina, o DHT22 conta como **um único sensor**, apesar de entregar duas grandezas.
- **Botão de pulso (livre escolha):** simula **batimentos** por meio de pressões repetidas; o firmware estima **batimentos por minuto (BPM)** com base na contagem de bordas de descida dentro de uma janela móvel de um minuto. Essa abordagem atende ao requisito de um segundo sensor distinto e evita hardware adicional no simulador.

## Fluxo de funcionamento

1. A cada intervalo fixo (por exemplo, 4 segundos), o firmware lê temperatura e umidade, calcula o BPM a partir do botão e calcula um **flag de alerta** quando a temperatura ultrapassa 38 °C ou o BPM ultrapassa 120 (limiares didáticos, alinhados ao dashboard da Parte 2).
2. Cada leitura é transformada em uma **amostra** (`timestamp`, temperatura, umidade, BPM, alerta) e **enfileirada**.
3. Se a rede estiver **offline** (no modo acadêmico, uma variável booleana controlada por botão simula isso), o sistema **continua apenas enfileirando** e registrando eventos no **Monitor Serial** (`ENQUEUE`, `DROP`, etc.).
4. Quando a rede está **online**, o firmware tenta **drenar a fila** publicando as amostras na ordem **FIFO** (mais antiga primeiro), o que reproduz a **sincronização de backlog** após uma queda de conectividade. No modo simulado (sem `secrets.h`), essa drenagem ocorre **via `Serial.println`** (linhas com prefixo `SIM CLOUD FLUSH` / `SIM PUBLISH …`), atendendo literalmente ao enunciado: *"Quando 'conectado', envie os dados armazenados para a nuvem via Serial.println e apague o arquivo local."* No modo com broker (`secrets.h` preenchido), a mesma fila é drenada via **MQTT publish** TLS no HiveMQ Cloud.

## Lógica de resiliência e limite de armazenamento

O armazenamento local utiliza uma **fila circular em RAM** com capacidade fixa (por exemplo, 32 amostras). Essa escolha reflete um **modelo de negócio** de monitoramento contínuo em que:

- O dispositivo deve manter **continuidade clínica** durante curtas interrupções de rede (fila curta, minutos de dados).
- Não é razoável crescer o buffer sem limite em um microcontrolador: há pouca RAM e risco de latência excessiva ao ressincronizar.

Quando a fila está cheia e chega uma nova amostra, a política adotada é **descartar a amostra mais antiga (FIFO)** e manter as mais recentes. Isso é registrado no Serial como `DROP oldest`, permitindo **auditoria** mesmo no simulador.

### SPIFFS e simulador Wokwi

O enunciado alerta que **SPIFFS em simuladores é volátil** e, em muitos cenários, inadequado para CSV persistente. O firmware deixa **`USE_SPIFFS` desligado por padrão** e documenta que, em **ESP32 físico**, pode-se ativar gravação complementar em arquivo (`/vitals.csv`). Quando `USE_SPIFFS=1`, ao concluir um flush bem-sucedido, o arquivo local é apagado — exatamente como pede o enunciado ("apague o arquivo local"). No Wokwi, o **Monitor Serial** cumpre o papel de evidência da resiliência offline, como alternativa sugerida pelo material.

### Wi-Fi simulada versus Wi-Fi real

Sem `secrets.h` com SSID preenchido, o firmware opera em **modo simulado**: um botão alterna “online/offline” para demonstrar fila e flush **sem depender** de laboratório de rede. Com `secrets.h` válido, o ESP32 usa **Wi-Fi real** e o estado online segue o `WiFi.status()`, aproximando um piloto de campo.

## Conclusão

A Parte 1 mostra, de ponta a ponta na borda, o ciclo **capturar → enfileirar → sincronizar**, com política de buffer explícita e observabilidade por Serial. Essa base é necessária para a Parte 2, em que as mesmas amostras passam a ser **publicadas via MQTT** e visualizadas em tempo quase real no Node-RED.
