import os
import json
import sys
from utils.crypto_utils import generate_keys, serialize_public_key, serialize_private_key
from config import REGISTRY_PATH, PRIVATE_KEY_DIR, PUBLIC_KEY_DIR

def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {}
    with open(REGISTRY_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def register_device(device_id):
    if not device_id.strip():
        return False, "Device ID cannot be empty"

    registry = load_registry()
    if device_id in registry:
        return False, "Device already registered"

    private_key, public_key = generate_keys()
    priv_pem = serialize_private_key(private_key)
    pub_pem = serialize_public_key(public_key)

    registry[device_id] = {"public_key": pub_pem}

    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    os.makedirs(PRIVATE_KEY_DIR, exist_ok=True)
    os.makedirs(PUBLIC_KEY_DIR, exist_ok=True)

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    priv_path = os.path.join(PRIVATE_KEY_DIR, f"{device_id}_private.pem")
    pub_path = os.path.join(PUBLIC_KEY_DIR, f"{device_id}_public_key.pem")

    with open(priv_path, "w") as f:
        f.write(priv_pem)
    with open(pub_path, "w") as f:
        f.write(pub_pem)

    return True, f"Device '{device_id}' registered."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python identity_registry.py <device_id>")
        sys.exit(1)

    device_id = sys.argv[1]
    success, message = register_device(device_id)
    if success:
        print("✅", message)
    else:
        print("❌", message)
