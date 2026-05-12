# Relatório — Parte 2: MQTT, nuvem e dashboard (Fog/Cloud)

**Projeto:** CardioIA — Fase 3  
**Autor:** Gustavo Zanette Martins (RM 564523)

## Objetivo

Descrever o **fluxo de comunicação MQTT** entre o ESP32 e um **broker na nuvem** (exemplo: **HiveMQ Cloud**), e a montagem de um **dashboard no Node-RED** com gráfico em tempo real, medidor (gauge) e **indicador de alerta** quando limiares são ultrapassados.

## Visão geral da arquitetura

O firmware publica mensagens JSON no tópico:

`cardioia/esp32_01/vitals`

Cada payload inclui, entre outros campos, **temperatura**, **umidade**, **BPM**, **alerta** (0/1 calculado no dispositivo) e **backlog** (indicando se ainda existem amostras antigas na fila no momento da publicação). O Node-RED assina o mesmo tópico, interpreta o JSON e alimenta os widgets do **node-red-dashboard**.

Essa separação — **produtor** (ESP32) e **consumidor** (Node-RED) acoplados apenas por tópico e contrato JSON — é típica de arquiteturas IoT em saúde, onde novos consumidores (por exemplo, serviços de auditoria ou ML) podem ser adicionados sem alterar o firmware, desde que respeitem o esquema acordado.

## MQTT: broker, TLS e credenciais

### Escolha do broker

Utiliza-se um **cluster gerenciado** (HiveMQ Cloud) para reduzir a operação de infraestrutura e obter **TLS** nativo na porta **8883**. Em ambientes acadêmicos isso aproxima o protótipo de um cenário real, em que o tráfego entre dispositivo e nuvem não deve trafegar em claro na Internet.

### QoS e semântica de entrega

No protótipo, as publicações usam **QoS 0** (no máximo uma entrega, sem handshake adicional). Para um piloto clínico real, avaliaríamos **QoS 1** em tópicos críticos para reduzir perdas quando há oscilação de rede — ao custo de mais tráfego e armazenamento temporário no broker. O firmware já trata **backpressure** localmente: se a publicação falhar, ele **interrompe o flush** e mantém o restante da fila para uma nova tentativa no próximo ciclo, evitando descarte silencioso na borda.

### Segurança

- **TLS:** o firmware usa `WiFiClientSecure` com `setInsecure()` apenas para **simplificar o protótipo** (não valida a cadeia de certificados). Em produção, o correto é **fixar o certificado da CA** ou usar **provisioning seguro** de credenciais.
- **Autenticação:** HiveMQ Cloud exige **usuário e senha** por cluster; esses dados ficam em `secrets.h` (fora do Git) e no painel do Node-RED, nunca no repositório público.
- **Princípio do menor privilégio:** credenciais do broker devem ser **específicas do dispositivo** ou de um papel limitado (por exemplo, somente publicar em `cardioia/{id}/#`).

## Contrato de mensagem (JSON)

Exemplo ilustrativo:

```json
{
  "ts": 123456,
  "temp": 36.7,
  "hum": 55.2,
  "bpm": 88,
  "alert": 0,
  "backlog": 0
}
```

O campo `alert` espelha a lógica do edge (temperatura ou BPM acima do limiar). O dashboard **recalcula** os limiares para redundância didática e para mostrar como regras podem morar tanto no dispositivo quanto na nuvem — com o cuidado de que, em sistemas regulados, a **fonte da verdade** e o **log de decisões** precisam ser formalmente definidos.

## Node-RED: fluxo e dashboard

### Importação

O arquivo [`fase3/node-red/flows.json`](../node-red/flows.json) contém:

1. Um nó **mqtt in** inscrito em `cardioia/esp32_01/vitals`, com payload tratado como **JSON**.
2. Uma função **rotear vitais** que divide o fluxo em três saídas: temperatura, umidade e dados para alerta.
3. Um **ui_chart** (linha) para **temperatura**.
4. Um **ui_gauge** para **umidade**.
5. Uma função **alertas** que combina o flag do dispositivo com regras `temp > 38` e `bpm > 120`, exibindo texto em **ui_text**.

### Limiares e responsabilidade

Os limiares no dashboard são **coerentes** com os do firmware, o que facilita demonstrações em sala. Em um produto real, haveria **política de versionamento** de limiares (por paciente, por perfil clínico) e **trilha de auditoria** das mudanças.

### Grafana (opcional)

A integração com **Grafana Cloud** não é obrigatória para o escopo mínimo. Caso se deseje evolução, um caminho comum é persistir séries temporais em **InfluxDB** ou **Prometheus** a partir do Node-RED e conectar o Grafana como camada de exploração histórica — útil para tendências de 24 h/7 d, mas exigindo mais componentes e custos de operação.

## Eficiência e boas práticas em IoT médico

- **Payload enxuto:** JSON compacto reduz bytes por minuto — relevante em conexões instáveis e em planos de dados M2M.
- **Backlog explícito:** o campo `backlog` ajuda operadores a perceber que o gráfico pode estar “atrasado” em relação ao paciente após uma queda de rede.
- **Privacidade:** mesmo com dados simulados, o desenho com tópicos por dispositivo facilita **isolamento** e futura **pseudonimização** dos IDs.

## Conclusão

A Parte 2 fecha o ciclo **edge → MQTT → visualização**, com TLS no broker, contrato JSON explícito e dashboard reativo com alertas. O protótipo está preparado para evolução (QoS 1, validação de certificado, persistência histórica e Grafana) sem quebrar o fluxo básico demonstrado na disciplina.
