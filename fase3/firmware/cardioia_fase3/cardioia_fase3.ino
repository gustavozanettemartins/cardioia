/**
 * CardioIA — Fase 3 (ESP32)
 *
 * Sensores: DHT22 (temperatura + umidade = 1 sensor) e botão de pulso (BPM simulado).
 * Edge: fila FIFO em RAM com limite; SPIFFS opcional em hardware real.
 * Conectividade: Wi-Fi real (secrets.h) ou Wi-Fi simulada (botão; sem rede).
 * Nuvem: MQTT TLS (HiveMQ Cloud) com payload JSON quando configurado;
 *        no modo simulado, o "envio à nuvem" é feito via Serial.println
 *        (fallback didático exigido pelo enunciado da Parte 1).
 *
 * Bibliotecas: DHT sensor library (Adafruit) + Adafruit Unified Sensor, PubSubClient,
 *              ArduinoJson v6.
 *
 * Copie secrets.h.example para secrets.h para Wi-Fi/MQTT reais.
 */
#if __has_include("secrets.h")
#include "secrets.h"
#else
#define WIFI_SSID ""
#define WIFI_PASSWORD ""
#define MQTT_HOST ""
#define MQTT_PORT 8883
#define MQTT_USER ""
#define MQTT_PASSWORD ""
#endif

#define MQTT_MAX_PACKET_SIZE 512

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

/** SPIFFS: 1 em ESP32 físico para log local; no Wokwi Web o sistema de arquivos é volátil. */
#ifndef USE_SPIFFS
#define USE_SPIFFS 0
#endif
#if USE_SPIFFS
#include <SPIFFS.h>
#endif

// --- Pinos (devem coincidir com fase3/wokwi/diagram.json) ---
static const int PIN_DHT = 15;
static const int PIN_PULSE_BTN = 27;
static const int PIN_WIFI_BTN = 26;
static const uint8_t DHT_TYPE = DHT22;

/** Capacidade da fila (amostras). Ex.: 32 × 4 s ≈ 2 min offline. */
static const size_t QUEUE_CAP = 32;
static const unsigned long SAMPLE_INTERVAL_MS = 4000;

static const float ALERT_TEMP_C = 38.0f;
static const uint16_t ALERT_BPM = 120;

static const char *const DEVICE_ID = "esp32_01";
static const char *const MQTT_TOPIC_BASE = "cardioia";

#if USE_SPIFFS
static const char *const SPIFFS_LOG_PATH = "/vitals.csv";
#endif

DHT dht(PIN_DHT, DHT_TYPE);
WiFiClientSecure wifiClient;
PubSubClient mqtt(wifiClient);

/** Sem SSID → Wi-Fi simulada (botão alterna online/offline); MQTT só se MQTT_HOST em secrets.h. */
static const bool kSimulatedWifi = (WIFI_SSID[0] == '\0');

struct VitalSample {
  uint32_t ts_ms;
  float temp;
  float hum;
  uint16_t bpm;
  uint8_t alert;
  uint8_t backlog;
};

static VitalSample g_queue[QUEUE_CAP];
static size_t g_qHead = 0;
static size_t g_qCount = 0;

static bool g_netUp = false;
static int g_lastWifiBtn = HIGH;
static int g_lastPulseBtn = HIGH;
static unsigned long g_lastPulseDebounce = 0;

static unsigned long g_minuteEpochMs = 0;
static uint32_t g_pulseInMinute = 0;
static unsigned long g_lastSampleMs = 0;

static String topicVitals() {
  return String(MQTT_TOPIC_BASE) + "/" + DEVICE_ID + "/vitals";
}

static void queueDropOldest() {
  if (g_qCount == 0) return;
  g_qHead = (g_qHead + 1) % QUEUE_CAP;
  g_qCount--;
  Serial.println(F("DROP oldest (FIFO, queue full)"));
}

