import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from prompt_template import prompt_template

load_dotenv()

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

def ask_tazuna(State):
    user_prompt = State["question"]
    
    message = prompt.invoke(user_prompt)

    response = llm.invoke(message)

    return {"answer": response.content}


builder = StateGraph(State)
builder.add_node("ask", ask_tazuna)

builder.add_edge(START, "ask")
builder.add_edge("ask", END)

graph = builder.compile()

def ask(user_input):
    response = graph.invoke({"question": user_input})

    return response["answer"]

if __name__ == "__main__":
    print(ask("Who are you?"))