import os
from dotenv import load_dotenv

from typing import Annotated, Literal, List
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

import discord
from discord.ext import commands

from ask_function import ask

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class State(TypedDict):
    request: str
    response: str

class Reason(BaseModel):
    use: Literal["ask"]

llm = ChatOllama(model=os.getenv('MODEL'))

prompt = ChatPromptTemplate.from_template(
    '''
        You are a helpful assistant.
        You come equip with tools to use to help with the user's request.

        Here are the descriptions of your tools:
        ask: use when the user's request can be answered with knowledge before 1st December 2023

        Your job is to determine which tool to use based on the user's request

        user's request: {request}

        What tool will you use?
    '''

)

def determine(State) -> dict:
    message = prompt.invoke({"request" : State["request"]})

    structured_llm = llm.with_structured_output(Reason)

    response = structured_llm.invoke(message)

    return response.use

def tool_ask(State) -> dict:
    return {"response": ask(State["request"])}

builder = StateGraph(State)

builder.add_node('tool_ask', tool_ask)

builder.add_conditional_edges(START, determine, {"ask": 'tool_ask'})

builder.add_edge('tool_ask', END)

graph = builder.compile()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

@bot.command(name="t")
async def ask_tazuna(ctx, *, user_input: str):
    async with ctx.typing():
        try:
            output_text = graph.invoke({"request": user_input})
            await ctx.reply(output_text["response"])

        except Exception as e:
            print(f"Error invoking Tazuna: {e}")
            await ctx.reply("Sorry, I ran into an error processing that request.")

# Run the bot (Replace with your actual Discord Bot Token)
# DO NOT hardcode this in production; use environment variables!
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)