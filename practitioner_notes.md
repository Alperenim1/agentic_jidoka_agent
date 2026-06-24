# 📋 Practitioner Notes & Executive Summary

*Project Title: Agentic QA: Autonomous Jidoka Agent*  
*Author: Alperen Tüfekçi (2101882)*  
*Course: SEN4018 Data Science with Python*

---

## 🔍 Executive Summary

This project implements an autonomous quality assurance (QA) system for modern smart manufacturing lines by combining **Computer Vision (YOLOv8)** and **Agentic AI (LangChain ReAct & LLM Supervisor)**. 

Inspired by Toyota's **Jidoka** (autonomation) and **Andon** (visual stopping systems) protocols, the system visualizes PCB assembly lines, detects manufacturing defects (missing capacitors, short circuits, solder bridges, scratches), and executes autonomous stopping and paging actions. 

By offloading exception handling to a Reasoning and Action (ReAct) agent, the system eliminates human response latency. Additionally, it introduces an **LLM Supervisor** to independently audit the system logs and guarantee safety compliance (LLM-in-the-loop validation). The final system is deployed as an interactive dashboard on Hugging Face Spaces.

---

## 💡 Practitioner Notes

These notes explain the practical significance of this research, technical trade-offs, and guidelines for deployment in real-world industrial environments.

### 1. Key Operational Findings
* **The Latency Trade-Off:** Real-time visual anomaly detection must run locally at the edge (YOLOv8 inference takes `<15ms` per frame). However, complex decision-making and notification dispatching can be offloaded to cloud LLMs (Gemini/OpenAI) because a `1.5 - 2.0s` response latency is fully acceptable once the physical line has already been halted.
* **Robustness through Redundancy (LLM Auditor):** Large Language Models can occasionally hallucinate or fail to parse text. Utilizing an independent **Supervisor LLM** to inspect the execution trace and safety checklist before clearing the state guarantees that failures are caught, logged, and audited.
* **Deterministic Fallbacks:** While agentic behavior allows flexible and intelligent responses to complex defect descriptions, safety-critical tasks (like halting the line) should always have deterministic software overrides.

### 2. How to Implement this System in a Real Factory
To transition this prototype into a physical smart factory, practitioners should follow these integration guidelines:

```
[ 🎥 Camera over Conveyor ]
            │
            ▼ (RTSP Stream)
[ 🖥️ Edge Device: NVIDIA Jetson ] ──► Runs YOLOv8 locally (<15ms detection)
            │
            ▼ (If defect found: sends text label to Local LLM)
[ 🧠 Local LLM: Ollama / Llama-3 ] ──► Executes ReAct Agent & Supervisor
            │
            ├─► Trigger relay output to PLC (Halt conveyor motor)
            └─► Send MQTT / SMS / Email alert to supervisor
```

1. **Hardware Setup (Vision):** Install high-resolution industrial cameras directly above the conveyor belt stations. Stream the visual feed via RTSP to an edge computing device (e.g., NVIDIA Jetson or an industrial PC with a dedicated GPU) to run the YOLOv8 model locally.
2. **Local LLM Deployment (Privacy & Latency):** In real production floors, relying on external cloud APIs (Gemini/OpenAI) introduces internet dependency and raises data privacy concerns. Deploy a local LLM (e.g., Llama-3 or Mistral via **Ollama**) on-premise to keep all data internal and reduce latency.
3. **PLC Integration (Physical Stoppage):** The `stop_line_tool` in a real factory should interact with a **PLC (Programmable Logic Controller)**. When the tool is triggered, it writes a register value via a protocol like Modbus/TCP or OPC UA, prompting the PLC to open a relay contact and immediately stop the conveyor motor.
4. **Notification Systems:** Connect the `notify_leader_tool` to industrial messaging systems (e.g., Siemens MindSphere, MQTT brokers, or SMS gateways) to ensure immediate notification delivery to the line supervisor's mobile device or smartwatch.
