# 🤖 Agentic QA: Autonomous Jidoka Agent — Final Implementation & Results

*By Alperen Tüfekçi — Student ID: 2101882*  
*SEN4018 Data Science with Python — Final Project Report*

---

## 🌟 Introduction & Motivation

Having observed the **Jidoka** (automation with a human touch) and **Andon** (visual stopping systems) concepts in person at **Toyota**, I was inspired to bring these powerful lean manufacturing methodologies into the age of Artificial Intelligence. 

In a traditional manufacturing setting, when a defect is detected on an assembly line, the time it takes for a human operator to notice, decide to halt the line, and notify the team leader introduces a significant delay. During this delay, defective products continue moving down the line, leading to waste and potential scrap.

My motivation for this project was to build an active, autonomous AI agent that eliminates this human latency by immediately executing the Andon protocol (halting the line and notifying the leader) the instant a defect is identified. 

---

## 🎯 Problem Statement and Field

* **Field:** The intersection of **Artificial Intelligence** and **Industrial Engineering**.
* **Problem Type:** Autonomous decision-making and computer vision.
* **Core Goal:** Automating the "stop-and-notify" quality control process to prevent defective PCBs (Printed Circuit Boards) from moving forward, removing the reliance on manual interventions.

---

## 🏗️ Technical Architecture: How It Works

Building upon the initial design, the final system implements a **three-step Agentic AI architecture**:

```
[ 📷 Vision Module ] ──(Defect Name)──► [ 🧠 LangChain ReAct Agent ] ──(Logs)──► [ 🛡️ LLM Supervisor ]
  Detects defect via                       Executes stop_line_tool &                      Audits compliance
 YOLOv8 or Simulator                      notify_leader_tool (Andon)                    & grades safety (0-100)
```

### 1. Vision Module
To inspect PCB boards, the system uses a high-fidelity synthetic PCB generator that renders clean boards with copper traces, mounting holes, and components. It simulates four manufacturing defect types:
* **Missing Capacitor**
* **Solder Bridge**
* **Short Circuit**
* **Scratch**

For defect detection, the system uses **Ultralytics YOLOv8** for fast and accurate object detection. In environments where local GPU resources are constrained or packages are missing, a high-fidelity rule-based visual simulator acts as a fallback to guarantee system reliability.

### 2. Agentic Decision Loop (LangChain)
When a defect is identified by the Vision Module, the text description of the defect is passed to a **LangChain ReAct (Reasoning and Action) Agent**. 
Rather than calling actions blindly, the agent uses a dynamic thought loop to determine the correct sequence of safety protocols using custom tools:
* `stop_line_tool`: Instantly halts the physical conveyor belt state.
* `notify_leader_tool`: Dispatches a formatted notification alert to the team leader (Alperen Tüfekçi - 2101882).

### 3. Safety Evaluation (LLM Supervisor)
To secure the system against potential AI hallucinations or tool execution failures, an independent **LLM Supervisor** audits the primary agent's execution logs. It runs as a secondary LLM-in-the-loop, checking two critical checklist items:
* Did the agent stop the conveyor line?
* Was the team leader notified?

The supervisor outputs a structured JSON report grading the safety execution (0-100%) and provides a detailed text audit.

---

## 🛠️ Frameworks, Technologies & Deployment

* **Computer Vision:** Ultralytics YOLOv8 for rapid visual frame analysis.
* **Agentic Framework:** LangChain to structure the ReAct decision loop and integrate custom tools.
* **LLM Integration:** Google Gemini API (Gemini 2.5 Flash) and OpenAI API (GPT-4o-mini) for dynamic reasoning and supervisor evaluation.
* **Web Interface:** A sleek Streamlit dashboard that visualizes the conveyor belt speed, visual camera feed, live console logs, and supervisor metrics.
* **Deployment:** Hosted live on Hugging Face Spaces for public testing.

---

## 👨‍💻 Solo Developer Responsibilities

As a solo developer on this project, I was responsible for the end-to-end pipeline:
* **Alperen Tüfekçi (2101882):** Responsible for designing the synthetic PCB generator, integrating YOLOv8, developing the LangChain ReAct reasoning loop, programming the custom tools, writing the LLM Supervisor audit prompt, and building and deploying the Streamlit UI on Hugging Face Spaces.

---

## 🔗 Try the Live System!

The final project is open-source and publicly hosted. You can inspect the source code or test the live agentic factory floor:

* 🐙 **GitHub Repository:** [github.com/Alperenim1/agentic_jidoka_agent](https://github.com/Alperenim1/agentic_jidoka_agent)
* 🤖 **Live Demo (Hugging Face Spaces):** [autonomous-jidoka-agent on Hugging Face](https://huggingface.co/spaces/alperenim1/autonomous-jidoka-agent)

*Developed as the final project for SEN4018 Data Science with Python, Bahçeşehir University.*
