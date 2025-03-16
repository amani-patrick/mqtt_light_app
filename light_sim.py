import paho.mqtt.client as mqtt
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

# MQTT broker details
BROKER_ADDRESS = "broker.emqx.io"
PORT_NUMBER = 1883
CONTROL_TOPIC = "/student_group/light_control"

# Callback triggered upon connecting to the MQTT broker
def handle_connection(client, userdata, flags, rc):
    print("Successfully connected to MQTT broker")
    client.subscribe(CONTROL_TOPIC)
    print(f"Subscribed to topic: {CONTROL_TOPIC}")

# Callback triggered when a message is received
def handle_message(client, userdata, msg):
    command = msg.payload.decode()
    if command == "ON":
        print("💡 Light is TURNED ON")
    elif command == "OFF":
        print("💡 Light is TURNED OFF")

def start_mqtt_client():
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = handle_connection
    mqtt_client.on_message = handle_message
    print(f"Attempting connection to broker {BROKER_ADDRESS}...")
    mqtt_client.connect(BROKER_ADDRESS, PORT_NUMBER, 60)
    mqtt_client.loop_forever()
mqtt_client = None

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/send_command'):
            command = self.path.split('=')[1]
            mqtt_client.publish(CONTROL_TOPIC, command)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Command sent')
        else:
            super().do_GET()

def start_http_server():
    server_address = ('', 8800)
    httpd = HTTPServer(server_address, RequestHandler)
    print("HTTP server running on port 8800")
    httpd.serve_forever()

if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=start_mqtt_client)
    mqtt_thread.start()

    try:
        start_http_server()
    except KeyboardInterrupt:
        print("\nShutting down HTTP server...")