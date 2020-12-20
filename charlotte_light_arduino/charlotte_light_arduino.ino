/*
  This sketch has code based on the following projects:
  
  * AWS IoT WiFi example (https://create.arduino.cc/projecthub/132016/securely-connecting-an-arduino-mkr-wifi-1010-to-aws-iot-core-a9f365)
  * ArduinoJson example
  * Adafruit NeoPixel strandtest example (https://adafruit.github.io/Adafruit_NeoPixel/html/index.html)

  This code is offered as-is and you are responsibe for any security issues or cost incurred.

  This code is in the public domain.
*/

#include <ArduinoBearSSL.h>
#include <ArduinoECCX08.h>
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h> // change to #include <WiFi101.h> for MKR1000
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#include "arduino_secrets.h"

/////// Enter your sensitive data in arduino_secrets.h
const char ssid[]        = SECRET_SSID;
const char pass[]        = SECRET_PASS;
const char broker[]      = SECRET_BROKER;
const char* certificate  = SECRET_CERTIFICATE;

#define PIXEL_PIN  6
#define NUMPIXELS 24

WiFiClient    wifiClient;            // Used for the TCP socket connection
BearSSLClient sslClient(wifiClient); // Used for SSL/TLS connection, integrates with ECC508
MqttClient    mqttClient(sslClient);

unsigned long last_publish_millis = 0;
unsigned long last_animate_millis = 0;
unsigned long last_poll_millis = 0;
unsigned long connect_retry = 0;

unsigned short brightness = 255;
unsigned int hue = 0;
unsigned short saturation = 0;
bool power = false;
byte mode = 1;
unsigned int frame_number = 0;
short frame_direction = 1;

Adafruit_NeoPixel pixels(NUMPIXELS, PIXEL_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200);
  //while (!Serial);

  if (!ECCX08.begin()) {
    Serial.println(F("No ECCX08 present!"));
    while (1);
  }

  pixels.begin();

  ArduinoBearSSL.onGetTime(getTime);

  sslClient.setEccSlot(0, certificate);

  mqttClient.onMessage(onMessageReceived);
}

void loop() {
  if (millis() - last_poll_millis > (100)) {
    last_poll_millis = millis();
    communicate();
  }

  // publish a message roughly every 5 minutes.
  if (millis() - last_publish_millis > (5 * 60 * 1000)) {
    last_publish_millis = millis();

    publishMessage();
  }

  animate();
}

void communicate() {
  if (millis() < connect_retry) {
    return;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (WiFi.status() != WL_CONNECTED) {
    connect_retry = millis() + 5000;
    Serial.println(F("Need to retry wifi"));
    return;
  }
  
  if(getTime() == 0) {
    connect_retry = millis() + 1000;
    Serial.println(F("Need to retry ntp server"));
    return;
  }
  
  if (!mqttClient.connected()) {
    connectMQTT();
  }

  if (!mqttClient.connected()) {
    connect_retry = millis() + 5000;
    Serial.println(F("Need to retry mqtt server"));
    return;
  }

  mqttClient.poll();
}

unsigned long getTime() {
  return WiFi.getTime();
}

void connectWiFi() {
  Serial.print(F("Attempting to connect to SSID: "));
  Serial.print(ssid);

  if (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.println(F("You're connected to the network"));
  } else {
    Serial.println(F("WiFi connect failed"));
  }
}

void connectMQTT() {
  Serial.print(F("Attempting to MQTT broker: "));
  Serial.println(broker);

  if (mqttClient.connect(broker, 8883)) {
    Serial.println(F("You're connected to the MQTT broker"));
    mqttClient.subscribe("device/charlotte-light-01/control");
  } else {
    Serial.print(F("MQTT connection failed! Error code = "));
    Serial.println(mqttClient.connectError());
  }
}

void publishMessage() {
  Serial.println(F("Publishing message"));

  StaticJsonDocument<200> status_update;
  
  status_update["Power"] = power;
  
  status_update["Hue"] = hue;
  status_update["Saturation"] = saturation;
  status_update["Brightness"] = brightness;

  status_update["Mode"] = mode;

  mqttClient.beginMessage("device/charlotte-light-01/status");
  serializeJson(status_update, mqttClient);
  mqttClient.endMessage();
}

void onMessageReceived(int messageSize) {
  // we received a message, print out the topic and contents
  Serial.print(F("Received a message with topic "));
  Serial.print(mqttClient.messageTopic());
  Serial.print(F(", length "));
  Serial.print(messageSize);

  StaticJsonDocument<128> doc;
  DeserializationError error = deserializeJson(doc, mqttClient);

  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.c_str());
    return;
  }

  if (doc.containsKey("powerState")){
    power = (doc["powerState"] == "ON");
  }

  if (doc.containsKey("SetColor")){
    hue = doc["SetColor"]["hue"].as<int>();
    saturation = doc["SetColor"]["saturation"].as<int>();

    // It is a nicer effect to change color and maintain existing brightness
    // brightness = doc["SetColor"]["brightness"].as<int>();
  }

  if (doc.containsKey("SetMode")){
    mode = doc["SetMode"].as<int>();
  }

  if (doc.containsKey("SetBrightness")){
    brightness = doc["SetBrightness"].as<int>();
  }

  setLight();
  
  Serial.println("Light Updated");
}

