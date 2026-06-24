import os
import streamlit as st
from PIL import Image, ImageDraw
from datetime import datetime
import json
import time

# Import local modules
import vision
import agent
import supervisor

# Page Configuration
st.set_page_config(
    page_title="SEN4018 - Autonomous Jidoka Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Detect environment API keys (Hugging Face Secrets or local environment)
env_gemini_key = os.environ.get("GEMINI_API_KEY")
env_openai_key = os.environ.get("OPENAI_API_KEY")

import pathlib
has_secrets_file = (
    pathlib.Path(".streamlit/secrets.toml").exists() or
    pathlib.Path("~/.streamlit/secrets.toml").expanduser().exists() or
    pathlib.Path("/app/.streamlit/secrets.toml").exists() or
    pathlib.Path("/root/.streamlit/secrets.toml").exists()
)

if has_secrets_file:
    try:
        if hasattr(st, "secrets"):
            if "GEMINI_API_KEY" in st.secrets:
                env_gemini_key = st.secrets["GEMINI_API_KEY"]
            if "OPENAI_API_KEY" in st.secrets:
                env_openai_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

# Custom Styling (Dark Industrial Dashboard with BAU corporate blue & Neon Accents)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Source+Code+Pro:wght@400;600&display=swap');

/* Apply modern typography */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif;
}

/* BAU Corporate Header Banner */
.academic-header {
    background: linear-gradient(135deg, #0f1c3f 0%, #1d3557 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.academic-title {
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}
.academic-subtitle {
    color: #4facfe;
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 5px;
    margin-bottom: 0;
}
.academic-logo-text {
    text-align: right;
    font-weight: 700;
    font-size: 1.3rem;
    color: #ffffff;
    border-left: 2px solid #4facfe;
    padding-left: 15px;
}

/* Glassmorphic panels */
.glass-card {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
}

/* Compliance Audit Panel styling */
.compliance-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f7fafc;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 8px;
}
.compliance-item {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 0.92rem;
}
.compliance-status-ok {
    color: #2ecc71;
    font-weight: 700;
}

/* Running/Stopped dynamic states */
.status-badge-running {
    background-color: rgba(46, 204, 113, 0.08);
    color: #2ecc71;
    border: 1.5px solid #2ecc71;
    padding: 12px;
    border-radius: 8px;
    font-weight: 800;
    font-size: 1.1rem;
    text-align: center;
    box-shadow: 0 0 15px rgba(46, 204, 113, 0.15);
    letter-spacing: 1px;
}
.status-badge-stopped {
    background-color: rgba(231, 76, 60, 0.08);
    color: #e74c3c;
    border: 1.5px solid #e74c3c;
    padding: 12px;
    border-radius: 8px;
    font-weight: 800;
    font-size: 1.1rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(231, 76, 60, 0.25);
    letter-spacing: 1px;
}

/* Logs console terminal styling */
.terminal-header {
    background-color: #1e2530;
    padding: 6px 12px;
    border-radius: 8px 8px 0 0;
    border-bottom: 1px solid #2d3748;
    color: #a0aec0;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.terminal-body {
    background-color: #0d1117;
    border-radius: 0 0 8px 8px;
    padding: 12px;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.8rem;
    color: #39ff14; /* Matrix Green */
    height: 300px;
    overflow-y: auto;
    border: 1px solid #1f242d;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.6);
}
.terminal-line {
    margin-bottom: 5px;
    line-height: 1.3;
}
.terminal-line-warn {
    color: #ffaa00;
}
.terminal-line-crit {
    color: #ff3333;
    font-weight: 600;
}
.terminal-line-info {
    color: #00bfff;
}

