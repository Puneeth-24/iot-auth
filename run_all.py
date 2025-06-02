import os
import subprocess
import sys
import time
import threading
from identity_registry import register_device
from broker.subscriber import main as subscriber_main
from config import MQTT_BROKER, MQTT_PORT

DEVICES = ["device1", "device2"]  
import platform

def start_mosquitto():
    if platform.system() == "Windows":
  
        print("⚠️ Detected Windows OS: please start Mosquitto manually before running this script.")
        return True  
    else:
        try:
            result = subprocess.run(["systemctl", "is-active", "--quiet", "mosquitto"])
            if result.returncode == 0:
                print("✅ Mosquitto broker is already running.")
                return True

            print("🔄 Starting mosquitto broker...")
            result = subprocess.run(["sudo", "systemctl", "start", "mosquitto"])
            if result.returncode == 0:
                print("✅ Mosquitto broker started.")
                return True
            else:
                print("❌ Failed to start mosquitto. Please start it manually.")
                return False
        except Exception as e:
            print(f"⚠️ Error checking/starting mosquitto: {e}")
            return False

def register_devices():
    print("🔐 Registering devices...")
    for device_id in DEVICES:
        success, msg = register_device(device_id)
        print(f"{'✅' if success else '❌'} {device_id}: {msg}")

def start_subscriber():
    print("📡 Starting subscriber...")
    thread = threading.Thread(target=subscriber_main, daemon=True)
    thread.start()
    return thread

def start_device_simulators():
    print("📡 Starting device simulators...")
    processes = []
    for device_id in DEVICES:
        cmd = [sys.executable, "device_sim.py", device_id]
        proc = subprocess.Popen(cmd)
        print(f"▶️ Started device simulator for {device_id} (pid {proc.pid})")
        processes.append(proc)
    return processes

def main():
    if not start_mosquitto():
        print("Please start Mosquitto broker manually and rerun.")
        return

    register_devices()
    sub_thread = start_subscriber()
    simulators = start_device_simulators()

    print("\n🚀 All systems started. Press Ctrl+C to exit.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for proc in simulators:
            proc.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()
