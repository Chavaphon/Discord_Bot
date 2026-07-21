import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from config.prompt_template import PromptTemplate

load_dotenv()

class State(TypedDict):
    text: str
    designated_language: str
    translation: str
    source_language: str

class structure(BaseModel):
    source_language: str = Field(description="the language of the original text")
    translation: str = Field(description="translated text")

llm = ChatOllama(model=os.getenv("MODEL"))

prompt = ChatPromptTemplate.from_template(PromptTemplate.prompt + 
    """
        You are also a translater that translate the given text to the given language.

        text: {text}
        language: {designated_language}
    """
)

def translation(state: State) -> dict:
    message = prompt.invoke({"text" : state["text"], "designated_language": state["designated_language"]})

    structured_llm = llm.with_structured_output(structure)

    response = structured_llm.invoke(message)

    return {"source_language": response.source_language, "translation": response.translation}

builder = StateGraph(State)

builder.add_node("translation", translation)

builder.add_edge(START, "translation")

builder.add_edge("translation", END)

graph = builder.compile()

def translate(text: str, language: str) -> list:
    response = graph.invoke({"text": text, "designated_language": language})

    return [response["source_language"], response["translation"]]
