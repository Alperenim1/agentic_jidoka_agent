import os
import json
import time
from datetime import datetime
try:
    from langchain_classic.agents import AgentExecutor, create_react_agent
except ImportError:
    from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Shared state dictionary to store execution details for the UI
agent_execution_state = {
    "line_status": "RUNNING",
    "notifications_sent": [],
    "logs": []
}

def reset_agent_state():
    """Resets the state of tools and logs for a new run."""
    agent_execution_state["line_status"] = "RUNNING"
    agent_execution_state["notifications_sent"] = []
    agent_execution_state["logs"] = []

# Define Tools using LangChain @tool decorator
@tool
def stop_line_tool(reason: str) -> str:
    """
    Stops the assembly line conveyor belt immediately.
    Use this tool when a manufacturing defect or missing part is detected.
    Input should be a descriptive reason for the shutdown.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    agent_execution_state["line_status"] = "STOPPED"
    log_entry = f"[{timestamp}] [CRITICAL] Andon Line Stop activated. Reason: {reason}."
    agent_execution_state["logs"].append(log_entry)
    return f"[STATUS: LINE_STOPPED] Assembly line stopped successfully at {timestamp}. Reason code: {reason}"

@tool
def notify_leader_tool(message: str) -> str:
    """
    Sends an urgent alert notification (email/SMS) to the team leader (Alperen Tüfekçi - 2101882).
    Use this tool to inform the supervisor about the line stoppage and the nature of the defect.
    Input should be the warning message detailing the defect.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notification = {
        "timestamp": timestamp,
        "recipient": "Alperen Tüfekçi (Leader - 2101882)",
        "message": message,
        "status": "SENT"
    }
    agent_execution_state["notifications_sent"].append(notification)
    log_entry = f"[{timestamp}] [ALERT] Team Leader Alperen Tüfekçi notified. Message: {message}."
    agent_execution_state["logs"].append(log_entry)
    return f"[ALERT: LEADER_NOTIFIED] Notification successfully transmitted to Alperen Tüfekçi - 2101882. Message: '{message}'"

def get_tools():
    return [stop_line_tool, notify_leader_tool]

# LangChain ReAct prompt template
REACT_PROMPT_TEMPLATE = """You are the Autonomous Jidoka Agent. Your goal is to manage assembly line exceptions.
When a defect is detected, you must immediately STOP the assembly line using the stop_line_tool and NOTIFY the team leader (Alperen Tüfekçi - 2101882) using the notify_leader_tool.

You have access to the following tools:

{tools}

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have completed all actions, or if no defects are present, respond with your final answer:

Thought: Do I need to use a tool? No
Final Answer: [your response summarizing what actions you took]

Begin!

Context: A visual inspection detected a defect: "{input}"
Thought: {agent_scratchpad}"""

def run_agent_real(provider, api_key, model_name, defect_description):
    """Executes the actual LangChain ReAct agent using OpenAI or Google Gemini."""
    tools = get_tools()
    
    # Initialize the correct LLM
    if provider == "Google Gemini":
        llm = ChatGoogleGenerativeAI(
            model=model_name or "gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.0
        )
    elif provider == "OpenAI":
        llm = ChatOpenAI(
            model=model_name or "gpt-4o-mini",
            api_key=api_key,
            temperature=0.0
        )
    else:
        raise ValueError("Invalid LLM Provider specified.")

    prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)
    
    # Build the ReAct Agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the Agent Executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )
    
    # Run agent execution
    result = agent_executor.invoke({"input": defect_description})
    
    # Extract trace/intermediate steps
    trace_logs = []
    for action, observation in result.get("intermediate_steps", []):
        trace_logs.append({
            "thought": action.log.split("Action:")[0].replace("Thought:", "").strip(),
            "action": action.tool,
            "action_input": action.tool_input,
            "observation": observation
        })
        
    return {
        "final_answer": result["output"],
        "trace": trace_logs,
        "raw_logs": agent_execution_state["logs"].copy()
    }

def run_agent_mock(defect_description):
    """
    Simulates the LangChain ReAct agent execution trace.
    Returns identical data structure to run_agent_real to allow seamless UI fallback.
    """
    time.sleep(1.5) # Simulate execution latency
    
    # Run the physical tool functions directly to update execution state
    stop_response = stop_line_tool.invoke(f"Defect detected: {defect_description}")
    time.sleep(0.8)
    notify_response = notify_leader_tool.invoke(f"Assembly line halted. Defect: {defect_description}. Action needed.")
    
    # Construct simulated ReAct intermediate steps
    trace = [
        {
            "thought": "A visual inspection defect has been detected. According to the Jidoka (Andon) protocol, I must stop the conveyor line immediately to prevent producing more defect products.",
            "action": "stop_line_tool",
            "action_input": f"Defect detected: {defect_description}",
            "observation": stop_response
        },
        {
            "thought": "The conveyor line has been successfully stopped. Now, I must notify the team leader, Alperen Tüfekçi - 2101882, to inspect the physical station and resolve the issue.",
            "action": "notify_leader_tool",
            "action_input": f"Assembly line halted. Defect: {defect_description}. Action needed.",
            "observation": notify_response
        },
        {
            "thought": "I have successfully stopped the line and notified the team leader Alperen Tüfekçi. The defect is contained and leadership is informed. I can conclude the task.",
            "action": "Final Answer",
            "action_input": "",
            "observation": ""
        }
    ]
    
    final_answer = f"Autonomous Jidoka Agent completed execution. Defect '{defect_description}' was intercepted. The assembly conveyor was stopped, and team leader Alperen Tüfekçi was paged."
    
    return {
        "final_answer": final_answer,
        "trace": trace,
        "raw_logs": agent_execution_state["logs"].copy()
    }

def execute_jidoka_loop(defect_description, provider="Mock", api_key=None, model_name=None):
    """
    Main entry point for agentic decision loop.
    Decides between executing a live LangChain Agent or Mock trace.
    """
    reset_agent_state()
    
    if provider == "Mock" or not api_key:
        return run_agent_mock(defect_description)
    else:
        return run_agent_real(provider, api_key, model_name, defect_description)

if __name__ == "__main__":
    # Test Mock execution
    print("Testing Mock Agent Execution:")
    res = execute_jidoka_loop("Missing Capacitor C1")
    print(json.dumps(res, indent=2))
