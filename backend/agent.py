import os
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# Phase 2: Agentic Trading Engine using LangGraph
# This agent takes in current grid conditions and battery state, 
# then decides how to allocate power between the factory and the grid.

# Define the state dictionary that LangGraph will pass between nodes
class AgentState(Dict[str, Any]):
    grid_price: float
    grid_status: str
    battery_soc: float
    factory_load: float
    decision_reasoning: str
    target_factory_multiplier: float # 0.0 to 1.0
    target_battery_action: str # "CHARGE", "DISCHARGE", "HOLD"

# --- Nodes ---

def analyze_market_conditions(state: AgentState) -> AgentState:
    """
    Node 1: Analyze current inputs and construct a prompt for the LLM.
    """
    system_prompt = """You are the AI brain behind the 'Resilient Micro-Hub Orchestrator'.
Your goal is to maximize yield through energy arbitrage while ensuring the modular housing factory 
suffers minimal disruption. You manage a 10 MWh battery and a 2.0 MW factory load.

Rules:
1. If NYISO Grid Status is NOT 'NORMAL' (e.g., 'EMERGENCY_ISLAND'), you MUST output:
   ACTION: HOLD, FACTORY_MULTIPLIER: 0.0, REASON: Emergency islanding triggered.
2. If the Grid Price is highly lucrative (>$60/MWh), optimize for Arbitrage (discharging battery).
3. If the Grid Price is very cheap (<$30/MWh), buy power to charge the battery and run the factory.
4. Otherwise, maintain stable factory operations and hold the battery.

Provide your output EXACTLY in this format:
ACTION: [CHARGE | DISCHARGE | HOLD]
FACTORY_MULTIPLIER: [0.0 to 1.0]
REASON: [Short explanation of why]"""

    user_prompt = f"""
Current State:
- Grid Price (ERCOT): ${state['grid_price']}/MWh
- NYISO Status: {state['grid_status']}
- Battery SoC: {state['battery_soc'] * 100}%
"""
    # We will invoke the LLM in the next node, we just prepare the messages here
    state['messages'] = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    return state

def generate_decision(state: AgentState) -> AgentState:
    """
    Node 2: Call the LLM to generate the trading decision and parse the output.
    """
    # For development/testing without a live API key, we will simulate the LLM's response
    # based on the rules we provided it.
    # TODO: Replace with actual `llm.invoke(state['messages'])` when OPENAI_API_KEY is provided.
    
    price = state['grid_price']
    status = state['grid_status']
    
    action = "HOLD"
    multiplier = 1.0
    reason = "Stable conditions."
    
    if status != "NORMAL":
        action = "HOLD"
        multiplier = 0.0
        reason = f"EMERGENCY! NYISO Signal: {status}. Islanding Micro-Hub."
    elif price > 60.0:
        action = "DISCHARGE"
        multiplier = 0.5
        reason = f"High grid price (${price:.2f}/MWh). Agent opted to throttle factory and perform arbitrage."
    elif price < 30.0:
        action = "CHARGE"
        multiplier = 1.0
        reason = f"Low grid price (${price:.2f}/MWh). Agent opted to charge battery and run factory."

    state['target_battery_action'] = action
    state['target_factory_multiplier'] = multiplier
    state['decision_reasoning'] = reason
    
    return state

# --- Build Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("analyze", analyze_market_conditions)
workflow.add_node("decide", generate_decision)

workflow.add_edge(START, "analyze")
workflow.add_edge("analyze", "decide")
workflow.add_edge("decide", END)

# Compile the graph
trading_agent = workflow.compile()

# Helper function to run the agent from the engine
def run_trading_agent(grid_price: float, grid_status: str, battery_soc: float) -> dict:
    initial_state = {
        "grid_price": grid_price,
        "grid_status": grid_status,
        "battery_soc": battery_soc,
        "factory_load": 0.0, # Will be updated by engine
        "decision_reasoning": "",
        "target_factory_multiplier": 1.0,
        "target_battery_action": "HOLD"
    }
    
    # Run the graph
    final_state = trading_agent.invoke(initial_state)
    return final_state
