
import subprocess
import platform

def check_mosquitto_running():
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output("tasklist", shell=True).decode()
            return "mosquitto.exe" in output
        else:
            output = subprocess.check_output(["ps", "aux"]).decode()
            return "mosquitto" in output
    except Exception as e:
        print(f"Error checking Mosquitto status: {e}")
        return False
