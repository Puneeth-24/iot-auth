import json
import os
import paho.mqtt.client as mqtt
import threading
import time
from utils.crypto_utils import verify_signature, deserialize_public_key
from config import REGISTRY_PATH, MQTT_BROKER, MQTT_PORT, TOPIC_PATTERN
import functools

print = functools.partial(print, flush=True)  

device_registry = {}
public_keys = {}

def load_registry():
    global device_registry, public_keys
    if not os.path.exists(REGISTRY_PATH):
        print(f"Registry file {REGISTRY_PATH} not found.")
        device_registry = {}
        public_keys = {}
        return

    with open(REGISTRY_PATH, "r") as f:
        try:
            device_registry = json.load(f)
        except json.JSONDecodeError:
            print("Failed to decode registry JSON.")
            device_registry = {}

    public_keys = {
        device_id: deserialize_public_key(info["public_key"])
        for device_id, info in device_registry.items()
    }
    print(f"Reloaded device registry: {len(public_keys)} devices loaded.")

def reload_registry_periodically(interval=60):
    while True:
        load_registry()
        time.sleep(interval)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(TOPIC_PATTERN)
    print(f"Subscribed to topic pattern: {TOPIC_PATTERN}")

def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        payload = data["payload"]
        signature = bytes.fromhex(data["signature"])
        device_id = payload.get("device_id")

        if not device_id:
            print("Missing device_id in payload.")
            return

        if device_id not in public_keys:
            print(f"Unregistered device: {device_id}")
            return

        message_bytes = json.dumps(payload).encode()
        valid = verify_signature(public_keys[device_id], message_bytes, signature)

        if valid:
            print(f"Valid signature from {device_id}: {payload}")
        else:
            print(f"Invalid signature from {device_id}: {payload}")

    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    load_registry()
    threading.Thread(target=reload_registry_periodically, daemon=True).start()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