static void enqueueSample(const VitalSample &s) {
  if (g_qCount >= QUEUE_CAP) {
    queueDropOldest();
  }
  const size_t tail = (g_qHead + g_qCount) % QUEUE_CAP;
  g_queue[tail] = s;
  g_qCount++;
  Serial.println(F("ENQUEUE"));

#if USE_SPIFFS
  File f = SPIFFS.open(SPIFFS_LOG_PATH, FILE_APPEND);
  if (f) {
    f.printf("%lu,%.2f,%.2f,%u,%u\n", (unsigned long)s.ts_ms, s.temp, s.hum,
             (unsigned)s.bpm, (unsigned)s.alert);
    f.close();
  }
#endif
}

static bool buildJson(const VitalSample &s, char *buf, size_t bufLen) {
  StaticJsonDocument<192> doc;
  doc["ts"] = s.ts_ms;
  doc["temp"] = round(s.temp * 100.0f) / 100.0f;
  doc["hum"] = round(s.hum * 100.0f) / 100.0f;
  doc["bpm"] = s.bpm;
  doc["alert"] = s.alert;
  doc["backlog"] = s.backlog;
  const size_t n = serializeJson(doc, buf, bufLen);
  return n > 0 && n < bufLen;
}

static void connectWifiIfNeeded() {
  if (kSimulatedWifi) return;
  if (WiFi.status() == WL_CONNECTED) return;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print(F("WiFi.begin ssid="));
  Serial.println(WIFI_SSID);
}

static bool ensureMqttConnected() {
  if (!g_netUp) return false;
  if (MQTT_HOST[0] == '\0') return false;
  if (!kSimulatedWifi && WiFi.status() != WL_CONNECTED) return false;
  if (mqtt.connected()) return true;

  /** Protótipo: sem verificação de cadeia (em produção, carregar CA do broker). */
  wifiClient.setInsecure();

  const String clientId =
      String("cardioia-") + String((uint32_t)ESP.getEfuseMac(), HEX);

  bool ok = false;
  if (MQTT_USER[0] != '\0') {
    ok = mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD);
  } else {
    ok = mqtt.connect(clientId.c_str());
  }
  if (ok) {
    Serial.println(F("MQTT conectado"));
  } else {
    Serial.print(F("MQTT falhou, estado="));
    Serial.println(mqtt.state());
  }
  return ok;
}

/**
 * Drena a fila no modo simulado: imprime cada amostra em JSON via Serial.println
 * (equivalente didático ao "envio para a nuvem") e apaga a entrada da fila.
 * Atende explicitamente o enunciado da Parte 1: "Quando 'conectado', envie os
 * dados armazenados para a nuvem via Serial.println e apague o arquivo local".
 */
static void flushQueueViaSerial() {
  if (!g_netUp) return;
  if (g_qCount == 0) return;

  char payload[256];
  Serial.print(F("SIM CLOUD FLUSH amostras="));
  Serial.println((unsigned)g_qCount);

  while (g_qCount > 0) {
    VitalSample s = g_queue[g_qHead];
    s.backlog = (g_qCount > 1) ? 1 : 0;
    if (!buildJson(s, payload, sizeof(payload))) {
      Serial.println(F("JSON erro; abort flush simulado"));
      break;
    }
    Serial.print(F("SIM PUBLISH "));
    Serial.println(payload);
    g_qHead = (g_qHead + 1) % QUEUE_CAP;
    g_qCount--;
  }

  if (g_qCount == 0) {
    Serial.println(F("FLUSH fila vazia (simulado)"));
#if USE_SPIFFS
    if (SPIFFS.exists(SPIFFS_LOG_PATH)) {
      SPIFFS.remove(SPIFFS_LOG_PATH);
      Serial.println(F("SPIFFS log apagado após sync simulado"));
    }
#endif
  }
}

/**
 * Drena a fila publicando do mais antigo ao mais recente.
 * Para na primeira falha de publish para não perder amostras.
 */
