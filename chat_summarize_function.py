import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from datetime import datetime, time

from prompt_template import prompt_template

load_dotenv()

# ==========================================
# summarize chat
# ==========================================

class State(TypedDict):
    ctx: any
    messages: str
    start_date: str
    end_date: str
    summarized_message: str

llm = ChatOllama(model=os.getenv('MODEL'))

summarization_prompt = ChatPromptTemplate.from_template(prompt_template.prompt + 
    '''
        Your job is to summarize the given messages.
        Do no skip on any details.
        Only outputs the summarized message and nothing else.
        

        Summarize this message: {messages}
    '''
)

async def get_messages(State) -> dict:
    start_date = State["start_date"]
    end_date = State["end_date"]
    ctx = State["ctx"]

    start_d = datetime.strptime(start_date.strip(), '%Y-%m-%d').date()
    end_d = datetime.strptime(end_date.strip(), '%Y-%m-%d').date()

    start_time = datetime.combine(start_d, time(0, 0, 0))
    end_time = datetime.combine(end_d, time(23, 59, 59))

    messages = []
    
    async for message in ctx.channel.history(after=start_time, before=end_time, limit=2000):
        if message.author.bot:
            continue
        
        messages.append(f"{message.author.display_name}: {message.content}")
    
    messages.reverse()
    formatted_message = "\n".join(messages)

    return {"messages": formatted_message}

def summarize(State):
    message = summarization_prompt.invoke({"messages": State["messages"]})

    response = llm.invoke(message)

    return {"summarized_message": response.content}

builder = StateGraph(State)

builder.add_node("get_messages", get_messages)
builder.add_node("summarize_messages", summarize)

builder.add_edge(START, "get_messages")
builder.add_edge("get_messages", "summarize_messages")
builder.add_edge("summarize_messages", END)

graph = builder.compile()

async def summarize_messages(ctx: any, start_date: str, end_date: str):
    response = await graph.ainvoke({"ctx": ctx, "start_date": start_date, "end_date": end_date})

    return response["summarized_message"]

if __name__ == "__main__":
    print("placeholder")