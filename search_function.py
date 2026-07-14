import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from langchain_tavily import TavilySearch

from prompt_template import prompt_template

load_dotenv()

class State(TypedDict):
    question: str
    context: str
    answer: str

llm = ChatOllama(model=os.getenv("MODEL"))

prompt = ChatPromptTemplate.from_template(prompt_template.prompt + 
    """
        You are also a helpful guide who answers the question using ONLY information from the context.

        Context: {context}

        Question: {question}
    """
)

def fetch_information(State) -> dict:
    query = State["question"]

    search_tool = TavilySearch(max_results=3)
    response = search_tool.invoke({"query": query})

    return {"context": str(response["results"])}

def answer(State) -> dict:
    message = prompt.invoke({"context": State["context"], "question": State["question"]})

    response = llm.invoke(message)

    return {"answer": response.content}

builder = StateGraph(State)

builder.add_node("fetch_information", fetch_information)
builder.add_node("answer", answer)

builder.add_edge(START, "fetch_information")
builder.add_edge("fetch_information", "answer")
builder.add_edge("answer", END)

graph = builder.compile()

def search(user_input):
    response = graph.invoke({"question": user_input})

    return response["answer"]

if __name__ == "__main__":
    print(search("how many days until Halloween"))