static void flushQueueToCloud() {
  if (!g_netUp || MQTT_HOST[0] == '\0') return;
  if (!ensureMqttConnected()) return;

  char payload[256];
  const String topic = topicVitals();

  while (g_qCount > 0) {
    VitalSample s = g_queue[g_qHead];
    s.backlog = (g_qCount > 1) ? 1 : 0;
    if (!buildJson(s, payload, sizeof(payload))) {
      Serial.println(F("JSON erro; abort flush"));
      break;
    }
    if (mqtt.publish(topic.c_str(), payload, false)) {
      g_qHead = (g_qHead + 1) % QUEUE_CAP;
      g_qCount--;
      Serial.println(F("MQTT PUBLISH ok"));
    } else {
      Serial.println(F("MQTT PUBLISH falhou; retentativa depois"));
      break;
    }
  }

  if (g_qCount == 0) {
    Serial.println(F("FLUSH fila vazia"));
#if USE_SPIFFS
    if (SPIFFS.exists(SPIFFS_LOG_PATH)) {
      SPIFFS.remove(SPIFFS_LOG_PATH);
      Serial.println(F("SPIFFS log apagado após sync"));
    }
#endif
  }
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println(F("CardioIA Fase 3 — boot"));

  dht.begin();
  pinMode(PIN_PULSE_BTN, INPUT_PULLUP);
  pinMode(PIN_WIFI_BTN, INPUT_PULLUP);
  g_minuteEpochMs = millis();

#if USE_SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println(F("SPIFFS falha ao montar"));
  }
#endif

  if (!kSimulatedWifi) {
    connectWifiIfNeeded();
  }

  if (MQTT_HOST[0] != '\0') {
    mqtt.setServer(MQTT_HOST, (uint16_t)MQTT_PORT);
  }

  if (kSimulatedWifi) {
    Serial.println(F("Modo: Wi-Fi/MQTT simulados (preencha secrets.h para nuvem real)."));
    Serial.println(F("Botão 'WiFi' alterna online/offline para testar a fila."));
    Serial.println(F("Ao ficar ONLINE, a fila é drenada via Serial.println (SIM PUBLISH)."));
    g_netUp = false;
  } else {
    Serial.println(F("Modo: Wi-Fi real + MQTT."));
  }
}

void loop() {
  mqtt.loop();

  if (kSimulatedWifi) {
    const int w = digitalRead(PIN_WIFI_BTN);
    if (w == LOW && g_lastWifiBtn == HIGH) {
      g_netUp = !g_netUp;
      Serial.println(g_netUp ? F("Rede simulada: ONLINE") : F("Rede simulada: OFFLINE"));
      if (g_netUp) {
        flushQueueViaSerial();
      }
    }
    g_lastWifiBtn = w;
  } else {
    if (WiFi.status() != WL_CONNECTED) {
      connectWifiIfNeeded();
      delay(200);
    }
    g_netUp = (WiFi.status() == WL_CONNECTED);
  }

  const int p = digitalRead(PIN_PULSE_BTN);
  if (p == LOW && g_lastPulseBtn == HIGH) {
    if (millis() - g_lastPulseDebounce > 40) {
      g_pulseInMinute++;
      g_lastPulseDebounce = millis();
    }
  }
  g_lastPulseBtn = p;

  if (millis() - g_minuteEpochMs >= 60000UL) {
    g_pulseInMinute = 0;
    g_minuteEpochMs = millis();
  }

  if (millis() - g_lastSampleMs < SAMPLE_INTERVAL_MS) {
    return;
  }
  g_lastSampleMs = millis();

  float tempC = dht.readTemperature();
  float hum = dht.readHumidity();
  if (isnan(tempC)) tempC = 36.5f;
  if (isnan(hum)) hum = 50.0f;

  const unsigned long elapsed = millis() - g_minuteEpochMs;
  uint16_t bpm = 0;
  if (elapsed > 200) {
    const unsigned long est = (g_pulseInMinute * 60000UL) / elapsed;
    bpm = (uint16_t)min(220UL, est);
  }

  const uint8_t alert =
      (tempC > ALERT_TEMP_C || bpm > ALERT_BPM) ? 1 : 0;

  VitalSample s;
  s.ts_ms = millis();
  s.temp = tempC;
  s.hum = hum;
  s.bpm = bpm;
  s.alert = alert;
  s.backlog = 0;

  enqueueSample(s);

  if (g_netUp) {
    if (MQTT_HOST[0] != '\0') {
      flushQueueToCloud();
    } else {
      flushQueueViaSerial();
    }
  }
}
