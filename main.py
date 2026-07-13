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