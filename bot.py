import json
import disnake
from platform import python_version
from os import listdir
from datetime import datetime
from disnake.ext.commands import Bot
from message_send import bot_send

with open("config.json") as cfg:
    config = json.load(cfg)
bot = Bot(command_prefix=config["prefix"])
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"disnake API version: {disnake.__version__}")
    print(f"Python version: {python_version()}")
    print("-" * 20)
    await bot.change_presence(activity=disnake.Game("plz help"))


@bot.event
async def on_message(message: disnake.Message):
    if message.author == bot.user or message.author.bot:
        return
    if message.content.lower() == "uwu":
        await bot_send(message.channel, f"did someone say uwu? you're very uwu {message.author.mention} :)")
        await bot_send(message.channel, message.author.avatar.url)
    else:
        await bot.process_commands(message)


@bot.event
async def on_slash_command(interaction: disnake.ApplicationCommandInteraction):
    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Executed {interaction.data.name} by {interaction.author} at {curr_time}")


@bot.event
async def on_command_completion(ctx):
    command = ctx.command.qualified_name.split()[0]
    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Executed {command} by {ctx.message.author} at {curr_time}")


def load_extensions():
    for file in [f[:-3] for f in listdir("./cogs") if f.endswith(".py")]:
        try:
            bot.load_extension(f"cogs.{file}")
            print(f"Loaded {file}")
        except Exception as e:
            print(f"Failed loading {file} -> {e}")


if __name__ == "__main__":
    load_extensions()
    bot.run(config["token"])
