// ESP32 Web Server Example
// Hardware: ESP32 Dev Module
// Connect ESP32 to Wi-Fi network (modify SSID and PASSWORD)

#include <WiFi.h>
#include <WebServer.h>

// Wi-Fi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// Create a WebServer object on port 80
WebServer server(80);

// HTML page to serve
const char htmlPage[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head><title>ESP32 Web Server</title></head>
<body>
<h1>Hello from ESP32!</h1>
<p>The current millis: %d</p>
</body>
</html>
)rawliteral";

void handleRoot() {
  char buffer[256];
  snprintf(buffer, sizeof(buffer), htmlPage, millis());
  server.send(200, "text/html", buffer);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.println();
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());

  // Define request handler
  server.on("/", handleRoot);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient(); // Process incoming client requests
}
