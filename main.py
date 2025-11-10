import langgraph
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from colorama import Fore
from typing import Annotated
from langgraph.prebuilt import ToolNode
from tool import simple_screener, crypto_screener#, stock_and_crypto_screener



SYSTEM_PROMPT = """You are a helpful financial assistant specializing in stocks and cryptocurrencies.

For STOCK screening:
- Use 'simple_screener' for US stocks (day_gainers, most_actives, etc.)
- Use 'stock_and_crypto_screener' for Indian stocks (top_gainers, top_losers, most_active, growth_stocks)

For CRYPTO screening, use 'crypto_screener' with:
- 'top_by_market_cap' - Largest cryptocurrencies
- 'top_gainers_24h' - Biggest 24h gainers
- 'top_losers_24h' - Biggest 24h losers  
- 'high_volume' - Most traded cryptocurrencies
- 'trending' - Trending/popular cryptos

Examples:
- "Show me top crypto gainers" → crypto_screener(screen_type='top_gainers_24h')
- "What are the biggest cryptocurrencies?" → crypto_screener(screen_type='top_by_market_cap')
- "Show trending cryptos" → crypto_screener(screen_type='trending')

DO NOT HALLUCINATE. Make the appropriate tool call based on the user's query."""


llm = ChatOllama(model="qwen3:8b")


tool = [simple_screener, crypto_screener,] #stock_and_crypto_screener

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
        