/* Agentic ReAct steps decoration */
.react-step-container {
    margin-bottom: 15px;
    border-left: 4px solid #4facfe;
    padding-left: 15px;
    background: rgba(255, 255, 255, 0.01);
    border-radius: 0 8px 8px 0;
    padding-top: 5px;
    padding-bottom: 5px;
}
.react-thought {
    color: #e2e8f0;
    background-color: rgba(66, 153, 225, 0.12);
    border: 1px solid rgba(66, 153, 225, 0.2);
    padding: 10px;
    border-radius: 6px;
    margin-top: 5px;
    margin-bottom: 5px;
}
.react-action {
    color: #fbd38d;
    background-color: rgba(221, 107, 32, 0.1);
    border: 1px solid rgba(221, 107, 32, 0.25);
    padding: 10px;
    border-radius: 6px;
    margin-top: 5px;
    margin-bottom: 5px;
}
.react-observation {
    color: #68d391;
    background-color: rgba(72, 187, 120, 0.1);
    border: 1px solid rgba(72, 187, 120, 0.25);
    padding: 10px;
    border-radius: 6px;
    margin-top: 5px;
    margin-bottom: 5px;
}

/* Metrics and visual styles */
.metric-box {
    text-align: center;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
.metric-box:last-child {
    border-right: none;
}
.metric-val {
    font-size: 1.8rem;
    font-weight: 800;
    color: #f7fafc;
}
.metric-lbl {
    font-size: 0.8rem;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "line_status" not in st.session_state:
    st.session_state.line_status = "RUNNING"
if "inspected" not in st.session_state:
    st.session_state.inspected = False
if "detections" not in st.session_state:
    st.session_state.detections = []
if "latency" not in st.session_state:
    st.session_state.latency = 0.0
if "agent_results" not in st.session_state:
    st.session_state.agent_results = None
if "supervisor_results" not in st.session_state:
    st.session_state.supervisor_results = None
if "log_history" not in st.session_state:
    st.session_state.log_history = [
        f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] Jidoka autonomous QA system initiated.",
        f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] Conveyor belt motor running normally (Speed: 1.2 m/s).",
        f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] Camera sensor activated. Ready for visual inspection."
    ]
if "selected_defect" not in st.session_state:
    st.session_state.selected_defect = "Normal (No Defects)"
if "inspected_image" not in st.session_state:
    st.session_state.inspected_image = None
if "annotated_image" not in st.session_state:
    st.session_state.annotated_image = None

