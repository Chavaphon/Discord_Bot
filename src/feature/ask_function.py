import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from util.search_function import search

from config.prompt_template import PromptTemplate

load_dotenv()

class State(TypedDict):
    question: str
    answer: str

class Reason(BaseModel):
    use: Literal["ask", "search",]

llm = ChatOllama(model=os.getenv("MODEL"))

ask_prompt = ChatPromptTemplate.from_template(PromptTemplate.prompt + 
    """
        You are also a helpful guide who answers every question in a clear and concise way.

        Question: {question}
    """
)

determiner_prompt = ChatPromptTemplate.from_template(
    """
        You are a helpful assistant equipped with tools to help with the user's request.

        Here are the descriptions of your tools:
        ask: Use when the request relies entirely on static facts, history, 
        or knowledge that does not change over time before 1st December 2023.

        search: Use when the request requires real-time information, current events, 
        or calculations dependent on the current date and time.

        Your job is to determine which tool to use based on the user's request.

        User's request: {request}

        What tool will you use? 
    """
)

def determine(state: State) -> dict:
    message = determiner_prompt.invoke({"request" : state["question"]})

    structured_llm = llm.with_structured_output(Reason)

    response = structured_llm.invoke(message)

    return response.use

def tool_ask(state: State) -> dict:
    user_prompt = state["question"]
    
    message = ask_prompt.invoke(user_prompt)

    response = llm.invoke(message)

    return {"answer": response.content}

def tool_search(state: State) -> dict:
    return {"answer": search(state["question"])}

builder = StateGraph(State)

builder.add_node("tool_ask", tool_ask)
builder.add_node("tool_search", tool_search)

builder.add_conditional_edges(START, determine, {"ask": "tool_ask", "search": "tool_search"})

builder.add_edge("tool_ask", END)
builder.add_edge("tool_search", END)

graph = builder.compile()

def ask(user_input: str):
    response = graph.invoke({"question": user_input})

    return response["answer"]
