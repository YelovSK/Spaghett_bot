import json
import time
import disnake
from platform import python_version
from os import listdir
from pathlib import Path
from os.path import join as pjoin
from datetime import datetime
from disnake.ext import commands
from disnake.ext.commands import Bot
from helpers.message_send import bot_send

with open("config.json") as cfg:
    config = json.load(cfg)
intents = disnake.Intents.default()
intents.members = True
intents.presences = True
bot = Bot(command_prefix=config["prefix"], intents=intents)
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


@bot.event
async def on_command_error(ctx, error) -> None:
    if isinstance(error, commands.MissingPermissions):
        embed = disnake.Embed(
            title="Error!",
            description=f"Missing permissions: `{', '.join(error.missing_permissions)}`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(error)
    else:
        raise error


@bot.event
async def on_presence_update(before: disnake.Member, after: disnake.Member):
    channel = bot.get_channel(config["ids"]["main_guild"])
    if before.guild != channel.guild:   # check only in the main guild (a member can be in multiple guilds)
        return
    bad_games = ("league of legends")
    if after.activity and after.activity.name.lower() in bad_games:
        await bot_send(channel, f"beware, {before.mention} just launched {after.activity.name}, yikes")
        await activity_timer(member=after, channel=channel, timeout=30)


async def activity_timer(member: disnake.Member, channel, timeout: int):
    """checks if the activity hasn't changed for <timeout> minutes"""
    start_activity: disnake.Activity = member.activity
    time.sleep(timeout * 60)
    if member.activity == start_activity:
        await bot_send(channel, f"{member.mention} still playing {member.activity.name} after {timeout} minutes :feelsweird:")
        # await member.ban(delete_message_days=0, reason=f"playing {member.activity.name}")   # (:


def check_folders():
    for folder in ("assets", "imgs", "memes", "send/kawaii", "send/videos", "text"):
        Path(pjoin("folders", folder)).mkdir(parents=True, exist_ok=True)


def load_extensions():
    for file in [f[:-3] for f in listdir("./cogs") if f.endswith(".py")]:
        try:
            bot.load_extension(f"cogs.{file}")
            print(f"Loaded {file}")
        except Exception as e:
            print(f"Failed loading {file} -> {e}")


if __name__ == "__main__":
    check_folders()
    load_extensions()
    bot.run(config["token"])
