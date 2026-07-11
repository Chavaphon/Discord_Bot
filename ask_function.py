import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from prompt_template import prompt_template

load_dotenv()

# ==========================================
# ask Tazuna
# ==========================================

class State(TypedDict):
    question: str
    answer: str

llm = ChatOllama(model=os.getenv('MODEL'))

prompt = ChatPromptTemplate.from_template(prompt_template.prompt + 
    '''
        You are also a helpful guide who answers every question in a clear and concise way.

        Question: {question}
    '''

)


def call_tazuna(State):
    user_prompt = State["question"]
    
    message = prompt.invoke(user_prompt)

    response = llm.invoke(message)

    return {"answer": response.content}


builder = StateGraph(State)
builder.add_node("tazuna", call_tazuna)

builder.add_edge(START, "tazuna")
builder.add_edge("tazuna", END)

graph = builder.compile()

def ask(user_input):
    response = graph.invoke({"question": user_input})

    output_text = response["answer"]

    return output_text

if __name__ == "__main__":
    print(ask("Who are you?"))