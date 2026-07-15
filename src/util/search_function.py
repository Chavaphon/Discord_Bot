import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from langchain_tavily import TavilySearch

from config.prompt_template import PromptTemplate

load_dotenv()

class State(TypedDict):
    question: str
    context: str
    answer: str

llm = ChatOllama(model=os.getenv("MODEL"))

prompt = ChatPromptTemplate.from_template(PromptTemplate.prompt + 
    """
        You are also a helpful guide who answers the question using ONLY information from the context.

        Context: {context}

        Question: {question}
    """
)

def fetch_information(state: State) -> dict:
    query = state["question"]

    search_tool = TavilySearch(max_results=3)
    response = search_tool.invoke({"query": query})

    return {"context": str(response["results"])}

def answer(state: State) -> dict:
    message = prompt.invoke({"context": state["context"], "question": state["question"]})

    response = llm.invoke(message)

    return {"answer": response.content}

builder = StateGraph(State)

builder.add_node("fetch_information", fetch_information)
builder.add_node("answer", answer)

builder.add_edge(START, "fetch_information")
builder.add_edge("fetch_information", "answer")
builder.add_edge("answer", END)

graph = builder.compile()

def search(user_input: str):
    response = graph.invoke({"question": user_input})

    return response["answer"]
