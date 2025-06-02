import json
import time
import paho.mqtt.client as mqtt
from utils.crypto_utils import load_private_key, sign_message
from config import MQTT_BROKER, MQTT_PORT, PRIVATE_KEY_DIR
import sys

if len(sys.argv) < 2:
    print("Usage: python device_sim.py <device_id>")
    sys.exit(1)

DEVICE_ID = sys.argv[1]
PRIVATE_KEY_PATH = f"{PRIVATE_KEY_DIR}/{DEVICE_ID}_private.pem"
TOPIC = f"iot/{DEVICE_ID}/data"

def create_signed_payload(private_key):
    message = {
        "device_id": DEVICE_ID,
        "timestamp": int(time.time()),
        "data": {
            "temperature": 25.0 + (hash(DEVICE_ID) % 10),
            "humidity": 50 + (hash(DEVICE_ID) % 20)
        }
    }
    msg_bytes = json.dumps(message).encode()
    signature = sign_message(private_key, msg_bytes)
    return {
        "payload": message,
        "signature": signature.hex()
    }

def main():
    print(f"📡 {DEVICE_ID} simulator started.")
    private_key = load_private_key(PRIVATE_KEY_PATH)
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    while True:
        signed_payload = create_signed_payload(private_key)
        message_json = json.dumps(signed_payload)
        client.publish(TOPIC, message_json)
        print(f"✅ Sent signed message from {DEVICE_ID} to {TOPIC}")
        time.sleep(5)

if __name__ == "__main__":
    main()
