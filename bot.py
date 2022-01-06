import json
import os
import platform
import disnake

from datetime import datetime
from disnake import ApplicationCommandInteraction
from disnake.ext import tasks, commands
from disnake.ext.commands import Bot
from message_send import bot_send


with open("config.json") as file:
    config = json.load(file)

intents = disnake.Intents.default()
bot = Bot(command_prefix=config["prefix"], intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"disnake API version: {disnake.__version__}")
    print(f"Python version: {platform.python_version()}")
    print("-" * 20)
    await bot.change_presence(activity=disnake.Game("plz help"))

bot.remove_command("help")

@bot.event
async def on_message(message: disnake.Message):
    if message.author == bot.user or message.author.bot:
        return
    if message.content.lower() == "uwu":
        await bot_send(message.channel, f"did someone say uwu? you're very uwu {message.author.mention} :)")
    else:
        await bot.process_commands(message)


@bot.event
async def on_slash_command(interaction: ApplicationCommandInteraction):
    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Executed {interaction.data.name} by {interaction.author} at {curr_time}")


@bot.event
async def on_command_completion(ctx):
    command = ctx.command.qualified_name.split()[0]
    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Executed {command} by {ctx.message.author} at {curr_time}")


if __name__ == "__main__":
    for file in [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]:
        bot.load_extension(f"cogs.{file}")
        print(f"Loaded {file}")
    bot.run(config["token"])
