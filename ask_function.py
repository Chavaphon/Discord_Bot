import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ==========================================
# ask Tazuna
# ==========================================
class State(TypedDict):
    prompt: str
    response: str

llm = ChatOllama(model=os.getenv('MODEL'))

# Define the node function that processes the message
def call_llama(state: State):
    user_prompt = state["prompt"]
    
    # Invoke the model directly without past memory array
    ai_message = llm.invoke(user_prompt)
    
    return {"response": ai_message.content}

# Compile the LangGraph
workflow = StateGraph(State)
workflow.add_node("llama_agent", call_llama)

# Define simple workflow structure: START -> llama_agent -> END
workflow.add_edge(START, "llama_agent")
workflow.add_edge("llama_agent", END)

app = workflow.compile()

def ask(user_input):
    inputs = {"prompt": user_input}
    result = app.invoke(inputs)
    
    output_text = result["response"]

    return output_text

if __name__ == "__main__":
    print(ask("What is 1 + 1?"))