import os
import discord
from discord.ext import commands
from typing import Annotated
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

# ==========================================
# 1. SETUP LANGGRAPH & OLLAMA
# ==========================================

# Define the state structure. Since we don't need history,
# we only pass the current prompt and the final response.
class BotState(TypedDict):
    prompt: str
    response: str

# Initialize the Ollama LLM wrapper
llm = ChatOllama(model="llama3.1:8b", temperature=0.7)

# Define the node function that processes the message
def call_llama(state: BotState):
    user_prompt = state["prompt"]
    
    # Invoke the model directly without past memory array
    ai_message = llm.invoke(user_prompt)
    
    return {"response": ai_message.content}

# Compile the LangGraph
workflow = StateGraph(BotState)
workflow.add_node("llama_agent", call_llama)

# Define simple workflow structure: START -> llama_agent -> END
workflow.add_edge(START, "llama_agent")
workflow.add_edge("llama_agent", END)

app = workflow.compile()


# ==========================================
# 2. SETUP DISCORD BOT
# ==========================================

# Configure intents (Message Content intent is required to read prompts)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

@bot.command(name="ask")
async def ask_llama(ctx, *, user_input: str):
    """
    Triggers the Llama model via LangGraph using: !ask <your question>
    """
    # Trigger typing indicator so users know the local LLM is thinking
    async with ctx.typing():
        try:
            # Execute the LangGraph workflow
            inputs = {"prompt": user_input}
            result = app.invoke(inputs)
            
            output_text = result["response"]
            print(output_text)
            
            # Discord has a 2000 character limit per message. 
            # We truncate it here as a safety measure.
            if len(output_text) > 2000:
                output_text = output_text[:1997] + "..."
                
            await ctx.reply(output_text)
            
        except Exception as e:
            print(f"Error invoking LangGraph/Ollama: {e}")
            await ctx.reply("Sorry, I ran into an error processing that request.")

# Run the bot (Replace with your actual Discord Bot Token)
# DO NOT hardcode this in production; use environment variables!
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)