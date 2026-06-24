# 🤖 Building an Autonomous Jidoka Agent: Merging Computer Vision and Agentic AI in Smart Manufacturing

*By Alperen Tüfekçi — Data Science with Python (SEN4018) Project*

Imagine a modern manufacturing facility producing thousands of Printed Circuit Boards (PCBs) every hour. In traditional factories, if a defect like a short circuit or a missing component slips past human inspectors, it can ruin an entire batch, costing thousands of dollars. 

To solve this, Toyota's production system popularized **Jidoka** (automation with a human touch) and **Andon** (a visual alert system that halts production when a defect occurs). 

In this blog post, we will walk through how we built **Agentic QA**, an end-to-end autonomous quality assurance system that combines **Computer Vision (YOLOv8)**, **Agentic AI (LangChain ReAct)**, and **LLM-in-the-Loop auditing** to bring Jidoka and Andon into the era of artificial intelligence.

---

## 🎯 The Core Philosophy: Jidoka & Andon Meet AI

* **Jidoka (Autonomation):** Instead of just automating tasks, we give machines the intelligence to detect anomalies and act autonomously. 
* **Andon Protocol:** The moment an anomaly is detected, the machine triggers a line stop, visual alarms sound, and the team leader is paged immediately.

In our software architecture, we modeled this lifecycle as a three-tier system:

```
📷 1. YOLOv8 (The Eyes) -> 🧠 2. LangChain Agent (The Brain) -> 🛡️ 3. Supervisor LLM (The Auditor)
```

---

## 🏗️ 3-Tier Technical Architecture

Here is how the three modules work together in Python:

### Phase 1: Computer Vision (YOLOv8) as the "Eyes"
Before an agent can make decisions, it needs to see. We programmatically generated high-fidelity synthetic PCBs containing normal states as well as various defect injections:
* **Missing Capacitor**
* **Solder Bridge**
* **Short Circuit**
* **Scratch**

We utilized **YOLOv8** (You Only Look Once) to run rapid inference on the camera frames. When YOLOv8 finds a defect, it outputs a bounding box and a class label with a confidence score.

```python
# A snippet from our vision.py showing how we detect PCB faults
def detect_defects(image, defect_type, use_yolo=False):
    # Runs local custom YOLOv8 model inference
    # Returns annotated image, bounding boxes, and latency (ms)
    ...
```

---

### Phase 2: LangChain ReAct Agent as the "Brain"
Once a defect is detected, the raw output is sent to a **LangChain agent** using the **ReAct (Reasoning and Action)** framework. The agent has access to two custom python tools:
1. `stop_line_tool`: Instantly halts the conveyor belt.
2. `notify_leader_tool`: Sends an SMS/Email alert to the team leader.

Using ReAct, the agent doesn't just call tools blindly; it reasons step-by-step:

> **Thought:** A visual inspection defect "Short Circuit" has been detected. According to the Jidoka protocol, I must stop the conveyor line immediately to prevent producing more defect products.
>
> **Action:** Call `stop_line_tool` with reason "Short Circuit detected".
>
> **Observation:** [STATUS: LINE_STOPPED] Assembly line stopped successfully.
>
> **Thought:** Now that the line is stopped, I must notify the team leader, Alperen Tüfekçi, so they can inspect the station.
>
> **Action:** Call `notify_leader_tool` with message "Assembly line halted due to Short Circuit."

---

### Phase 3: The Supervisor LLM as the "Auditor"
In high-stakes industrial environments, we cannot blindly trust an AI agent. To ensure absolute compliance, we introduced a **Supervisor LLM** that audits the execution logs of the primary agent.

The Supervisor acts as an independent auditor, verifying two critical safety rules:
1. Did the agent halt the line?
2. Was the manager paged?

It parses the raw logs and outputs a structured JSON compliance report:

```json
{
  "evaluation_status": "APPROVED",
  "line_stopped": true,
  "leader_notified": true,
  "score": 100,
  "evaluation_details": "The primary agent executed the Jidoka safety protocol flawlessly..."
}
```

---

## 🎨 Interactive Industrial Dashboard
We built a premium, responsive dashboard using **Streamlit** to tie the entire project together. The UI features:
* A **Conveyor Controls** sidebar to adjust speeds and toggle between simulation and live API modes (Gemini Flash & OpenAI GPT-4o).
* A **Live Camera Feed** with real-time YOLOv8 bounding box overlays.
* An **Industrial Events Console** displaying system logs in a retro matrix green terminal.
* A **Reasoning Trace** tab showing the agent's inner thoughts.
* An **Auditor** tab showing the safety compliance score.

---

## 💡 Key Engineering Takeaways
1. **Latency vs. Reasoning:** Real-time object detection must be done locally (YOLOv8 is fast, taking <15 ms), while the complex decision-making and auditing can be offloaded to cloud LLMs (Gemini/OpenAI) since a few seconds of latency is acceptable during a line stop.
2. **Safety with LLM-in-the-Loop:** Designing autonomous systems requires fallback safeguards. Having a supervisor agent evaluating execution logs guarantees that anomalies or tool failures are caught instantly.

---

## 🔗 Try It Out!
The project is fully open-source and deployed:
* 🐙 **GitHub Repository:** [github.com/Alperenim1/agentic_jidoka_agent](https://github.com/Alperenim1/agentic_jidoka_agent)
* 🤖 **Live Web Application:** [Hugging Face Spaces](https://huggingface.co/spaces/alperenim1/autonomous-jidoka-agent)

*Developed for the SEN4018 Data Science with Python course at Bahçeşehir University.*
