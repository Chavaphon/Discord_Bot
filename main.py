import os
from dotenv import load_dotenv

from typing import Annotated, Literal, List
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from datetime import datetime, time

import discord
from discord.ext import commands

from help_message import help_message
from ask_function import ask
from helper_function import helper_chunk
from chat_summarize_function import summarize_messages

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

# ==========================================
# !help
# ==========================================
@bot.command(name="help")
async def ask_tazuna(ctx):
    async with ctx.typing():
        try:
            await ctx.reply(help_message.message)
            
            print("Task completed!")

        except Exception as e:
            print(f"Error invoking Tazuna: {e}")
            await ctx.reply("Sorry, I ran into an error processing that request.")

# ==========================================
# !ask
# ==========================================
# class State(TypedDict):
#     request: str
#     response: str

# class Reason(BaseModel):
#     use: Literal["ask", "search",]

# llm = ChatOllama(model=os.getenv('MODEL'))

# prompt = ChatPromptTemplate.from_template(
#     '''
#         You are a helpful assistant equipped with tools to help with the user's request.

#         Here are the descriptions of your tools:
#         ask: Use when the request relies entirely on static facts, history, 
#         or knowledge that does not change over time before 1st December 2023.

#         search: Use when the request requires real-time information, current events, 
#         or calculations dependent on the current date and time.

#         Your job is to determine which tool to use based on the user's request.

#         User's request: {request}

#         What tool will you use? 
#     '''
# )

# def determine(State) -> dict:
#     message = prompt.invoke({"request" : State["request"]})

#     structured_llm = llm.with_structured_output(Reason)

#     response = structured_llm.invoke(message)

#     return response.use

# def tool_ask(State) -> dict:
#     print("using tool_ask...")
#     return {"response": ask(State["request"])}

# def tool_search(State) -> dict:
#     print("using tool_search...")
#     return {"response": search(State["request"])}

# builder = StateGraph(State)

# builder.add_node("tool_ask", tool_ask)
# builder.add_node("tool_search", tool_search)

# builder.add_conditional_edges(START, determine, {"ask": "tool_ask", "search": "tool_search"})

# builder.add_edge("tool_ask", END)
# builder.add_edge("tool_search", END)

# graph = builder.compile()

@bot.command(name="ask")
async def ask_tazuna(ctx, *, user_input: str):
    async with ctx.typing():
        try:
            output_text = ask(user_input=user_input)

            if len(output_text) > 2000:
                print("chunking...")
                await ctx.reply("Give me one moment, please.")
                
                chunked_output = helper_chunk(output_text)
                for ele in chunked_output:
                    await ctx.reply(ele)
            else:
                await ctx.reply(output_text)
            
            print("Task completed!")

        except Exception as e:
            print(f"Error invoking Tazuna: {e}")
            await ctx.reply("Sorry, I ran into an error processing that request.")

# ==========================================
# !summarize
# ==========================================
@bot.command(name="summarize")
async def summarize_tazuna(ctx, *, user_input: str):
    async with ctx.typing():
        try:
            start_date, end_date = user_input.split("|")
            output_text = await summarize_messages(ctx=ctx, start_date=start_date.strip(), end_date=end_date.strip())

            if len(output_text) > 2000:
                print("chunking...")
                await ctx.reply("Give me one moment, please.")
                
                chunked_output = helper_chunk(output_text)
                for ele in chunked_output:
                    await ctx.reply(ele)
            else:
                await ctx.reply(output_text)
            
            print("Task completed!")

        except Exception as e:
            print(f"Error invoking Tazuna: {e}")
            await ctx.reply("Sorry, I ran into an error processing that request.")

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    bot.run(TOKEN)