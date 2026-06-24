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

# Agentic QA: Autonomous Jidoka Agent

This project implements an end-to-end Agentic AI system demonstrating the application of **Jidoka** (Automation with a human touch) and **Andon** (visual stopping systems) protocols in smart manufacturing. 

## Academic Context
- **Course:** SEN4018 Data Science with Python
- **Developer:** Alperen Tüfekçi - 2101882
- **Domain:** Intersection of Artificial Intelligence and Industrial Engineering (Computer Vision & Agentic Automation)
- **Deployment Targets:** Streamlit + Hugging Face Spaces

---

## 🛠️ System Architecture

1. **Step 1: Vision Module (YOLOv8)**
   - Simulates visual inspection on an assembly conveyor belt.
   - Uses a programmatic high-fidelity synthetic PCB board generator (producing green FR-4 boards, copper traces, and component placement) to inject defects like `"Missing Capacitor"`, `"Solder Bridge"`, `"Short Circuit"`, or `"Scratch"`.
   - Runs a YOLOv8 detection pipeline (supporting standard library prediction and a highly realistic fallback pipeline to guarantee execution reliability in resource-constrained hosting environments).

2. **Step 2: Agentic Decision Loop (LangChain)**
   - When a defect is identified, a LangChain agent using the **ReAct (Reasoning and Action)** framework executes the **Andon** protocol.
   - It is equipped with custom tools:
     - `stop_line_tool`: Immediately shuts down the conveyor line.
     - `notify_leader_tool`: Dispatches a simulated alert notification to the team leader (Alperen Tüfekçi - 2101882).

3. **Step 3: Supervisor Evaluation (LLM-in-the-Loop)**
   - A secondary LLM supervisor agent analyzes the primary agent's execution logs and trace outputs.
   - It audits the run to ensure all safety guidelines were adhered to (stoppage was triggered, leader notified, defect described correctly) and issues a graded safety report.

---

## 🚀 Running Locally

1. **Clone or copy the project files:**
   ```bash
   cd agentic_jidoka_agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit dashboard:**
   ```bash
   streamlit run app.py
   ```

---

## 🤗 Deploying to Hugging Face Spaces

Since this project contains the Hugging Face frontmatter in the `README.md` and a custom `requirements.txt`, deployment is simple:

1. Create a new Space on [Hugging Face](https://huggingface.co/new-space).
2. Choose **Streamlit** as the SDK.
3. Push these files to your Space's repository:
   - `app.py`
   - `vision.py`
   - `agent.py`
   - `supervisor.py`
   - `requirements.txt`
   - `README.md`
4. The Space will automatically build and start!

*Note: You can run the application fully without API keys using the **Mock Simulation Mode** directly in the UI. To test live LLM logic, input your Google Gemini or OpenAI API keys in the sidebar.*
