import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import platform
import sys
import os
from utils.system_utils import check_mosquitto_running
import time
import paho.mqtt.publish as publish

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BROKER_CONF = os.path.join(BASE_DIR, "broker", "mosquitto.conf")
DEVICE_SCRIPTS = {
    "device1": os.path.join(BASE_DIR, "devices", "device1_sim.py"),
    "device2": os.path.join(BASE_DIR, "devices", "device2_sim.py"),
    "device3": os.path.join(BASE_DIR, "devices", "device3_sim.py"),
}
SUBSCRIBER_SCRIPT = os.path.join(BASE_DIR, "broker", "subscriber.py")


class IoTManagerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IoT MQTT Manager")
        self.geometry("700x600")

        self.device_processes = {}
        self.subscriber_process = None

        self.broker_status_var = tk.StringVar(value="Broker status: Unknown")
        self.create_widgets()
        self.start_broker_status_monitor()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_broker_status(self):
        status = "Running" if check_mosquitto_running() else "Not Running"
        self.after(0, lambda: self.broker_status_var.set(f"Broker status: {status}"))

    def start_broker_status_monitor(self):
        def monitor():
            while True:
                self.update_broker_status()
                time.sleep(5)
        threading.Thread(target=monitor, daemon=True).start()

    def send_start_signal(self):
        try:
            publish.single("system/start_signal", payload="start", qos=1, retain=True, hostname="localhost", port=1883)
            self.log("[INFO] Start signal sent.")
        except Exception as e:
            self.log(f"[ERROR] Failed to send start signal: {e}")

    def send_stop_signal(self):
        try:
            publish.single("system/start_signal", payload="stop", qos=1, retain=False, hostname="localhost", port=1883)
            self.log("[INFO] Stop signal sent.")
        except Exception as e:
            self.log(f"[ERROR] Failed to send stop signal: {e}")

    def create_widgets(self):
        tk.Label(self, textvariable=self.broker_status_var, font=("Arial", 14)).pack(pady=10)

        broker_frame = tk.Frame(self)
        broker_frame.pack(pady=5)

        tk.Button(broker_frame, text="Check Broker Status", command=self.check_broker_status).pack(side=tk.LEFT, padx=5)
        tk.Button(broker_frame, text="Start Broker", command=self.start_broker).pack(side=tk.LEFT, padx=5)
        tk.Button(broker_frame, text="Stop Broker", command=self.stop_broker).pack(side=tk.LEFT, padx=5)
        tk.Button(broker_frame, text="Send Start Signal", command=self.send_start_signal).pack(side=tk.LEFT, padx=5)
        tk.Button(broker_frame, text="Send Stop Signal", command=self.send_stop_signal).pack(side=tk.LEFT, padx=5)

        devices_frame = tk.LabelFrame(self, text="Device Simulators")
        devices_frame.pack(fill=tk.X, padx=10, pady=10)

        for device in DEVICE_SCRIPTS.keys():
            tk.Button(devices_frame, text=f"Start {device}", command=lambda d=device: self.start_device(d)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(devices_frame, text=f"Stop {device}", command=lambda d=device: self.stop_device(d)).pack(side=tk.LEFT, padx=5, pady=5)

        subscriber_frame = tk.LabelFrame(self, text="Subscriber")
        subscriber_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        subscriber_btn_frame = tk.Frame(subscriber_frame)
        subscriber_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(subscriber_btn_frame, text="Start Subscriber", command=self.start_subscriber).pack(side=tk.LEFT, padx=5)
        tk.Button(subscriber_btn_frame, text="Stop Subscriber", command=self.stop_subscriber).pack(side=tk.LEFT, padx=5)
        tk.Button(subscriber_btn_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)

        self.log_area = scrolledtext.ScrolledText(subscriber_frame, state='disabled', height=20)
        self.log_area.pack(fill=tk.BOTH, expand=True)

        tag_styles = {
            "[device1]": {"foreground": "blue"},
            "[device2]": {"foreground": "green"},
            "[device3]": {"foreground": "purple"},
            "[WAIT]": {"foreground": "orange"},
            "[INFO]": {"foreground": "teal"},
            "[OK]": {"foreground": "darkgreen"},
            "[WARN]": {"foreground": "red"},
            "[ERROR]": {"foreground": "red", "font": ("Consolas", 10, "bold")},
            "[Subscriber]": {"foreground": "darkblue"},
        }
        for tag, config in tag_styles.items():
            self.log_area.tag_config(tag, **config)

    def check_broker_status(self):
        def check():
            if platform.system() == "Windows":
                result = subprocess.run("sc query mosquitto", capture_output=True, text=True, shell=True)
                status = "Mosquitto broker is RUNNING" if "RUNNING" in result.stdout else "Mosquitto broker is NOT running"
            else:
                result = subprocess.run(["systemctl", "is-active", "mosquitto"], capture_output=True, text=True)
                status = "Mosquitto broker is RUNNING" if result.returncode == 0 else "Mosquitto broker is NOT running"
            self.after(0, lambda: self.broker_status_var.set(f"Broker status: {status}"))

        threading.Thread(target=check, daemon=True).start()

    def start_broker(self):
        if platform.system() == "Windows":
            messagebox.showinfo("Info", "Please start Mosquitto broker manually on Windows.")
            return
        def start():
            subprocess.run(["sudo", "systemctl", "start", "mosquitto"])
            self.check_broker_status()
        threading.Thread(target=start, daemon=True).start()

    def stop_broker(self):
        if platform.system() == "Windows":
            messagebox.showinfo("Info", "Please stop Mosquitto broker manually on Windows.")
            return
        def stop():
            subprocess.run(["sudo", "systemctl", "stop", "mosquitto"])
            self.check_broker_status()
        threading.Thread(target=stop, daemon=True).start()

    def start_device(self, device_name):
        if device_name in self.device_processes and self.device_processes[device_name].poll() is None:
            messagebox.showwarning("Warning", f"{device_name} simulator already running.")
            return

        script_path = DEVICE_SCRIPTS[device_name]
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self.device_processes[device_name] = process
        threading.Thread(target=self._read_process_output, args=(process, f"{device_name}"), daemon=True).start()
        self.log(f"[INFO] Started {device_name} simulator.")

    def stop_device(self, device_name):
        process = self.device_processes.get(device_name)
        if process and process.poll() is None:
            process.terminate()
            self.log(f"[INFO] Stopped {device_name} simulator.")
        else:
            self.log(f"[WARN] {device_name} simulator is not running.")

    def start_subscriber(self):
        if self.subscriber_process and self.subscriber_process.poll() is None:
            messagebox.showwarning("Warning", "Subscriber is already running.")
            return

        process = subprocess.Popen(
            [sys.executable, SUBSCRIBER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.subscriber_process = process
        threading.Thread(target=self._read_process_output, args=(process, "Subscriber"), daemon=True).start()
        self.log("[INFO] Started subscriber.")

    def stop_subscriber(self):
        if self.subscriber_process and self.subscriber_process.poll() is None:
            self.subscriber_process.terminate()
            self.log("[INFO] Stopped subscriber.")
            self.send_stop_signal()
        else:
            self.log("[WARN] Subscriber is not running.")

    def clear_logs(self):
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.configure(state='disabled')

    def log(self, message):
        self.log_area.configure(state='normal')
        index_start = self.log_area.index('end-1c')
        self.log_area.insert(tk.END, message + "\n")
        index_end = self.log_area.index('end-1c')

        for tag in ["[device1]", "[device2]", "[device3]", "[WAIT]", "[INFO]", "[OK]", "[WARN]", "[ERROR]", "[Subscriber]"]:
            tag_start = self.log_area.search(tag, index_start, index_end)
            if tag_start:
                tag_end = f"{tag_start}+{len(tag)}c"
                self.log_area.tag_add(tag, tag_start, tag_end)

        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def _read_process_output(self, process, name):
        def stream_output():
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.after(0, lambda l=line: self.log(f"[{name}] {l.strip()}"))
            process.stdout.close()
        threading.Thread(target=stream_output, daemon=True).start()

    def on_closing(self):
        for process in self.device_processes.values():
            if process and process.poll() is None:
                process.terminate()
        if self.subscriber_process and self.subscriber_process.poll() is None:
            self.subscriber_process.terminate()
        self.destroy()


def clear_retained_start_signal():
    try:
        publish.single(
            topic="system/start_signal",
            payload=None,
            qos=0,
            retain=True,
            hostname="localhost"
        )
        print("[INFO] Cleared retained start signal.")
    except Exception as e:
        print(f"[ERROR] Failed to clear retained message: {e}")


if __name__ == "__main__":
    clear_retained_start_signal()
    app = IoTManagerGUI()
    app.mainloop()
