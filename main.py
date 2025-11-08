import langgraph
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from colorama import Fore
from typing import Annotated
from langgraph.prebuilt import ToolNode
from tool import simple_screener



SYSTEM_PROMPT = """You are a helpful financial assistant specializing in Indian mutual funds.

When users ask about mutual fund screening:
- "high risk" or "aggressive" → use "best_mid_cap_funds" or "high_return_funds"
- "low risk" or "conservative" → use "debt_mutual_funds"  
- "moderate risk" or "balanced" → use "best_large_cap_funds"
- "top performing" → use "top_performing_funds" or "high_return_funds"

Don't overthink - pick the closest matching screen_type and make the tool call.
DO NOT HALLUCINATE"""


llm = ChatOllama(model="qwen3:8b")


tool = [simple_screener]

llm_tooled = llm.bind_tools(tool)

tools = ToolNode(tool)


class State(dict):
    messages: Annotated[list[dict], add_messages]

def chat(state: State) -> State:
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content = SYSTEM_PROMPT) ]+ messages
    return {"messages":[llm_tooled.invoke(state["messages"])]}

def cond(state:State):
    last = state['messages'][-1]
    if hasattr(last, "tool_calls") and len(last.tool_calls) > 0:
        return "tool"
    else:
        return "end"



graph_builder = StateGraph(State)
graph_builder.add_node("chat", chat)
graph_builder.add_edge(START, "chat")
graph_builder.add_node("tool", tools)
graph_builder.add_edge("tool", "chat")
graph_builder.add_conditional_edges(
       "chat",
       cond,
       {
           "tool": "tool", 
           "end": END
       }
   )

graph_builder.add_edge("chat", END)

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)

if __name__ == "__main__":
    while True:
        Prompt = input("Enter your prompt: ")
        if Prompt.lower() == "exit":
            break 
        else:
            response = graph.invoke({"messages": [{"role": "user", "content": Prompt}]}, config={"configurable": {"thread_id": "123"}})
            print(Fore.LIGHTYELLOW_EX + response["messages"][-1].content + Fore.RESET)
        
