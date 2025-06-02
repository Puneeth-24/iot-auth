import time
import json
import paho.mqtt.client as mqtt
import random
import os
import threading
from utils.crypto_utils import sign_message, load_private_key_from_file

# MQTT configuration
BROKER = "localhost"
PORT = 1883
TOPIC = "device2/data"
START_TOPIC = "system/start_signal"

# Load private key for signing
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "credentials", "private_keys", "device2_private.pem")
private_key = load_private_key_from_file(PRIVATE_KEY_PATH)

# Initialize MQTT client
client = mqtt.Client(client_id="device2_sim", callback_api_version=2)

start_received_event = threading.Event()
stop_received_event = threading.Event()

def on_message(client, userdata, msg):
    payload = msg.payload.decode()

    if msg.topic == START_TOPIC:
        if payload == "start":
            if msg.retain == 1:
                print("[INFO] Ignored retained start signal.", flush=True)
                return
            if not start_received_event.is_set():
                print("[INFO] Start signal received. Beginning data transmission...", flush=True)
                start_received_event.set()

        elif payload == "stop":
            print("[INFO] Stop signal received. Halting transmission...", flush=True)
            stop_received_event.set()

def publish_data():
    payload = {
        "device_id": "device2",
        "light_intensity": round(random.uniform(100, 800), 2), 
        "status": random.choice(["ON", "OFF"]),
        "timestamp": int(time.time())
    }

    message_bytes = json.dumps(payload).encode()
    signature = sign_message(private_key, message_bytes).hex()

    signed_message = {
        "payload": payload,
        "signature": signature
    }

    client.publish(TOPIC, json.dumps(signed_message))
    print(f"=>Sent: {signed_message}", flush=True)

def main():
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(START_TOPIC)
    client.loop_start()

    print("[WAIT] Waiting for start signal...", flush=True)
    
    while not start_received_event.is_set() and not stop_received_event.is_set():
        time.sleep(0.5)

    if stop_received_event.is_set():
        print("[INFO] Stop signal received before start. Exiting.", flush=True)
        client.loop_stop()
        client.disconnect()
        return

    print("[OK] Start signal confirmed. Publishing will now begin.", flush=True)

    try:
        while not stop_received_event.is_set():
            publish_data()
            time.sleep(3)
    except KeyboardInterrupt:
        print("Device2 simulator stopped by user.", flush=True)
    finally:
        print("=> Shutting down Device2 simulator.", flush=True)
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
