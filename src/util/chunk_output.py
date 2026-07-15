import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from config.prompt_template import PromptTemplate

load_dotenv()

class State(TypedDict):
    text: str
    chunks: List[str]

class Chunks(BaseModel):
    chunks: List[str]

llm = ChatOllama(model=os.getenv("MODEL"), temperature=0)

prompt = ChatPromptTemplate.from_template(
    """
    Your job is to split the provided text into a list of smaller consecutive chunks.
    
    CRITICAL RULES:
    1. Do not skip, summarize, or alter any words. Every single sentence from the original text must appear in order across the chunks.
    2. Each chunk must be less than 2000 characters.
    3. Do not include chunk numbers (e.g., "Chunk 1") or introductory text.
    4. Do not add "..." at the start or end of the chunks.
    5. Return the result strictly as the requested structured list of chunks.

    text: {text}
    """
)


def chunking(state: State):
    message = prompt.invoke(state["text"])

    structured_llm = llm.with_structured_output(Chunks)

    response = structured_llm.invoke(message)

    return {"chunks": response.chunks}


builder = StateGraph(State)
builder.add_node("chunker", chunking)

builder.add_edge(START, "chunker")
builder.add_edge("chunker", END)

graph = builder.compile()

def chunk_output(text: str):
    response = graph.invoke({"text": text})

    output_text = response["chunks"]

    return output_text

if __name__ == "__main__":
    print(helper_chunk(""))