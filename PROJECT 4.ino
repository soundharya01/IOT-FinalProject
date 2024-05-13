
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include "Adafruit_SHT4x.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include <WiFi.h>
#include <PubSubClient.h>

/*********************WiFi and MQTT Broker****************************/
const char* ssid = "Immanuel";
const char* password = "01234567";
const char* mqtt_server = "broker.netpie.io";
const int mqtt_port = 1883;
const char* mqtt_Client = "dde04b52-af3b-4816-a9b2-9a8eeea8255e";//ClientID
const char* mqtt_username = "ejmzuaqQtHLG7dT6hPNd8XW58YU5m43D";//Token
const char* mqtt_password = "pxJHvR4aytW9PEnPn7PF9YshTHtvpGMh";//Secret
char msg[200];
WiFiClient espClient;
PubSubClient client(espClient);
/*******************Sensor**********************/
Adafruit_BMP280 bmp; // Define BMP280 Sensor
Adafruit_SHT4x sht4 = Adafruit_SHT4x(); //Define SHT4x Sensor
sensors_event_t humidity, temp;

/**************Structure of Queue**********/
// Define a struct
struct dataRead {
  float SHT4xTemperature;
  float SHT4xHumidity;
  float BMP280Pressure;
  float BMP280Temperature;
};
QueueHandle_t Queue; //Define QueueHandle_t

void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void controlActuators(float temperature, float humidity, float pressure);
// Define COOLING_SYSTEM_PIN with the actual pin number
const int COOLING_SYSTEM_PIN = 12; // Example pin number

void setup() {
  Serial.begin(9600);
  Wire.begin(41, 40);
  if (bmp.begin(0x76)) { // prepare BMP280 sensor
    Serial.println("BMP280 sensor ready");
  }
  if ( sht4.begin()) { // prepare sht4 sensor
    Serial.println("SHT4x sensor ready");
  }
    Queue = xQueueCreate(100,sizeof(struct dataRead));

    if (Queue == NULL) {
      Serial.println("Error creating the queue");
    }
    //Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi ");
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("\nWiFi Connected");
    //connect client to MQTT Broker
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);
    if(!client.connected()){
      Serial.println("Cucumber's not connected to MQTT Broker");
      client.connect(mqtt_Client, mqtt_username, mqtt_password);
    }
    // Create task that consumes the queue.
    xTaskCreate(sendToQueue, "Sender", 2048, NULL, 2, NULL);
    xTaskCreate(receiveFromQueue, "Receiver", 2048, NULL, 1, NULL);
    
    pinMode(COOLING_SYSTEM_PIN, OUTPUT); // Initialize COOLING_SYSTEM_PIN as output
}

void loop() {
  if (!client.connected()) {
    reconnect(); // Reconnect to MQTT if not connected
  }
  client.loop();
}

// Task that get data and sends it to the queue
void sendToQueue(void *parameter) {
  while (1) {
    // Read data from sensor
    struct dataRead currentData;
    sht4.getEvent(&humidity, &temp);
    currentData.SHT4xTemperature =temp.temperature;
    currentData.SHT4xHumidity = humidity.relative_humidity;
    currentData.BMP280Temperature = bmp.readTemperature();
    currentData.BMP280Pressure = bmp.readPressure()/1000;//kPa
    // Send data to the queue
    if (xQueueSend(Queue, &currentData, portMAX_DELAY) != pdPASS) {
      Serial.println("Failed to send data to the queue");
    }
    // delay for 1 second
     vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

// Task data from the queue
void receiveFromQueue(void *parameter) {
  while (1) {
    // Receive data from the queue
    struct dataRead currentData;
    if (xQueueReceive(Queue, &currentData, portMAX_DELAY) == pdPASS) {
      // Serial.println("Temp data: "+String(currentData.SHT4xTemperature)+" °C");
      // Serial.println("AirTemp data: "+String(currentData.BMP280Temperature) + " °C");
      // Serial.println("AirPressure data: "+String(currentData.BMP280Pressure)+" kPa");
      // Serial.println("Humidity data: "+String(currentData.SHT4xHumidity)+ " %(RH)");
    }
    // Process the received data
    if (!client.connected()) {
    reconnect();
    }
    client.loop();
    String data = "{\"data\": {\"SHT4xTemperature\":"+String(currentData.SHT4xTemperature)+",\"SHT4xHumidity\":"+ String(currentData.SHT4xHumidity)+",\"BMP280Temperature\":"+ String(currentData.BMP280Temperature)+",\"BMP280Pressure\":"+ String(currentData.BMP280Pressure) + "}}";
    Serial.println(data);
    data.toCharArray(msg, (data.length() + 1));
    client.publish("@shadow/data/update", msg);
     // Control actuators based on sensor data
      controlActuators(currentData.SHT4xTemperature, currentData.SHT4xHumidity, currentData.BMP280Pressure);
    }
  }

//Reconnect to MQTT Function
void reconnect() {
  while (!client.connected()) {
    Serial.print("Sensor MQTT connection…");
    if (client.connect(mqtt_Client, mqtt_username, mqtt_password)) {
      Serial.println("connected");
    }
    else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println("try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String command = String((char*)payload); // Convert payload to a String
  if (command.equals("activate")) {
    digitalWrite(COOLING_SYSTEM_PIN, HIGH); // Activate cooling system
  } else if (command.equals("deactivate")) {
    digitalWrite(COOLING_SYSTEM_PIN, LOW); // Deactivate cooling system
  }
}

void controlActuators(float temperature, float humidity, float pressure) {
  // Check conditions and control actuators based on sensor data
  if (temperature > 38 && humidity > 40) {
    digitalWrite(COOLING_SYSTEM_PIN, HIGH); // Activate cooling system
  } else {
    digitalWrite(COOLING_SYSTEM_PIN, LOW); // Deactivate cooling system
  }
}