void setLight() {
  Serial.println(power);
  Serial.println(mode);
  
  if (power == 0) {
    pixels.clear();
    pixels.show();
    return;
  }

  if (mode != 1) {
    frame_number = 0;
    return;
  }

  uint32_t rgbcolor = pixels.gamma32(pixels.ColorHSV(hue, saturation, brightness));
  
  pixels.fill(rgbcolor);
  pixels.show();
  Serial.println('Light changed');
}

void animate() {
  if (power == 0) {
    return;
  }
  
  if (mode == 2) {
    if (millis() - last_animate_millis > 100) {
      last_animate_millis = millis();
      knightrider();
      frame_number += frame_direction;
    }
  } else if (mode == 3) {
    if (millis() - last_animate_millis > 100) {
      last_animate_millis = millis();
      starburst();
    }
  } else if (mode == 4) {
    if (millis() - last_animate_millis > 20) {
      last_animate_millis = millis();
      slowRainbow();
      frame_number++;
    }
  } else if (mode == 5) {
    if (millis() - last_animate_millis > 50) {
      last_animate_millis = millis();
      fastRainbow();
      frame_number++;
    }
  } else if (mode == 6) {
    if (millis() - last_animate_millis > 100) {
      last_animate_millis = millis();
      emergenyFlash();
      frame_number++;
    }
  }
}

void starburst() {
  pixels.clear();
  pixels.setPixelColor(random(0, NUMPIXELS), brightness / 2, brightness / 2, brightness / 2);
  pixels.setPixelColor(random(0, NUMPIXELS), brightness, brightness, brightness);
  pixels.setPixelColor(random(0, NUMPIXELS), brightness / 2, brightness / 2, brightness / 2);
  pixels.show();
}

void emergenyFlash() {
  unsigned int half = NUMPIXELS / 2;
  uint32_t color1;
  uint32_t color2;

  Serial.println(frame_number % 2);

  if (frame_number % 2 == 0) {
    Serial.println("Red");
    color1 = pixels.Color(brightness, 0, 0);
    color2 = pixels.Color(0, 0, brightness);
  } else {
    Serial.println("Blue");
    color1 = pixels.Color(0, 0, brightness);
    color2 = pixels.Color(brightness, 0, 0);
  }
  pixels.fill(color1, 0);
  pixels.fill(color2, half);
  pixels.show();
}

void knightrider() {
  if (frame_number >= NUMPIXELS) {
    frame_direction = -frame_direction;
  }
  pixels.clear();
  if (frame_number > 0){
    pixels.setPixelColor(frame_number - 1, brightness/4, 0, 0);
  }
  pixels.setPixelColor(frame_number, brightness, 0, 0);
  if (frame_number < (NUMPIXELS - 1)) {
    pixels.setPixelColor(frame_number + 1, brightness/4, 0, 0);
  }
  pixels.show();
}

void slowRainbow() {
  unsigned int first_pixel_hue = frame_number * 256;
  for(int i = 0; i < NUMPIXELS; i++) {
    int pixel_hue = first_pixel_hue + (i * 65536L / NUMPIXELS);
    pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(pixel_hue, 255, brightness)));
  }
  pixels.show();
}

void fastRainbow() {
  int first_pixel = frame_number % 3;
  int first_pixel_hue = (frame_number / 3) * (65536L / 90);
  pixels.clear();
  for(int i = first_pixel; i < NUMPIXELS; i += 3) {
    int hue = first_pixel_hue + i * (65536L / NUMPIXELS);
    pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(hue, 255, brightness)));
  }
  pixels.show();
}
