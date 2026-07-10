import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from ask_function import ask

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

@bot.command(name="ask")
async def ask_tazuna(ctx, *, user_input: str):
    async with ctx.typing():
        try:
            output_text = ask(user_input)
            await ctx.reply(output_text)

        except Exception as e:
            print(f"Error invoking Tazuna: {e}")
            await ctx.reply("Sorry, I ran into an error processing that request.")

# Run the bot (Replace with your actual Discord Bot Token)
# DO NOT hardcode this in production; use environment variables!
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)