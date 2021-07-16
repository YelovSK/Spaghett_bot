import discord
from discord.ext import commands
from discord_slash import SlashCommand


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = 'plz ', intents=intents)
client.remove_command("help")
slash = SlashCommand(client, sync_commands=True)


@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title = "Help", description = "<plz help> + [command] for additional info.\n<argument> is necessary | [argument] is optional", color=ctx.author.color)
    em.add_field(name = "Degenerate", value = "fap | kawaii | coomer", inline=False)
    em.add_field(name = "Bad", value = "insult | fuck | f | addf | a | deth | AAA | EEE | AAAEEE ", inline=False)
    em.add_field(name = "Very useful", value = "dict | journal | reddit | weather | word | remind", inline=False)
    em.add_field(name = "Media", value = "audio | image | text | video | meme", inline=False)
    em.add_field(name = "Colour", value = "colour | colourlist | namecolour | showcolour", inline=False)
    em.add_field(name = "Not 100% bs", value = "no | asdlkj | answer | cut | delete | guess | number | randomword | staats", inline=False)
    em.add_field(name = "100% bs", value = "aeoo | goodbot | badbot | me | sorry | whOMEGALUL", inline=False)
    await ctx.send(embed = em)

@help.command()
async def fap(ctx):
    em = discord.Embed(title = "fap", description = "When horny. Or not.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "fap [folder]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def kawaii(ctx):
    em = discord.Embed(title = "kawaii", description = "Like fap, less lewd.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "kawaii [cum] [image]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def coomer(ctx):
    em = discord.Embed(title = "coomer", description = "Random image from a random nsfw subreddit.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "coomer", inline=False)
    await ctx.send(embed = em)

@help.command()
async def insult(ctx):
    em = discord.Embed(title = "insult", description = "Randomly generated insult. Argument is username, not nick.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "insult <username>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def fuck(ctx):
    em = discord.Embed(title = "fuck", description = "Random swear word.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "fuck", inline=False)
    await ctx.send(embed = em)

@help.command()
async def f(ctx):
    em = discord.Embed(title = "f", description = "Random sad/angry message.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "f", inline=False)
    await ctx.send(embed = em)

@help.command()
async def addf(ctx):
    em = discord.Embed(title = "addf", description = "Adds message to the f list.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "f <*message>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def a(ctx):
    em = discord.Embed(title = "a", description = "Prints 4-20 A-s. Keeps track of stats with staats.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "a", inline=False)
    await ctx.send(embed = em)

@help.command()
async def deth(ctx):
    em = discord.Embed(title = "deth", description = "Sends Komm Susser Tod.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "deth", inline=False)
    await ctx.send(embed = em)

@help.command()
async def AAA(ctx):
    em = discord.Embed(title = "AAA", description = "Sends shinji_scream.mp4", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "AAA", inline=False)
    await ctx.send(embed = em)