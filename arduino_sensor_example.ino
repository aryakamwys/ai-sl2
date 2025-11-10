/*
 * Smart AQI Sensor - Arduino/ESP32 Example
 * 
 * Contoh code untuk membaca sensor kualitas udara dan mengirim data
 * ke sistem Smart AQI melalui berbagai metode.
 * 
 * Sensor yang didukung:
 * - PMS5003/PMS7003 (PM2.5, PM10)
 * - MQ135 (Air Quality)
 * - DHT22 (Temperature, Humidity)
 * 
 * Metode pengiriman:
 * 1. Serial (USB)
 * 2. WiFi HTTP POST
 * 3. WiFi MQTT
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ===== KONFIGURASI =====
#define WIFI_SSID "Your_WiFi_SSID"
#define WIFI_PASSWORD "Your_WiFi_Password"

// MQTT Configuration
#define MQTT_SERVER "broker.hivemq.com"
#define MQTT_PORT 1883
#define MQTT_TOPIC "sensor/aqi/jakarta"

// HTTP API Configuration
#define API_ENDPOINT "http://your-server.com/api/aqi"

// Pin Configuration
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define MQ135_PIN 34

// Sensor Objects
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Variables
float temperature = 0;
float humidity = 0;
int aqi = 0;
float pm25 = 0;
float pm10 = 0;

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Smart AQI Sensor Starting ===");
  
  // Initialize sensors
  dht.begin();
  pinMode(MQ135_PIN, INPUT);
  
  // Connect to WiFi
  connectWiFi();
  
  // Setup MQTT
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  
  Serial.println("Setup complete!");
}

// ===== MAIN LOOP =====
void loop() {
  // Ensure WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  
  // Ensure MQTT connection
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();
  
  // Read sensors
  readSensors();
  
  // Calculate AQI
  calculateAQI();
  
  // Send data via Serial
  sendSerialData();
  
  // Send data via MQTT
  sendMQTTData();
  
  // Send data via HTTP (optional)
  // sendHTTPData();
  
  // Display on Serial Monitor
  displayData();
  
  // Wait before next reading
  delay(30000); // 30 seconds
}

// ===== WiFi CONNECTION =====
void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

// ===== MQTT CONNECTION =====
void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT...");
    
    String clientId = "ESP32-AQI-" + String(random(0xffff), HEX);
    
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming MQTT messages if needed
}

// ===== READ SENSORS =====
void readSensors() {
  // Read DHT22
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  
  // Check if reads failed
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    temperature = 0;
    humidity = 0;
  }
  
  // Read MQ135 (analog value)
  int mq135Value = analogRead(MQ135_PIN);
  
  // Read PMS5003 (if connected via Serial2)
  // readPMS5003();
  
  // Simulate PM2.5 and PM10 values for demo
  // Replace with actual sensor reading
  pm25 = map(mq135Value, 0, 4095, 0, 100) / 2.0;
  pm10 = pm25 * 1.8;
}

// ===== CALCULATE AQI =====
void calculateAQI() {
  // Simplified AQI calculation based on PM2.5
  // Using EPA's AQI breakpoints
  
  if (pm25 <= 12.0) {
    aqi = map(pm25 * 10, 0, 120, 0, 50);
  } else if (pm25 <= 35.4) {
    aqi = map(pm25 * 10, 121, 354, 51, 100);
  } else if (pm25 <= 55.4) {
    aqi = map(pm25 * 10, 355, 554, 101, 150);
  } else if (pm25 <= 150.4) {
    aqi = map(pm25 * 10, 555, 1504, 151, 200);
  } else if (pm25 <= 250.4) {
    aqi = map(pm25 * 10, 1505, 2504, 201, 300);
  } else {
    aqi = map(pm25 * 10, 2505, 5000, 301, 500);
  }
  
  // Constrain to valid range
  aqi = constrain(aqi, 0, 500);
}

// ===== SEND DATA VIA SERIAL =====
void sendSerialData() {
  // JSON format untuk mudah di-parse
  StaticJsonDocument<256> doc;
  
  doc["device_id"] = "AQI-SENSOR-001";
  doc["location"] = "Jakarta";
  doc["timestamp"] = millis();
  doc["aqi"] = aqi;
  doc["pm25"] = pm25;
  doc["pm10"] = pm10;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  
  serializeJson(doc, Serial);
  Serial.println();
}

// ===== SEND DATA VIA MQTT =====
void sendMQTTData() {
  if (!mqttClient.connected()) {
    return;
  }
  
  StaticJsonDocument<256> doc;
  
  doc["device_id"] = "AQI-SENSOR-001";
  doc["location"] = "Jakarta";
  doc["aqi"] = aqi;
  doc["pm25"] = pm25;
  doc["pm10"] = pm10;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  if (mqttClient.publish(MQTT_TOPIC, buffer)) {
    Serial.println("MQTT data sent successfully");
  } else {
    Serial.println("MQTT send failed");
  }
}

// ===== SEND DATA VIA HTTP =====
void sendHTTPData() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  http.begin(API_ENDPOINT);
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<256> doc;
  doc["device_id"] = "AQI-SENSOR-001";
  doc["location"] = "Jakarta";
  doc["aqi"] = aqi;
  doc["pm25"] = pm25;
  doc["pm10"] = pm10;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    String response = http.getString();
    Serial.println(response);
  } else {
    Serial.print("HTTP Error code: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}

// ===== DISPLAY DATA =====
void displayData() {
  Serial.println("\n===== Sensor Readings =====");
  Serial.print("AQI: ");
  Serial.println(aqi);
  Serial.print("PM2.5: ");
  Serial.print(pm25);
  Serial.println(" μg/m³");
  Serial.print("PM10: ");
  Serial.print(pm10);
  Serial.println(" μg/m³");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  Serial.println("===========================\n");
}

// ===== READ PMS5003 SENSOR (Optional) =====
/*
void readPMS5003() {
  // PMS5003 mengirim data 32 byte
  // Format: START1(0x42) START2(0x4d) + 30 byte data
  
  if (Serial2.available() >= 32) {
    byte buffer[32];
    Serial2.readBytes(buffer, 32);
    
    // Check start bytes
    if (buffer[0] == 0x42 && buffer[1] == 0x4D) {
      // PM2.5 (ug/m3)
      pm25 = (buffer[12] << 8) | buffer[13];
      
      // PM10 (ug/m3)
      pm10 = (buffer[14] << 8) | buffer[15];
    }
  }
}
*/
