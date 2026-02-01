#  IoT Authentication & Authorization System

This repository contains a **Python-based IoT Authentication and Authorization System** designed to simulate IoT devices, register identities, and manage authentication flows — all while providing a basic GUI and orchestrator to run the workflow end-to-end.

It can serve as a starting point for learning IoT security concepts such as cryptographic identity management, secure device onboarding, and simulated device authentication flows.

---

##  Key Features

- Identity registry for devices  
- Multiple simulated IoT devices  
- Central manager GUI for controlling authentication setup  
- Utilities for cryptography and key management  
- One-shot script to run the entire pipeline

---

## Repository Structure


```
iot-auth-systems
├─ broker
│  └─ subscriber.py
├─ config.py
├─ credentials
│  ├─ did_registry.json
│  ├─ identity
│  │  ├─ device1_public_key.pem
│  │  └─ device2_public_key.pem
│  └─ private_keys
│     ├─ device1_private.pem
│     └─ device2_private.pem
├─ devices
│  ├─ device1_sim.py
│  ├─ device2_sim.py
│  └─ device3_sim.py
├─ device_sim.py
├─ identity_registry.py
├─ iot_manager_gui.py
├─ run_all.py
├─ utils
│  ├─ crypto_utils.py
│  ├─ __init__.py
│  └─ __pycache__
│     ├─ crypto_utils.cpython-312.pyc
│     └─ __init__.cpython-312.pyc
└─ __pycache__
   ├─ config.cpython-312.pyc
   ├─ identity_registry.cpython-312.pyc
   └─ subscriber.cpython-312.pyc

```
---

## About This Project

Internet-of-Things (IoT) devices often need identity verification and authentication before they can participate in a network. This project includes:

- A simulated identity registry and credential store  
- Multiple simulated IoT devices  
- A simple GUI to orchestrate authentication  
- Core cryptographic utilities to sign and verify messages

---

##  Requirements

- Python **3.8+**  
- `pip` (Python package manager)  
-  Recommended: Virtual environment (`venv` / `conda`)

Before running, install all dependencies:

```bash
pip install cryptography tkinter
```
---

## Running the System

1. Setup Credential Store (Optional)
You can customize or inspect the identity and key files under credentials/.
This directory contains device public/private keys and a DID registry.

2. Run the Full Pipeline
To start all components in a coordinated way:
```bash
python run_all.py
```
This script launches:
- identity registry handler
- simulated devices
- authentication broker
- manager GUI
  
3. Run Individual Components
If you’d like to start modules individually:

Run the manager GUI
```bash
python iot_manager_gui.py
```
Run a Device Simulator
```bash
python devices/device1_sim.py
```
(Replace device1_sim.py with any available device script.)

---

## How It Works
1. **Identity Registry**
   
   Stores public keys and identifiers for registered IoT devices.
3. **Device Simulators**
   
   Each simulated device communicates with the system, authenticates itself, and participates in basic messaging.
5. **Crypto Utilities**
   
   Handles signing, verification, and key load/store logic under the hood.
7. **Manager GUI**
   
   A user interface to monitor and control the system, inspect devices, and manage authentication flows.

---

## Example Use Cases
- Prototype secure onboarding for IoT devices
- Demonstrate authentication flows to students or teams
- Extend with real network communication protocols
- Integrate with actual edge devices or cloud backends

---

## Contributing
Contributions are welcome! You may:

- Add support for real IoT protocols (MQTT, CoAP)
- Expand identity types (certificates, signed JWTs, etc.)
- Improve the GUI (web interface)
- Add logging and test suites

---

## Acknowledgements
Built to explore IoT authentication fundamentals using Python and simple simulation tooling.
