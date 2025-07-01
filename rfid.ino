#include <ESP8266WiFi.h>     // For NodeMCU
#include <ESP8266HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// Pin Definitions
#define SS_PIN D8
#define RST_PIN D0

// WiFi and Server Details
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://(replace it by ipv4 address of your local system):8000/access"; // Your FastAPI server IP + endpoint

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
}

void loop() {
  // Look for new cards
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Read UID
  String uidString = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uidString += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    uidString += String(mfrc522.uid.uidByte[i], HEX);
  }
  uidString.toUpperCase();
  Serial.println("Scanned UID: " + uidString);

  // Send UID to Server
  sendUidToServer(uidString);

  delay(1500); // To avoid multiple reads
}

void sendUidToServer(String uid) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client; // 🔥 Create a WiFiClient instance
    HTTPClient http;
    http.begin(client, serverUrl); // 🛠️ Pass client and serverUrl both now
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{\"rfid_uid\":\"" + uid + "\"}";
    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      Serial.println("POST Response code: " + String(httpResponseCode));
      String response = http.getString();
      Serial.println("Server says: " + response);
    } else {
      Serial.println("Error in POST: " + String(http.errorToString(httpResponseCode).c_str()));
    }

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}