# Sidebar - Student Information Card
st.sidebar.markdown(f"""
<div class="glass-card" style="margin-bottom:15px; border-left:4px solid #4facfe;">
    <div style="font-weight:800; font-size:1.1rem; color:#f7fafc;">SEN4018 Data Science</div>
    <div style="font-size:0.85rem; color:#a0aec0; margin-bottom:8px;">Semester-Long Project</div>
    <div style="font-size:0.9rem; font-weight:600; color:#4facfe;">Alperen Tüfekçi</div>
    <div style="font-size:0.8rem; color:#a0aec0;">Student ID: 2101882</div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Settings Configuration
st.sidebar.title("🛠️ Project Settings")

# Detect and default based on available keys
default_idx = 0
provider_options = ["Mock Simulation Mode", "Google Gemini", "OpenAI"]

if env_gemini_key:
    default_idx = 1
elif env_openai_key:
    default_idx = 2

provider = st.sidebar.selectbox(
    "LLM Provider Engine",
    provider_options,
    index=default_idx,
    help="Select Mock Simulation Mode or query real API endpoints."
)

api_key = None
model_name = None

# API input configurations
if provider == "Google Gemini":
    api_key = env_gemini_key or st.sidebar.text_input("Gemini API Key", type="password", placeholder="Enter Gemini key...")
    model_name = st.sidebar.selectbox("Gemini Model", ["gemini-2.5-flash", "gemini-2.5-pro"])
elif provider == "OpenAI":
    api_key = env_openai_key or st.sidebar.text_input("OpenAI API Key", type="password", placeholder="Enter OpenAI key...")
    model_name = st.sidebar.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o"])

# Display status of the selected LLM Provider
if provider != "Mock Simulation Mode" and api_key:
    st.sidebar.success("🔑 API Key configured and active.")
elif provider != "Mock Simulation Mode" and not api_key:
    st.sidebar.warning("⚠️ Please provide an API Key.")
else:
    st.sidebar.info("💡 Running in self-contained simulation mode.")

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Conveyor Controls")
conveyor_speed = st.sidebar.slider("Conveyor Speed (m/s)", 0.2, 2.5, 1.2, step=0.1)
yolo_inference_mode = st.sidebar.toggle("Use Ultralytics YOLOv8 Library", value=False, help="Runs local YOLOv8 weights on the board.")

# Reset Button
if st.sidebar.button("♻️ Reset Factory Floor State", use_container_width=True):
    st.session_state.line_status = "RUNNING"
    st.session_state.inspected = False
    st.session_state.detections = []
    st.session_state.latency = 0.0
    st.session_state.agent_results = None
    st.session_state.supervisor_results = None
    st.session_state.log_history = [
        f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] Conveyor state reset requested.",
        f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] Conveyor belt motor restarted. Status: RUNNING.",
        f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] Inspection logs cleared."
    ]
    st.session_state.inspected_image = None
    st.session_state.annotated_image = None
    agent.reset_agent_state()
    st.rerun()

# 🎓 Academic Header Banner
st.markdown("""
<div class="academic-header" style="justify-content: center; text-align: center;">
    <div>
        <h1 class="academic-title" style="font-size: 2.5rem; text-align: center;">🤖 Agentic QA: Autonomous Jidoka Agent</h1>
        <p class="academic-subtitle" style="font-size: 1.1rem; text-align: center; margin-top: 5px;">Smart Defect Inspection and Automated Stoppage Protocol (Andon)</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout containing Dynamic Line Status and the compliance audit panel
cols_status = st.columns([1, 2])

with cols_status[0]:
    # Dynamic Line Status Bar
    status_badge_html = (
        '<div class="status-badge-running">💚 CONVEYOR STATUS: RUNNING</div>'
        if st.session_state.line_status == "RUNNING"
        else '<div class="status-badge-stopped">🚨 ANDON HALT: STOPPED</div>'
    )
    st.markdown(status_badge_html, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display: flex; margin-top:15px; justify-content: space-around; background: rgba(255,255,255,0.02); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); height: 75px; align-items: center;">
        <div class="metric-box" style="flex:1;">
            <div class="metric-val" style="font-size:1.4rem;">{conveyor_speed} m/s</div>
            <div class="metric-lbl" style="font-size:0.7rem;">Belt Speed</div>
        </div>
        <div class="metric-box" style="flex:1;">
            <div class="metric-val" style="font-size:1.4rem;">{'YOLOv8-Sim' if not yolo_inference_mode else 'YOLOv8-Native'}</div>
            <div class="metric-lbl" style="font-size:0.7rem;">CV Model</div>
        </div>
        <div class="metric-box" style="flex:1;">
            <div class="metric-val" style="font-size:1.4rem; color: {'#e74c3c' if st.session_state.line_status == 'STOPPED' else '#2ecc71'}">
                {1 if st.session_state.line_status == 'STOPPED' else 0}
            </div>
            <div class="metric-lbl" style="font-size:0.7rem;">Defects Caught</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with cols_status[1]:
    # Course Project Compliance Verification
    st.markdown("""
    <div class="glass-card" style="padding: 12px 20px; height: 165px; margin-bottom: 0;">
        <div class="compliance-header">🎓 Course Project Compliance Audit</div>
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
            <div style="flex: 1; min-width: 200px;">
                <div class="compliance-item"><span class="compliance-status-ok">✓</span> <b>Autonomous Decision Loop:</b> LangChain ReAct</div>
                <div class="compliance-item"><span class="compliance-status-ok">✓</span> <b>Tool Usage:</b> stop_line_tool & notify_leader_tool</div>
            </div>
            <div style="flex: 1; min-width: 200px;">
                <div class="compliance-item"><span class="compliance-status-ok">✓</span> <b>Evaluation:</b> Supervisor LLM-in-the-loop</div>
                <div class="compliance-item"><span class="compliance-status-ok">✓</span> <b>Deployment:</b> Streamlit on Hugging Face Spaces</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# Tabs Configuration
tab_monitoring, tab_agent, tab_supervisor, tab_docs = st.tabs([
    "📸 Conveyor Belt Live Monitoring", 
    "🧠 Agentic ReAct Decision Trace", 
    "🛡️ Supervisor Compliance Audit", 
    "📘 Project Documentation"
])

# Tab 1: Live Monitoring
with tab_monitoring:
    col_trigger, col_feed = st.columns([1, 2])
    
    with col_trigger:
        with st.container(border=True):
            st.write("##### 🔬 Defect Injection Panel")
            st.write("Simulate defects on the assembly line to trigger the Jidoka safety protocol:")
            
            defect_option = st.selectbox(
                "Select PCB Fault",
                ["Normal (No Defects)", "Missing Capacitor", "Solder Bridge", "Short Circuit", "Scratch"]
            )
            
            run_sim = st.button("🚀 Trigger Conveyor & Inspect", use_container_width=True)
        
        # Display simulated email output in the UI if sent
        if st.session_state.line_status == "STOPPED" and len(agent.agent_execution_state["notifications_sent"]) > 0:
            st.markdown('<div class="glass-card" style="border-left: 4px solid #9b59b6;">', unsafe_allow_html=True)
            st.markdown("##### 📧 Notification Dispatch Box")
            for note in agent.agent_execution_state["notifications_sent"]:
                st.markdown(f"""
                **To:** `{note['recipient']}`  
                **Time:** `{note['timestamp']}`  
                **Status:** `TRANSMITTED ✅`  
                **Alert Body:**  
                *{note['message']}*
                """)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_feed:
        col_img, col_term = st.columns([1, 1])
        
        with col_img:
            st.write("##### 🖼️ Camera Feed (YOLOv8)")
            if st.session_state.inspected and st.session_state.annotated_image is not None:
                st.image(st.session_state.annotated_image, use_column_width=True, caption="Live CV Inspection Output")
            else:
                # Standby image
                empty_img = Image.new("RGB", (640, 480), color=(25, 28, 36))
                draw = ImageDraw.Draw(empty_img)
                draw.text((220, 230), "CONVEYOR IN STANDBY MODE", fill=(100, 115, 130))
                st.image(empty_img, use_column_width=True, caption="Camera Standby Feed")
                
        with col_term:
            st.write("##### 📟 Industrial Events Console")
            
            # Print logs into the console
            logs_html = ""
            for line in st.session_state.log_history:
                if "[CRITICAL]" in line or "HALTED" in line or "STOPPED" in line:
                    logs_html += f'<div class="terminal-line terminal-line-crit">{line}</div>'
                elif "[ALERT]" in line or "warning" in line.lower() or "defect" in line.lower():
                    logs_html += f'<div class="terminal-line terminal-line-warn">{line}</div>'
                elif "[SYSTEM]" in line:
                    logs_html += f'<div class="terminal-line terminal-line-info">{line}</div>'
                else:
                    logs_html += f'<div class="terminal-line">{line}</div>'
                    
            st.markdown(f"""
            <div class="terminal-header">
                <span>Production Console v1.50</span>
                <span style="color: #2ecc71;">● ONLINE</span>
            </div>
            <div class="terminal-body">
                {logs_html}
            </div>
            """, unsafe_allow_html=True)

    # Core logic when simulation runs
    if run_sim:
        st.session_state.inspected = True
        st.session_state.selected_defect = defect_option
        
        # Determine actual injected defect
        injected = None if "Normal" in defect_option else defect_option
        
        # Initialize logs
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.log_history = [
            f"[{ts}] [SYSTEM] Conveyor startup triggered. Initializing inspection cycle...",
            f"[{ts}] [SYSTEM] Conveyor belt moving at {conveyor_speed} m/s.",
            f"[{ts}] [SYSTEM] Capturing visual frame of incoming PCB board..."
        ]
        
        # Generate base PCB image
        raw_img, _ = vision.generate_pcb_image(injected)
        st.session_state.inspected_image = raw_img
        
        # Run detection
        with st.spinner("Executing YOLOv8 inspection..."):
            ann_img, detections, latency = vision.detect_defects(raw_img, injected, use_yolo=yolo_inference_mode)
            
        st.session_state.annotated_image = ann_img
        st.session_state.detections = detections
        st.session_state.latency = latency
        
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.log_history.append(f"[{ts}] [SYSTEM] Frame analysis completed in {latency} ms.")
        
        if len(detections) > 0:
            defect_details = detections[0]
            label = defect_details["label"]
            conf = defect_details["conf"]
            
            st.session_state.log_history.append(
                f"[{ts}] [CRITICAL] CV Alert: Defect '{label}' detected with {int(conf*100)}% confidence!"
            )
            st.session_state.log_history.append(
                f"[{ts}] [SYSTEM] Handing off control to Autonomous LangChain Agent..."
            )
            
            # Run LangChain agent
            agent_provider = "Mock" if provider == "Mock Simulation Mode" else provider
            
            with st.spinner("LangChain Agent executing safety decision loop..."):
                agent_res = agent.execute_jidoka_loop(
                    defect_description=f"{label} (Confidence: {int(conf*100)}%)",
                    provider=agent_provider,
                    api_key=api_key,
                    model_name=model_name
                )
            
            st.session_state.agent_results = agent_res
            st.session_state.line_status = agent.agent_execution_state["line_status"]
            
            # Incorporate agent logs
            for alog in agent_res["raw_logs"]:
                st.session_state.log_history.append(alog)
                
            ts = datetime.now().strftime("%H:%M:%S")
            st.session_state.log_history.append(f"[{ts}] [SYSTEM] Autonomous Agent tasks finalized.")
            st.session_state.log_history.append(f"[{ts}] [SYSTEM] Activating Supervisor safety auditor...")
            
            # Run Supervisor verification LLM
            with st.spinner("Supervisor LLM auditing execution logs..."):
                supervisor_res = supervisor.run_supervisor_evaluation(
                    logs=agent_res["raw_logs"],
                    provider=agent_provider,
                    api_key=api_key,
                    model_name=model_name
                )
                
            st.session_state.supervisor_results = supervisor_res
            
            st.session_state.log_history.append(
                f"[{ts}] [SYSTEM] Safety evaluation complete. Result: {supervisor_res.get('evaluation_status', 'UNKNOWN')} "
                f"(Safety Audit Score: {supervisor_res.get('score', 0)}/100)"
            )
            
        else:
            # Clean board, no defect
            st.session_state.line_status = "RUNNING"
            st.session_state.agent_results = None
            st.session_state.supervisor_results = None
            st.session_state.log_history.append(
                f"[{ts}] [SYSTEM] Inspection PASS: Board is clean. No defects detected."
            )
            st.session_state.log_history.append(
                f"[{ts}] [SYSTEM] Conveyor belt continues moving (Normal State)."
            )
            
        st.rerun()

# Tab 2: Agent Decision Trace
with tab_agent:
    st.subheader("LangChain Autonomous Reasoning Loop (ReAct Trace)")
    
    if st.session_state.agent_results is not None:
        st.write("This tab displays the step-by-step reasoning logs (Thought-Action-Observation) generated by the LangChain agent:")
        
        # Display Final Answer Card
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #2ecc71;">
            <div style="font-weight:600; color:#a0aec0; font-size:0.9rem;">FINAL AGENT CONCLUSION</div>
            <div style="font-size:1.1rem; font-weight:600; margin-top:5px; color:#f7fafc;">
                {st.session_state.agent_results['final_answer']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Step-by-step Traces
        st.write("##### 🛠️ Agent Execution Trace Logs:")
        for idx, step in enumerate(st.session_state.agent_results["trace"]):
            st.markdown(f"""
            <div class="react-step-container">
                <div style="font-weight:800; color:#4facfe; margin-bottom:5px;">Agent Cycle Step #{idx+1}</div>
                <div class="react-thought">
                    <strong>Thought:</strong> {step['thought']}
                </div>
            """, unsafe_allow_html=True)
            
            if step['action'] and step['action'] != 'Final Answer':
                st.markdown(f"""
                <div class="react-action">
                    <strong>Action:</strong> Call tool <code>{step['action']}</code> with argument <code>"{step['action_input']}"</code>
                </div>
                <div class="react-observation">
                    <strong>Observation:</strong> {step['observation']}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
    else:
        st.info("No active agent traces. Run an inspection cycle with a PCB defect selected to trigger the LangChain agent loop.")

# Tab 3: Supervisor Verification
with tab_supervisor:
    st.subheader("Supervisor LLM-in-the-Loop Quality Audit")
    
    if st.session_state.supervisor_results is not None:
        eval_res = st.session_state.supervisor_results
        status = eval_res.get("evaluation_status", "FAILED")
        score = eval_res.get("score", 0)
        line_stopped = eval_res.get("line_stopped", False)
        leader_notified = eval_res.get("leader_notified", False)
        details = eval_res.get("evaluation_details", "No details provided.")
        
        badge_style = "background-color:rgba(46,204,113,0.12); color:#2ecc71; border:1.5px solid #2ecc71;" if status == "APPROVED" else "background-color:rgba(231,76,60,0.12); color:#e74c3c; border:1.5px solid #e74c3c;"
        
        col_grade, col_audit = st.columns([1, 2])
        
        with col_grade:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h5 style="margin-bottom:10px;">Audit Verdict</h5>
                <div style="display:inline-block; padding:8px 20px; border-radius:20px; font-weight:800; {badge_style} margin-bottom:15px;">
                    {status}
                </div>
                <div style="font-size:3.2rem; font-weight:800; color:#4facfe; margin-bottom:5px;">{score}%</div>
                <div style="font-size:0.8rem; color:#718096; text-transform:uppercase;">Compliance Audit Score</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("##### ✅ Compliance Checklist:")
            st.markdown(f"- {'✅' if line_stopped else '❌'} **Conveyor Halted:** { 'Yes' if line_stopped else 'No'}")
            st.markdown(f"- {'✅' if leader_notified else '❌'} **Leader Contacted:** { 'Yes' if leader_notified else 'No'}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_audit:
            st.write("##### 📝 Safety Audit Details:")
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #f1c40f; white-space: pre-wrap; font-family: sans-serif; font-size:0.95rem; line-height:1.5;">
{details}
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.info("No active supervisor report. Run an inspection cycle with a PCB defect to compile logs for the Supervisor LLM.")

# Tab 4: System Docs
with tab_docs:
    st.subheader("🔍 Technical System Inspector (Background Processes)")
    st.write("This helper panel allows you to walk through the raw logic, prompts, and tool definitions running in the background of the Jidoka system:")

    # 1. Pipeline Status
    st.markdown("### 🚦 Real-Time Pipeline State")
    cols_pipeline = st.columns(3)
    with cols_pipeline[0]:
        st.markdown(f"""
        <div style="background: rgba(79, 172, 254, 0.08); border: 1px solid #4facfe; border-radius: 8px; padding: 12px; text-align: center;">
            <div style="font-size: 0.8rem; color: #a0aec0;">STEP 1: VISION MODULE</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff;">YOLOv8 Detection</div>
            <div style="font-size: 0.9rem; margin-top: 5px; color: #2ecc71;">{"ACTIVE (Latency: " + str(st.session_state.latency) + " ms)" if st.session_state.inspected else "STANDBY"}</div>
        </div>
        """, unsafe_allow_html=True)
    with cols_pipeline[1]:
        st.markdown(f"""
        <div style="background: rgba(251, 211, 141, 0.08); border: 1px solid #fbd38d; border-radius: 8px; padding: 12px; text-align: center;">
            <div style="font-size: 0.8rem; color: #a0aec0;">STEP 2: AGENTIC LOOP</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff;">LangChain ReAct Agent</div>
            <div style="font-size: 0.9rem; margin-top: 5px; color: #fbd38d;">{"COMPLETED" if st.session_state.agent_results else "STANDBY"}</div>
        </div>
        """, unsafe_allow_html=True)
    with cols_pipeline[2]:
        st.markdown(f"""
        <div style="background: rgba(241, 196, 15, 0.08); border: 1px solid #f1c40f; border-radius: 8px; padding: 12px; text-align: center;">
            <div style="font-size: 0.8rem; color: #a0aec0;">STEP 3: SAFETY AUDIT</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff;">Supervisor LLM</div>
            <div style="font-size: 0.9rem; margin-top: 5px; color: #f1c40f;">{("COMPLETED (Score: " + str(st.session_state.supervisor_results.get("score", 0)) + "%)") if st.session_state.supervisor_results else "STANDBY"}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # 2. Under the Hood expanders
    st.markdown("### 🛠️ Under the Hood (Prompts & Tool Specs)")
    
    with st.expander("📝 1. Primary Agent: ReAct Prompt Template"):
        st.code(agent.REACT_PROMPT_TEMPLATE, language="markdown")
        st.caption("This system prompt dictates how the primary agent reasons (Thought) and decides to execute tools (Action).")

    with st.expander("🔧 2. Registered Python Tools (API Specs)"):
        st.markdown("""
        When the LLM receives the prompt, LangChain automatically extracts the docstrings and arguments of our registered tools to let the LLM know they exist:
        """)
        st.markdown("**Tool 1: `stop_line_tool`**")
        st.code("""
@tool
def stop_line_tool(reason: str) -> str:
    \"\"\"
    Stops the assembly line conveyor belt immediately.
    Use this tool when a manufacturing defect or missing part is detected.
    Input should be a descriptive reason for the shutdown.
    \"\"\"
        """, language="python")
        
        st.markdown("**Tool 2: `notify_leader_tool`**")
        st.code("""
@tool
def notify_leader_tool(message: str) -> str:
    \"\"\"
    Sends an urgent alert notification (email/SMS) to the team leader (Alperen Tüfekçi - 2101882).
    Use this tool to inform the supervisor about the line stoppage and the nature of the defect.
    Input should be the warning message detailing the defect.
    \"\"\"
        """, language="python")

    with st.expander("🛡️ 3. Supervisor LLM: System Instruction"):
        st.code(supervisor.SUPERVISOR_SYSTEM_INSTRUCTION, language="markdown")
        st.caption("This prompt enforces that the supervisor agent outputs a clean, compliant JSON report without any markdown formatting.")

    with st.expander("📊 4. System Deployment & Academic Context"):
        st.markdown("""
        * **Developer:** Alperen Tüfekçi (Student ID: 2101882)
        * **Course:** SEN4018 Data Science with Python (Bahçeşehir University)
        * **Deployment Architecture:** Streamlit Dashboard hosted on Hugging Face Spaces.
        * **Code Repository:** [GitHub Repo](https://github.com/Alperenim1/agentic_jidoka_agent)
        * **Concepts Demonstrated:**
          * **Jidoka (Autonomation):** Conveyor stops automatically upon abnormality.
          * **Andon Protocol:** Immediate visual alerts and leader notification dispatch.
          * **LLM-in-the-loop:** Automated auditing of safety-critical agent logic.
        """)
