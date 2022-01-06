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
    em.add_field(name = "Very useful", value = "dict | journal | reddit | weather | word | remind | findword | showfunction", inline=False)
    em.add_field(name = "Media", value = "audio | image | text | video | meme", inline=False)
    em.add_field(name = "Play music", value = "play | leave | pause | resume | skip | queue | clearqueue | stop | volume | currentvolume", inline=False)
    em.add_field(name = "GPT3 AI", value = "aigenerate | aianswer | aicode | aiad | aianalogy | aiengrish", inline=False)
    em.add_field(name = "Other text generation", value = "gptj | j1", inline=False)
    em.add_field(name = "Colour", value = "colour | colourlist | namecolour | showcolour", inline=False)
    em.add_field(name = "Not 100% bs", value = "no | asdlkj | answer | cut | delete | guess | staats | number | randomword | execute", inline=False)
    em.add_field(name = "100% bs", value = "aeoo | goodbot | badbot | me | sorry | whOMEGALUL | epicshit", inline=False)
    await ctx.send(embed = em)

@help.command()
async def fap(ctx):
    em = discord.Embed(title = "fap", description = "When horny. Or not.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "fap [folder]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def kawaii(ctx):
    em = discord.Embed(title = "kawaii", description = "Like fap but less lewd.", color=ctx.author.color)
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

@help.command()
async def EEE(ctx):
    em = discord.Embed(title = "EEE", description = "Sends subaru_scream.mp4", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "EEE", inline=False)
    await ctx.send(embed = em)

@help.command()
async def AAAEEE(ctx):
    em = discord.Embed(title = "AAAEEE", description = "Sends EoE_ptsd.mp4", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "AAAEEE", inline=False)
    await ctx.send(embed = em)

@help.command()
async def dict(ctx):
    em = discord.Embed(title = "dict", description = "Dictionary", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "dict <word> <synonyms/antonyms/define>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def journal(ctx):
    em = discord.Embed(title = "journal", description = "Private shit, you can't use it anyway.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "journal [word] [count/allinfo/random]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def reddit(ctx):
    em = discord.Embed(title = "reddit", description = "Send a post from a given subreddit", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "reddit <subreddit> [text]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def weather(ctx):
    em = discord.Embed(title = "weather", description = "Shows weather info. Example: 'weather temperature' or 'weather in Bratislava'.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "weather [info]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def word(ctx):
    em = discord.Embed(title = "word", description = "Local dictionary", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "word [list/define word/add word : definition]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def remind(ctx):
    em = discord.Embed(title = "remind", description = "Sents a message later", color=ctx.author.color)
    em.add_field(name = "**Syntax example**", value = "remind 1 hour 5 minutes MESSAGE /repeat/>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def findword(ctx):
    em = discord.Embed(title = "findword", description = "Finds a word that begins/ends with <word_part>", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "findword <begins/ends> <word_part>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def showfunction(ctx):
    em = discord.Embed(title = "showfunction", description = "Shows the code of a function of the bot", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "showfunction <function>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def audio(ctx):
    em = discord.Embed(title = "audio", description = "Sends an audio file", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "audio <filename>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def image(ctx):
    em = discord.Embed(title = "image", description = "Puts text on an image. Lists images if no argument.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "image [image] [text]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def text(ctx):
    em = discord.Embed(title = "text", description = "Sends a text file.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "text <file>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def video(ctx):
    em = discord.Embed(title = "video", description = "Sends a video. Lists videos if no argument.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "video [file_name]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def meme(ctx):
    em = discord.Embed(title = "meme", description = "Sends a random meme.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "meme", inline=False)
    await ctx.send(embed = em)

@help.command()
async def play(ctx):
    em = discord.Embed(title = "play", description = "Joins a voice channel and plays a Spotify song/playlist or searches YouTube.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "play <song> [vol={num}]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def leave(ctx):
    em = discord.Embed(title = "leave", description = "Leaves the current voice channel.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "leave", inline=False)
    await ctx.send(embed = em)

@help.command()
async def pause(ctx):
    em = discord.Embed(title = "pause", description = "Pauses the current playing song.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "pause", inline=False)
    await ctx.send(embed = em)

@help.command()
async def resume(ctx):
    em = discord.Embed(title = "resume", description = "Resumes currently paused song.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "resume", inline=False)
    await ctx.send(embed = em)

@help.command()
async def skip(ctx):
    em = discord.Embed(title = "skip", description = "Skips the current song.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "skip", inline=False)
    await ctx.send(embed = em)

@help.command()
async def queue(ctx):
    em = discord.Embed(title = "queue", description = "Shows the song queue.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "queue", inline=False)
    await ctx.send(embed = em)

@help.command()
async def clearqueue(ctx):
    em = discord.Embed(title = "clearqueue", description = "Clears the song queue.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "clearqueue", inline=False)
    await ctx.send(embed = em)

@help.command()
async def stop(ctx):
    em = discord.Embed(title = "stop", description = "Stops playing the current song. Can't be resumed.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "stop", inline=False)
    await ctx.send(embed = em)

@help.command()
async def volume(ctx):
    em = discord.Embed(title = "volume", description = "Changes the volume, from 0 to 100.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "volume <number>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def currentvolume(ctx):
    em = discord.Embed(title = "currentvolume", description = "Shows the current volume.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "currentvolume", inline=False)
    await ctx.send(embed = em)

@help.command()
async def aigenerate(ctx):
    em = discord.Embed(title = "aigenerate", description = "Generates text from a prompt.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "aigenerate <prompt>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def aiainswer(ctx):
    em = discord.Embed(title = "aiainswer", description = "Answers the question.. well, tries to.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "aiainswer <prompt>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def aicode(ctx):
    em = discord.Embed(title = "aicode", description = "Generates code based on the prompt. For example a function.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "aicode <prompt>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def aiad(ctx):
    em = discord.Embed(title = "aiad", description = "Generates an ad based on the description.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "aiad <prompt>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def aianalogy(ctx):
    em = discord.Embed(title = "aianalogy", description = "Writes an analogy. Write 'X is like Y'.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "aianalogy <prompt>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def aiengrish(ctx):
    em = discord.Embed(title = "aiengrish", description = "Translates broken English into proper English.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "aiengrish <prompt>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def colour(ctx):
    em = discord.Embed(title = "colour", description = "Sends an image of a random colour.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "colour", inline=False)
    await ctx.send(embed = em)

@help.command()
async def colourlist(ctx):
    em = discord.Embed(title = "colourlist", description = "Sends a list of named colours.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "colourlist", inline=False)
    await ctx.send(embed = em)

@help.command()
async def namecolour(ctx):
    em = discord.Embed(title = "namecolour", description = "Names the last generated colour.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "namecolour <name>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def showcolour(ctx):
    em = discord.Embed(title = "showcolour", description = "Sends an image of the given colour.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "showcolour <name>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def no(ctx):
    em = discord.Embed(title = "no", description = "Sends 30 empty lines (if you don't want to see something).", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "no", inline=False)
    await ctx.send(embed = em)

@help.command()
async def asdlkj(ctx):
    em = discord.Embed(title = "asdlkj", description = "Sends 2000 random characters.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "asdlkj", inline=False)
    await ctx.send(embed = em)
    
@help.command()
async def answer(ctx):
    em = discord.Embed(title = "answer", description = "Magic 8-ball.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "answer <question>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def cut(ctx):
    em = discord.Embed(title = "cut", description = "Splits the message into multiple lines.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "cut <text>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def delete(ctx):
    em = discord.Embed(title = "delete", description = "Deletes the last [num] messages of certain functions. Set [num] to '-1' to delete all messages.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "delete [num]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def guess(ctx):
    em = discord.Embed(title = "guess", description = "Higher/lower guessing game. Generated number is from 0 to 10000.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "guess <num>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def staats(ctx):
    em = discord.Embed(title = "staats", description = "Stats the 'a' function. Percentage of full-length A-s. Argument 'all' for everyone's stats.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "staats [all]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def number(ctx):
    em = discord.Embed(title = "number", description = "Guess a number from 1 to 100.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "number <num>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def randomword(ctx):
    em = discord.Embed(title = "randomword", description = "Sends a random word from a dictionary.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "randomword", inline=False)
    await ctx.send(embed = em)

@help.command()
async def execute(ctx):
    em = discord.Embed(title = "execute", description = "Executes a piece of code. Send without argument for further explanation.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "execute [code]", inline=False)
    await ctx.send(embed = em)

@help.command()
async def aeoo(ctx):
    em = discord.Embed(title = "aeoo", description = "Sends a spook sound from Re:Zero.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "aeoo", inline=False)
    await ctx.send(embed = em)

@help.command()
async def goodbot(ctx):
    em = discord.Embed(title = "goodbot", description = "Compliments spaghett.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "goodbot", inline=False)
    await ctx.send(embed = em)

@help.command()
async def badbot(ctx):
    em = discord.Embed(title = "badbot", description = "Don't you dare.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "badbot", inline=False)
    await ctx.send(embed = em)

@help.command()
async def me(ctx):
    em = discord.Embed(title = "me", description = "Sends your name.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "me", inline=False)
    await ctx.send(embed = em)

@help.command()
async def sorry(ctx):
    em = discord.Embed(title = "sorry", description = "Sends a heartfelt apology.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "sorry <name>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def whOMEGALUL(ctx):
    em = discord.Embed(title = "whOMEGALUL", description = "Sends a random video making fun of Rem disappearing.", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "whOMEGALUL", inline=False)
    await ctx.send(embed = em)

@help.command()
async def epicshit(ctx):
    em = discord.Embed(title = "epicshit", description = "Just follow the instructions", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "epicshit", inline=False)
    await ctx.send(embed = em)

@help.command()
async def gptj(ctx):
    em = discord.Embed(title = "gptj", description = "Continues generation from input", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "gtpj <input>", inline=False)
    await ctx.send(embed = em)

@help.command()
async def j1(ctx):
    em = discord.Embed(title = "j1", description = "Continues generation from input", color=ctx.author.color)
    em.add_field(name = "**Syntax**", value = "j1 <input>", inline=False)
    await ctx.send(embed = em)
