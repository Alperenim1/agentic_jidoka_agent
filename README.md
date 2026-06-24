---
title: Agentic QA - Autonomous Jidoka Agent
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.30.0
app_file: app.py
pinned: false
---

# 🤖 Agentic QA: Autonomous Jidoka Agent

An end-to-end Agentic AI system demonstrating the application of **Jidoka** (Automation with a human touch) and **Andon** (visual stopping systems) protocols in smart manufacturing using **Computer Vision (YOLOv8)**, **LangChain (ReAct Agent)**, and **LLM-in-the-loop Quality Auditing**.

## 🔗 Live Application
The project is deployed and live on Hugging Face Spaces:
👉 **[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/Alperenim1/agentic_jidoka_agent)**

---

## 🎓 Academic Context
* **Institution:** Bahçeşehir University (BAU)
* **Course:** SEN4018 Data Science with Python
* **Developer:** Alperen Tüfekçi — Student ID: 2101882
* **Domain:** Intersection of Artificial Intelligence, Computer Vision, and Industrial Engineering

---

## 💡 Industrial Engineering Concepts Implemented

1. **Jidoka (Autonomation):** In traditional manufacturing, automation simply means machines replacing human labor. Jidoka introduces "automation with a human touch"—machines equipped with the intelligence to detect abnormalities and immediately shut themselves down to prevent the propagation of defects.
2. **Andon Protocol:** A visual alert system on the production floor. When the visual module detects a PCB defect, the Andon protocol is triggered: it halts the conveyor belt, changes the status light to red, and pages the line supervisor to inspect the station.

---

## 🏗️ System Architecture

The application is structured as a **three-tier agentic pipeline**:

```
                  [ 📸 STEP 1: VISION MODULE ]
                   Generates Synthetic PCB &
                    detects defects via YOLOv8
                                │
                                ▼ (Defect Description)
               [ 🧠 STEP 2: LANGCHAIN REACT AGENT ]
                Reasoning: Evaluates safety rules
                 Action: Calls stop_line_tool() &
                         calls notify_leader_tool()
                                │
                                ▼ (Execution Logs)
               [ 🛡️ STEP 3: SUPERVISOR AUDITOR ]
                 LLM-in-the-loop checks logs &
                  produces a JSON compliance report
```

### 1. Vision Module (`vision.py`)
* Programmatically generates high-fidelity synthetic PCB images (simulating green FR-4 substrates, gold traces, mounting holes, and components like resistors, capacitors, and microcontrollers).
* Supports injecting 4 defect types: `Missing Capacitor`, `Solder Bridge`, `Short Circuit`, and `Scratch`.
* Uses a custom-trained **YOLOv8** pipeline (with a high-fidelity local simulation fallback) to localize defects and generate bounding box overlays.

### 2. LangChain ReAct Agent (`agent.py`)
* Implements the **Reasoning and Action (ReAct)** pattern using LangChain.
* Equipped with custom tools:
  * `stop_line_tool`: Instantly halts the physical conveyor belt state.
  * `notify_leader_tool`: Dispatches a formatted notification dispatch box to the team leader (Alperen Tüfekçi).

### 3. Supervisor Auditor (`supervisor.py`)
* A secondary LLM agent acting as an independent quality inspector.
* It reads the primary agent's execution traces and verifies if the safety rules were strictly adhered to (i.e., conveyor line stopped AND leader notified).
* Outputs a structured JSON safety audit report containing approval status, checklist verification, and a compliance score (0-100%).

---

## ⚙️ Local Installation & Setup

To run the Streamlit dashboard locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Alperenim1/agentic_jidoka_agent.git
   cd agentic_jidoka_agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

*Note: You can run the application fully without API keys using the **Mock Simulation Mode** directly in the UI. To test live LLM logic, input your Google Gemini or OpenAI API keys in the sidebar.*
