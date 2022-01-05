import openai
import praw
import asyncio
import contextlib
import math
import os
import random
import re
import shelve
import sys
import time
import requests
import urllib.request
import json
import soundfile as sf

from os.path import join as pjoin
from datetime import timezone
from decimal import Decimal
from io import StringIO
from pathlib import Path
from espnet2.bin.tts_inference import Text2Speech
from PIL import Image, ImageDraw, ImageFont
from PyDictionary import PyDictionary
from pyowm.owm import OWM
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from youtubesearchpython import Video, VideosSearch
from collections import Counter

from help import *

stop = False
remindrun = False
users_allowed = open(pjoin("folders", "text", "users_allowed.txt")).read().splitlines()
song_queue = []
current_song = ''
text2speech_model = None
curr_colour = None
keys = {}
with open("ClientKey.txt") as f:
    for line in f:
        key, val = line.strip().split()
        keys[key] = val


def split_long(text):    # todo formatting breaks if split at **word
    mssgs = []
    for _ in range((len(text) // 2000) + 1):
        mssgs.append(text[:2000])
        text = text[2000:]
    if text:
        mssgs.append(text)
    return mssgs

async def my_send(context, mssg):
    if type(mssg) == discord.File:
        sent_mssg = await context.send(file = mssg)
    elif len(mssg) > 2000:
        for m in split_long(mssg):
            await my_send(context, m)
        return
    else:
        sent_mssg = await context.send(mssg)
    mssg_id, channel_id = sent_mssg.id, sent_mssg.channel.id
    with open(pjoin("folders", "text", "prev_mssg_ids.txt"), "a") as f:
        f.write(f'{channel_id} {mssg_id}\n')

# @slash.slash(description='example: 1 hour 5 minutes <message> /repeat/')
@client.command(pass_context=True)
async def remind(ctx, *, string):
    global stop
    global remindrun
    split = string.split()
    send = ''
    repeat = split[-1] == '/repeat/'
    if split[1] in ('hours', 'hour'):
        when = float(split[0])
        min = False
    elif split[1] in ('minute', 'minutes'):
        when = int(split[0])
        min = True
    for prvok in split[2:]:
        if repeat and prvok == split[-1]:
            break
        send += f'{prvok} '
    if min:
        await my_send(ctx, f'Reminding in {when} minutes')
        mul = 60
    else:
        if when % 1 == 0:
            await my_send(ctx, f'Reminding in {round(when)} hours')
        else:
            await my_send(ctx, f'Reminding in {round(when // 1)}h{round((when % 1) * 60)}m')
        mul = 3600
    remindrun = True
    if repeat:
        stop = False
        for _ in range(100):
            if stop:
                break
            await asyncio.sleep(round(when * mul))
            await my_send(ctx, send)
    else:
        await asyncio.sleep(round(when * mul))
        await my_send(ctx, send)
        remindrun = False


# @slash.slash(description='is timer active?')
@client.command(pass_context=True)
async def remind_active(ctx):
    if remindrun:
        await my_send(ctx, 'Ye')
    else:
        await my_send(ctx, 'Nah')


# @slash.slash(description='stops timer')
@client.command(pass_context=True)
async def remind_stop(ctx):
    global stop
    print('Stopped reminder')
    stop = True


# @slash.slash(description='guess num from 1 to 100')
@client.command(pass_context=True)
async def number(ctx, *, num):
    good = []
    bad = []
    with open(pjoin("folders", "text", "num_answers.txt")) as f:
        adding_good = True
        for line in f:
            line = line[:-1]
            if line == "bad":
                adding_good = False
            elif line != "good":
                if adding_good:
                    good.append(line)
                else:
                    bad.append(line)
    if not num.isnumeric():
        await my_send(ctx, f'Ah yes, {num} - the perfect "num". Moron.')
        return
    num_int = int(num)
    cis = random.randint(1, 100)
    ans = random.choice(good) if num_int == cis else random.choice(bad)
    await my_send(ctx, f'Guessed {num}\n{ans}')
    print(f'Guessed {num}, was {cis}')


# @slash.slash(description='"list" / "add "word" / "define" <word : definition>')
@client.command(pass_context=True)
async def word(ctx, do='', *, word=''):
    dick = {}
    if len(word.split()) > 1:
        word, definition = word.split(':')
        word.strip()
        definition.strip()

    dictionary_path = pjoin("folders", "text", "dictionary.txt")
    if not do:
        await my_send(ctx, '"list" / "define <word>" / "add <word : definition>"')
    elif do in 'add':
        with open(dictionary_path, 'r') as file:
            for line in file:
                index = line.find(':')
                dick[line[:index-1]] = line[index+2:]

        if word not in dick.keys():
            with open(dictionary_path, 'a') as file:
                file.write(f'{word}:{definition}\n')
                print(f'Added {word}')

    elif do == 'define':
        with open(dictionary_path, 'r') as file:
            for line in file:
                index = line.find(':')
                if line[:index-1] == word:
                    await my_send(ctx, f'Definition of {word} -> {line[index+2:]}')

    elif do == 'list':
        send = ''

        with open(dictionary_path, 'r') as file:
            for line in file:
                index = line.find(':')
                send += f'{line[:index-1]}\n'
        await my_send(ctx, send)


# @slash.slash(description='<image name> <text> / img list when no argument')
@client.command(pass_context=True)
async def image(ctx, img_name='', *, text=''):
    if not img_name:
        path = pjoin("folders", "imgs")
        files = [f[:-4] for f in os.listdir(path) if os.path.isfile(pjoin(path, f))]
        send = "\n".join(files)
        await my_send(ctx, 'Send with <image_name> <text>')
        await my_send(ctx, f'Image list:\n{send}')
        return

    basewidth = 1200
    for ext in (".png", ".jpg", ".bmp", ".jpeg"):
        curr_path = pjoin("folders", "imgs", img_name + ext)
        if os.path.exists(curr_path):
            img = Image.open(curr_path)
            break

    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    draw = ImageDraw.Draw(img)

    message = ' '.join(list(text))

    char_count = len(message)
    for offset, col in ((230, "black"), (200, "white")):
        font = ImageFont.truetype("font.ttf", int((basewidth + offset) / ((char_count / 2) + 4)))
        fontsize = int((basewidth + offset) / ((char_count / 2) + 3))
        w, _ = draw.textsize(message, font=font)
        draw.text(((img.width-w) / 2, img.height - (fontsize / 1.2) - 30), message, font=font, fill=col)
    img.save(pjoin("folders", "send", "meme.png"))

    file = discord.File(pjoin("folders", "send", "meme.png"), filename=pjoin("folders", "send", "meme.png"))
    await my_send(ctx, file)


# @slash.slash(description='random fap image, can be sent with <folder_name>')
@client.command(pass_context=True)
async def fap(message, *, folder=''):
    if not folder:
        folders = open(pjoin("folders", "text", "fap.txt")).read().splitlines()
        folder = random.choice(folders)

    path = pjoin("F:\\Desktop start menu", "homework", folder)
    files = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f)) if os.path.getsize(pjoin(path, f)) < 8_000_000]
    file_path = pjoin("folders", "send", "homework.png")
    Image.open(pjoin(path, random.choice(files))).save(file_path)
    file = discord.File(file_path, filename=file_path)
    await my_send(message.channel, f'****Folder:**** {folder}')
    try:
        await my_send(message, file)
    except Exception as error:
        await my_send(message, 'oopsie, failed to upload, error kodiQ: ' + str(error))


# # @slash.slash(description='[plz delete <msg_num>] no argument deletes all messages')
@client.command(pass_context=True)
async def delete(message, num=1):
    prev_messages = []
    with open(pjoin("folders", "text", "prev_mssg_ids.txt")) as f:
        for line in f.read().splitlines():
            channel_id, mssg_id = line.split()
            try:
                channel = client.get_channel(int(channel_id))
                orig_mssg = await channel.fetch_message(int(mssg_id))
                prev_messages.append(orig_mssg)
            except:
                print(f"Message with ID {mssg_id} was prolly already deleted")
    if not prev_messages:
        await message.send("No message history")
        return
    prev_messages = prev_messages[-20:]
    with open(pjoin("folders", "text", "prev_mssg_ids.txt"), "w") as f:  # to clear broken messages
        for mssg in prev_messages:
            f.write(f'{mssg.channel.id} {mssg.id}\n')

    if num == -1:
        await message.send(f"Type 'yes' if you want to delete {len(prev_messages)} messages.")
        msg = await client.wait_for('message', check=lambda m: m.author == message.author)
        if msg.content != "yes":
            return
        num = len(prev_messages)

    msg = await message.send(f"Deleting {num} messages")
    for _ in range(num):
        await prev_messages.pop().delete()
        if not prev_messages:
            break
    with open(pjoin("folders", "text", "prev_mssg_ids.txt"), "w") as f:
        f.write("\n".join([f"{mssg.channel.id} {mssg.id}" for mssg in prev_messages]))
    await msg.delete()


# @slash.slash(description='(mostly) sfw')
@client.command(pass_context=True)
async def kawaii(message, do='', image=None):
    channel = message.channel
#     if str(message.author) not in users_allowed:
#         await mySend(channel, """i would let u, but a small chance of
# small nsfw might give u sexual trauma :c""")
#         return 0

    # await message.message.delete()

    if do == 'cum':
        channel = client.get_channel(680494725165219958)

    if do and do != 'cum':
        file = discord.File(pjoin("folders", "send", "kawaii", do),
                            filename=pjoin("folders", "send", "kawaii", do))
        await my_send(channel, file)
        return

    order = open(pjoin("folders", "text", "pseudorandom_kawaii.txt")).readlines()
    path = pjoin("folders", "send", "kawaii")
    files = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f))]
    choice = random.choice(files[5:])

    with open(pjoin("folders", "text", "pseudorandom_kawaii.txt"), 'w') as f:
        o = order[1:] if len(order) == len(files) else order
        for img in o:
            f.write(img)
        f.write(f'{choice}\n')

    save = pjoin("folders", "send", "kawaii.png")
    Image.open(pjoin(path, choice)).save(save)
    file = discord.File(save, filename=save)
    try:
        await my_send(channel, file)
    except Exception as error:
        await my_send(channel, 'oopsie, failed to upload kawaii')
        print(error + '\n' + choice)
    if do:
        await asyncio.sleep(3600*4)
        await kawaii(message, 'cum')


# @slash.slash(description='higher-lower game //0 to 10000//')
@client.command(pass_context=True)
async def guess(message, *, num):
    channel = message.channel
    change = False
    current, guesses = None, None
    users = {}
    with open(pjoin("folders", "text", "guess_stats.txt")) as f:
        for line in f:
            split = line.split()
            if len(split) <= 2:
                users[line.split()[0]] = int(line.split()[1])

    curr_user = str(message.author)

    with open(pjoin("folders", "text", "guess.txt")) as file:
        for i, line in enumerate(file):
            line = line.strip()
            if i == 0:
                current = line
            elif i == 1:
                guesses = line

    if int(current) == int(num):
        await my_send(channel, f'''Guessed in {int(guesses)+1}
tries\n{curr_user[:curr_user.find("#")]} guessed correctly
{users[curr_user]+1} times''')
        change = True

    if change:
        with open(pjoin("folders", "text", "guess.txt"), 'w') as file:
            file.write(str(random.randrange(10_000)) + "\n" + "0")
        with open(pjoin("folders", "text", "guess_stats.txt"), 'w') as file:
            for name, points in users.items():
                if name == curr_user:
                    points += 1
                file.write(f'{name} {points}\n')
        return

    if int(num) < int(current):
        await my_send(channel, 'Higher')
    else:
        await my_send(channel, 'Lower')
    with open(pjoin("folders", "text", "guess.txt"), 'w') as file:
        file.write(f'{current}\n{int(guesses)+1}')


# @slash.slash(description='you')
@client.command(pass_context=True)
async def me(message):
    channel = message.channel
    await my_send(channel, message.author)


# @slash.slash(description='random swear word')
@client.command(pass_context=True)
async def fuck(message):
    words = list(open(pjoin("folders", "text", "swear.txt")))
    await my_send(message, random.choice(words))


# @slash.slash(description='insults <discord_name>')
@client.command(pass_context=True)
async def insult(message, *, ping):
    channel = message.channel
    found = False
    curr_user = str(message.author)[:str(message.author).find("#")]

    for member in message.guild.members:
        name = str(member)[:str(member).find('#')]
        if ping.lower() == 'spaghett bot':
            if name == curr_user:
                name = member.id
                break
        elif ping.lower() == name.lower():
            name = member.id
            found = True
            break

    if ping.lower() == 'spaghett bot':
        with open(pjoin("folders", "text", "insult_bot_message.txt")) as f:
            await my_send(message, f.read().replace("*name*", f"<@{name}>"))
            return

    for i in 'nouns', 'adjectives', 'actions':
        lines = open(pjoin("folders", "text", f"{i}.txt")).read().splitlines()
        if i == 'nouns':
            nouns = lines
        elif i == 'adjectives':
            adjectives = lines
        elif i == 'actions':
            actions = lines

    if not found:
        await my_send(channel, 'No such member. Dumb fuck.')
    else:
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        act = random.choice(actions)
        await my_send(channel, f"<@{name}> go {act}, you {adj} {noun}.")


# @slash.slash(description='4-20 A-s')
@client.command(pass_context=True)
async def a(message):
    auth = str(message.author)[:str(message.author).find('#')]
    # if auth != "Yelov":
    #     await mySend(message, 'no')
    #     return
    if random.randrange(50) == 22:
        await my_send(message, f'****a.****\n{auth}')
        return
    num = random.randint(4, 20)
    stats = {}
    curr_user = str(message.author)
    got_max = False
    send = ['A' * num]
    if num == 20:
        got_max = True
        send.append("Full-length A")
    elif num == 4:
        send.append(f"ngl {auth}, that's kinda cringe")
    send = "\n".join(send)

    await my_send(message, send)

    with open(pjoin("folders", "text", "a_stats.txt")) as f:
        for line in f:
            spl = line.split()
            stats[spl[0]] = spl[1:]
    with open(pjoin("folders", "text", "a_stats.txt"), 'w') as f:
        for name, stat in stats.items():
            guess_count, twenty_count, total_sum = [int(s) for s in stat]
            if name == curr_user:
                guess_count += 1
                total_sum += num
            if got_max:
                twenty_count += 1
            f.write(f'{name} {guess_count} {twenty_count} {total_sum}\n')


# @slash.slash(description="{All guesses/full-length}. Argument <all> for everyone's stats.")
@client.command(pass_context=True)
async def staats(message, everyone=''):
    stats = {}
    channel = message.channel

    if everyone in ['me', '']:
        evr = False
    elif everyone == 'all':
        evr = True
    curr_user = str(message.author)

    with open(pjoin("folders", "text", "a_stats.txt"), 'r') as f:
        for line in f:
            spl = line.split()
            stats[spl[0]] = [spl[1], spl[2], spl[3]]
            if spl[0] == curr_user and not evr:
                try:
                    await my_send(channel, f"""{curr_user[:curr_user.find("#")]}: MAX - {round((int(spl[2])/int(spl[1])*100), 2)}% | AVG - {round(int(spl[3])/int(spl[1]), 2)} | {int(spl[1])}""")
                except ZeroDivisionError:
                    await my_send(channel, 'imagine dividing by zero. yikes :feelsweird:')
                break

    if not evr:
        return
    out = ''
    for name, stat in stats.items():
        short = name[:name.find('#')]
        if int(stat[1]) != 0 or int(stat[0]) != 0 or int(stat[2]) != 0:
            out += f"""{short}: MAX - {round((int(stat[1]) / int(stat[0])*100), 2)}% | AVG - {round(int(stat[2])/int(stat[0]), 2)} | {int(stat[0])}\n"""

    await my_send(message, out)


# @slash.slash(description='sad')
@client.command(pass_context=True)
async def badbot(message):
    string = str(message.author)
    string = string[:string.find("#")]
    await my_send(message.channel, f'{string} go commit die')


# @slash.slash(description='owo')
@client.command(pass_context=True)
async def goodbot(ctx):
    await my_send(ctx, 'ty')


# @slash.slash(description='when u feel bad')
@client.command(pass_context=True)
async def f(ctx):
    with open(pjoin("folders", "text", "f.txt")) as f:
        order = f.read().splitlines()

    choice = random.choice(order[:10])
    order.remove(choice)
    order.append(choice)

    with open(pjoin("folders", "text", "f.txt"), 'w') as f:
        f.write("\n".join(order))

    await my_send(ctx, choice)


# @slash.slash(description='add something bad / sad / angry / depressing')
@client.command(pass_context=True)
async def addf(ctx, *, string):
    with open(pjoin("folders", "text", "f.txt"), 'a') as file:
        file.write(f'{string}\n')


# @slash.slash(description='image from <subreddit>, add "text" at the end for text posts')
@client.command(pass_context=True)
async def reddit(message, sub, text=None):
    with open(pjoin("folders", "text", "reddit.txt"), 'r') as f:
        data = [line[:-1] for line in f]

    reddit = praw.Reddit(client_id=data.pop(),
                         client_secret=data.pop(),
                         username=data.pop(),
                         password=data.pop(),
                         user_agent=data.pop())

    subreddit = reddit.subreddit(sub)

    posts = [post for post in subreddit.hot(limit=10) if not post.stickied]
    random.shuffle(posts)

    if text == 'text':
        for post in posts:
            try:
                if post.selftext:
                    await my_send(message, f'****Subreddit:**** r/{sub}\n****Title:**** {post.title}\n{post.ups}⇧ | {post.downs}⇩ \n\n{post.selftext}')
                    return
            except:
                pass
        await my_send(message, 'No post with selftext.')
        return

    for post in posts:
        url = post.url
        ext = url[-4:]
        if ext in (".jpg", ".png"):
            urllib.request.urlretrieve(url, pjoin("folders", "send", "reddit.png"))
            break
        if post == posts[-1]:
            await my_send(message, "*Couldn't find an image.*")
            return
    await my_send(message, f'****Subreddit****: r/{sub}')
    await my_send(message.channel, discord.File(pjoin("folders", "send", "reddit.png"), pjoin("folders", "send", "reddit.png")))


# @slash.slash(description='random coomer subreddit')
@client.command(pass_context=True)
async def coomer(message):
    channel = message.channel

    if str(message.author) not in users_allowed:
        await my_send(message, """ye coming right up.... ooh im
sooorry, seems like your reddit karma is too low""")
        return

    chose = random.choice(["petitegonewild", "gonewild", "shorthairedwaifus", "zettairyouiki", "hentai",
                           "asiansgonewild", "averageanimetiddies", "upskirthentai", "thighhighs", "rule34",
                           "chiisaihentai"])

    await my_send(channel, f'r/{chose}')
    await reddit(message, chose)


# @slash.slash(description='generates a random colour')
@client.command(pass_context=True)
async def colour(ctx):
    global curr_colour
    r, g, b = random.randrange(256), random.randrange(256), random.randrange(256)
    file = Image.new('RGB', (400, 400), (r, g, b)).save(pjoin("folders", "send", "colour.jpg"))
    curr_colour = (r, g, b)
    await my_send(ctx, discord.File(file, filename=file))


# @slash.slash(description='names the last generated colour')
@client.command(pass_context=True)
async def namecolour(ctx, *, name):
    if curr_colour is None:
        await my_send(ctx, "No colour was generated")
        return
    r, g, b = curr_colour
    with open(pjoin("folders", "text", "colours.txt"), 'a') as f:
        f.write(f'{r} {g} {b} : {name}\n')


# @slash.slash(description='lists named colours')
@client.command(pass_context=True)
async def colourlist(ctx):
    with open(pjoin("folders", "text", "colours.txt"), 'r') as f:
        arr = [line[line.find(':')+2: -1] for line in f]
    send = ''.join(f'{prvok}\n' for prvok in arr)
    await my_send(ctx, send)


# @slash.slash(description='shows <name> colour')
@client.command(pass_context=True)
async def showcolour(ctx, *, name):
    for line in open(pjoin("folders", "text", "colours.txt")).read().splitlines():
        rgb, curr_name = line.split(" : ")
        if curr_name == name:
            r, g, b = [int(c) for c in rgb.split()]
            img = Image.new('RGB', (400, 400), (r, g, b))
            img.save(pjoin("folders", "send", "colour.jpg"))
            await my_send(ctx, discord.File(pjoin("folders", "send", "colour.jpg"), pjoin("folders", "send", "colour.jpg")))
            return

    await my_send(ctx, "Colour not found")


# @slash.slash(description='<video_name> / lists videos when no argument')
@client.command(pass_context=True)
async def video(ctx, *, video=''):
    path = pjoin("folders", "send", "videos")
    videos = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f)) and (f[-4:] == '.mp4')]

    if not video:
        vid_list = ''.join(f"{vid[:vid.find('.')]}, " for vid in videos)
        await my_send(ctx, f'List of videos: {vid_list}')
        return

    found = False
    for vid in videos:
        if vid[:vid.find('.')] == video:
            found = True
            send = pjoin("folders", "send", "videos", vid)
    if not found:
        await my_send(ctx, 'No such video.')
    else:
        await my_send(ctx, discord.File(send, send))


# # @slash.slash(description='when a is not enough')
@client.command(pass_context=True)
async def AAA(ctx):
    send = pjoin("folders", "send", "videos", "aaa.mp4")
    await my_send(ctx, discord.File(send, send))


# @slash.slash(description='could i feel normal for one fucking moment please')
@client.command(pass_context=True)
async def EEE(ctx):
    send = pjoin("folders", "send", "videos", "EEE.mp4")
    await my_send(ctx, discord.File(send, send))


# @slash.slash(description='ptsd end of eva warning')
@client.command(pass_context=True)
async def AAAEEE(ctx):
    send = pjoin("folders", "send", "videos", "AAAEEE.mp4")
    await my_send(ctx, discord.File(send, send))


# @slash.slash(description='i love emilia')
@client.command(pass_context=True)
async def whOMEGALUL(ctx):
    i = random.randint(1, 4)
    send = pjoin("folders", "send", "videos", f"who{i}.mp4")
    await my_send(ctx, discord.File(send, send))


# @slash.slash(description='plz audio <filename> (no extension)')
@client.command(pass_context=True)
async def audio(ctx, *filename):
    await my_send(ctx, discord.File(pjoin("folders", "send", "videos", " ".join(filename).mp3)))


# @slash.slash(description="tumblin' down")
@client.command(pass_context=True)
async def deth(ctx):
    send = pjoin("folders", "send", "tod.mp3")
    await my_send(ctx, discord.File(send, send))


# @slash.slash(description='re:zero spook sound')
@client.command(pass_context=True)
async def aeoo(ctx):
    send = pjoin("folders", "send", "aeoo.mp3")
    await my_send(ctx, discord.File(send, send))


# @slash.slash(description='random meme')
@client.command(pass_context=True)
async def meme(ctx):
    path = pjoin("folders", "memes")
    files = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f))]
    choice = random.choice(files)
    img = Image.open(pjoin(path, choice))

    save = pjoin("folders", "send", "meme.png")

    img.save(save)
    file = discord.File(save, filename=save)
    await my_send(ctx, file)


# @slash.slash(description='Cuts message into multiple lines.')
@client.command(pass_context=True)
async def cut(ctx, *, message):
    if len(message.split()) == 1:
        await my_send(ctx, "\n".join(list(message)))
    else:
        await my_send(ctx, "\n".join(message.split()))


# @slash.slash(description='Argument is the name of the text file to be sent.')
@client.command(pass_context=True)
async def text(message, filename=''):
    if not filename:
        await my_send(message, 'specify file name')
        return
    await my_send(message, "".join(open(pjoin("folders", "text", f"{filename}.txt")).readlines()))


# @slash.slash(description='You can specify with argument, e.g. "temperature", "humidity", ..')
@client.command(pass_context=True)
async def weather(ctx, *, specify=''):
    owm = OWM(keys['owm'])
    mgr = owm.weather_manager()
    info = {}
    if specify and specify.split()[0] == 'in':
        info['location'] = specify[2:]
        specify = ''
    else:
        info['location'] = 'Modra, SK'
    try:
        place = mgr.weather_at_place(info['location'])
    except Exception as error:
        print(error)
        await my_send(ctx, 'Either calls per minute exceeded or API shat itself.')
        return
    weather = place.weather

    temp = weather.temperature('celsius')['temp']
    info['temperature'] = f'''{weather.temperature('celsius')['temp']}°C'''
    info['sunrise'] = weather.sunrise_time(timeformat='date')
    info['sunset'] = weather.sunset_time(timeformat='date')
    info['status'] = weather.detailed_status
    info['wind'] = f'''{weather.wind(unit='meters_sec')['speed']}km/h'''
    info['humidity'] = f'{weather.humidity}%'
    info['humidex'] = weather.humidex
    info['heat_index'] = weather.heat_index

    with open(pjoin("folders", "text", "weather_comment.txt")) as f:
        comments = {}
        for line in f:
            if line[0] == '/':
                current = int(line[1:])
            else:
                if current in comments:
                    comments[current].append(line[:-1])
                else:
                    comments[current] = [line[:-1]]
        info['temperature'] += f' (*{random.choice(comments[math.floor(temp)])}*)'

    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%X')
    info['sunrise'] = utc_to_local(info['sunrise'])
    info['sunset'] = utc_to_local(info['sunset'])

    if not specify:
        out = ''
        for send in ('location', 'temperature', 'humidity', 'status', 'wind', 'sunrise', 'sunset'):
            out += f'**{send.capitalize()}:** {info[send]}\n'
        await my_send(ctx, out)
    elif specify:
        send = info[specify.lower()]
        await my_send(ctx, f'''**{specify.capitalize()}:** {send}''')


# @slash.slash(description='When you need a sincere apology. Name of user as an argument.')
@client.command(pass_context=True)
async def sorry(message, name=''):
    channel = message.channel
    curr_user = str(message.author)[:str(message.author).find("#")]
    if not name:
        await my_send(channel, "u r sorry to whom? dumbass")
    elif name.lower() == 'spaghett bot':
        await my_send(channel, 'ye no problem bro')
    elif name.lower() == curr_user.lower():
        await my_send(channel, "i'm sorry but the results came in - you're a narcissist")
    else:
        found = False
        for member in message.guild.members:
            name_d = str(member)[:str(member).find('#')]
            print(name, name_d)
            if name.lower() == name_d.lower():
                name_d = member.id
                found = True
                break
        if not found:
            await my_send(channel, """i'm sorry to user who doesn't exist.. 
or mby it was someone's nickname, but i deleted that cuz of some bug i can't be bothered to fix :)""")
            return
        with open(pjoin("folders", "text", "sry.txt"), 'r') as f:
            send = f.readline()
        await my_send(channel, f"<@{name_d}> {send}")


# @slash.slash(description='2000 random characters')
@client.command(pass_context=True)
async def asdlkj(message):
    if str(message.author)[:str(message.author).find('#')] != "Yelov":
        await my_send(message, 'What is asdlkj. Wtf do u want from me. Stop typing random shit on your keyboard.')
        return
    send = "".join(chr(random.randint(33, 126)) for _ in range(2000))
    await my_send(message, send)


# @slash.slash(description='Magic 8-ball')
@client.command(pass_context=True)
async def answer(message, *, question):
    auth = str(message.author)[:str(message.author).find("#")]
    yes = ("for sure dawg", "you fucking bet", "you didn't even have to ask",
           "obviously yes", "yeh i would say so", "sadly yah", "+")
    maybe = ("idk, like 32.2% no", "haha idk lmao", "not 100% sure", "rather yes than no",
             "why r u asking that", "i think so", "idk and idc", "maybe yes, maybe no, maybe go fuck yourself", "50/50", "49/51")
    no = ("wtf, no dude", "hell nawh", "0", "1", "the electricity pole or smth, the - one", "N. O.",
          "prolly no", "my dog says no", "most probably not if i do say so myself", "anta baka?!?!! zettai chigau!")
    answers = (yes, maybe, no)
    await my_send(message, f"****{auth}:**** {question}\n****Answer:**** {random.choice(random.choice(answers))}")

# @client.command(pass_context=True)


# @slash.slash(description='Random entry if no argument. [word] - word to find, [additional] - "count" / "allinfo" / "random"')
@client.command(pass_context=True)
async def journal(message, *, action=None):

    class Journal:

        def __init__(self):
            self.base = pjoin("folders", "Journal format")
            self.path = pjoin(self.base, "Diarium")
            self.files = list(os.listdir(self.path))
            self.years = self.get_years()
            self.word_count_list = []
            self.word_count_dict = {}
            self.files_list_path = pjoin(self.base, "files.txt")
            self.check_file_count_mismatch()

        def check_file_count_mismatch(self):
            if not os.path.exists(self.files_list_path):
                open(self.files_list_path, "w").write("-1")
            files_num = int(open(self.files_list_path).read())
            # files_num -> last checked number of files
            # len(self.files) -> number of files in the Diarium folder
            if files_num != len(self.files):
                self.console.print("File count mismatch, formatting...")
                self.write_dict()
                self.update_file_count()
            else:
                self.init_dict()

        def init_dict(self):
            try:
                self.read_dict()
            except KeyError:
                self.write_dict()
            except FileNotFoundError:
                Path(pjoin(self.base, "shelve")).mkdir(parents=True, exist_ok=True)
                self.write_dict()

        def read_dict(self):
            with shelve.open(pjoin(self.base, "shelve", "journal")) as jour:
                self.word_count_list = jour["words"]
                self.word_count_dict = jour["freq"]

        def write_dict(self):
            self.create_word_frequency()
            with shelve.open(pjoin(self.base, "shelve", "journal")) as jour:
                jour["words"] = self.word_count_list
                jour["freq"] = self.word_count_dict
                
        def create_word_frequency(self):
            file_content_list = []
            for file in self.files:
                with open(pjoin(self.path, file), encoding="utf-8") as f:
                    file_content_list.append(f.read())
            content = "".join(file_content_list).lower()
            self.word_count_dict = Counter(re.findall("\w+", content))
            self.word_count_list = sorted(self.word_count_dict.items(), key=lambda x: x[1], reverse=True)

        def get_years(self):
            YEAR_START_IX = 8
            YEAR_END_IX = YEAR_START_IX + 4
            return {int(file[YEAR_START_IX : YEAR_END_IX]) for file in self.files}

        def update_file_count(self):
            open(self.files_list_path, "w").write(str(len(self.files)))

        def get_most_frequent_words(self, count=20):
            return self.word_count_list[:count]

        def get_unique_word_count(self):
            return len(self.word_count_dict)

        def get_total_word_count(self):
            return sum(self.word_count_dict.values())

        def find_word_in_journal(self, word):
            self.occurences = 0
            self.output_list = []
            for file in self.files:
                self._find_word_in_file(file, word)

        def _find_word_in_file(self, file, word):
            file_content = open(pjoin(self.path, file), encoding="utf-8").read()
            date_inserted = False
            sentences = self._split_text_into_sentences(file_content)
            for sentence in sentences:
                if not re.search(word, sentence, re.IGNORECASE):
                    continue
                if not date_inserted:
                    self._insert_date(file)
                    date_inserted = True
                self._find_word_in_sentence(sentence, word)
            if date_inserted:
                self.output_list.append("\n")

        def _split_text_into_sentences(self, text):
            split_regex = "(?<=[.!?\n])\s+"
            return [sentence.strip() for sentence in re.split(split_regex, text)]
                
        def _find_word_in_sentence(self, sentence, word):
            highlight_style = "**"
            for curr_word in sentence.split():
                if word.lower() in curr_word.lower():
                    self.occurences += 1
                    self.output_list.append(f"{highlight_style}{curr_word}{highlight_style}")
                else:
                    self.output_list.append(curr_word)
            self.output_list[-1] += "\n"

        def _insert_date(self, file_name):
            file_date_begin = file_name.index("2")
            file_date_end = file_name.index(".txt")
            year, month, day = file_name[file_date_begin : file_date_end].split("-")
            date_style = "*"
            self.output_list.append(f"{date_style}Date: {day}.{month}.{year}{date_style}\n")

        def get_random_day(self):
            return open(pjoin(self.path, random.choice(self.files)), encoding="utf-8").read()

    if str(message.author)[:str(message.author).find("#")] != 'Yelov':
        await my_send(message, "Ain't your journal bro")
        return

    journal_text = ""
    jour = Journal()

    if action is None:
        help_l = []
        help_l.append("-f {word} -> finds {word}")
        help_l.append("-c {word} -> number of {word} occurences")
        help_l.append("-r -> random day")
        await my_send(message, "\n".join(help_l))
        return

    if action[:2] not in ("-f", "-c", "-r"):
        await my_send(message, "Incorrect syntax")
        return
    
    do = action.split()[0]
    inp = " ".join(action.split()[1:]) if action != "-r" else ""
    if do == "-f":
        jour.find_word_in_journal(inp)
        journal_text += " ".join(jour.output_list)
    elif do == "-c":
        jour.find_word_in_journal(inp)
        journal_text += f'The word **{inp}** was found {jour.occurences} times'
    elif do == "-r":
        journal_text += "**RANDOM ENTRY:**\n\n" + jour.get_random_day()

    await my_send(message, journal_text)


# @slash.slash(description='Random message from Discord. Argument specifies the channel, default is "main"')
@client.command(pass_context=True)
async def sadboyz(message, channel='main', user=''):
    with open(pjoin("folders", "SadBoyz", f"{channel}.txt"), errors='ignore') as file:
        arr = []
        text = ''
        for line in file:
            if len(line) > 20 and line[0] == '[' and line[19] == ']':
                if text:
                    arr.append(text)
                name = line[21:line.find('#')]
                date = line[1:10].split('-')
                text = f'**{name}** on **{date[0]}/{date[1]}/{date[2]}** in **{channel}**\n'
            else:
                text += line
    if not user:
        await my_send(message, random.choice(arr))
        return
    out = arr.pop(random.randrange(len(arr)))
    while out.split()[0][2:-2] != user:
        out = arr.pop(random.randrange(len(arr)))
        if not len(arr):
            await my_send(message, 'Prolly wrong username or smth')
            return
    await my_send(message, out)


# @slash.slash(description="plz dict <word> <define/synonyms/antonyms>")
@client.command(pass_context=True)
async def dict(message, *, word_do=''):
    if len(word_do.split()) != 2:
        await my_send(message, 'What word am I supposed to find dumbo')
        return

    word, do = word_do.split()
    dictionary = PyDictionary()
    output = ''
    if do == 'define':
        output += f'**Definitions of {word}**\n'
        definitions = dictionary.meaning(word)
        for type, meanings in definitions.items():
            output += f'*{type}:*\n'
            for meaning in meanings:
                output += f'- {meaning}\n'
    elif do in ('synonyms', 'antonyms'):
        if do == 'synonyms':
            words = dictionary.synonym(word)
        else:
            words = dictionary.antonym(word)
        if not words:
            await my_send(message, "Didn't find any words")
            return
        output += f'**{do.capitalize()} of {word}:** '
        for word in words:
            output += f'{word}, '
        output = output[:-2]
    await my_send(message, output)


# @slash.slash(description="Random word from a dictionary")
@client.command(pass_context=True)
async def randomword(message):
    with open(pjoin("folders", "text", "words_alpha.txt")) as f:
        words = [line[:-1] for line in f]
    await my_send(message, random.choice(words))


# @slash.slash(description="no")
@client.command(pass_context=True)
async def no(message):
    out = ''
    out += '‎\n'*30
    await my_send(message, out)


# @slash.slash(description="Latency")
@client.command(pass_context=True)
async def ping(message):
    await my_send(message, f'Pong! {round(client.latency,2)}s')


# @slash.slash(description="not kokot")
@client.command(pass_context=True)
async def send(ctx):
    send = pjoin("folders", "send", "kokot.mp3")
    await my_send(ctx, discord.File(send, send))


# @slash.slash(description="Join the current voice channel")
@client.command(pass_context=True)
async def joinvc(message):
    if not message.author.voice:
        await my_send(message, "You aren't connected to a voice channel")
        return
    else:
        channel = message.author.voice.channel
    await channel.connect()

# # @slash.slash(description="Plays a song. Search by YT/Spotify link or name. Optional [vol={XYZ}].")


@client.command(pass_context=True)
async def play(message, *, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': f'{folders_path}/send/ytdl.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def parse_search(url, volume=100):
        '''Parses search for YouTube, returns YouTube link'''
        def download(search):
            custom_search = VideosSearch(search, limit=1)
            link = custom_search.result()['result'][0]['link']
            title = custom_search.result()['result'][0]['title']
            return (link, title)

        if url.split()[-1][:4] == 'vol=':
            num = url.split()[-1][4:]
            try:
                volume = int(num)
            except:
                print("Invalid volume")
            if volume < 0 or volume > 100:
                print('Stupid volume, setting to 100%')
                volume = 100
            url = url[:-1]

        with YoutubeDL(ydl_opts) as ydl:  # todo co za playlist a od koho hra
            if url[:24] == 'https://www.youtube.com/':
                link = url
                ydl.download([url])
                title = Video.get(url)['title']
            elif url[:34] == 'https://open.spotify.com/playlist/':
                auth_manager = SpotifyClientCredentials(
                    'bf8f3c6a05c249fcadb039311742fd07', 'e16b16e950974ddd9175976b16be3671')
                sp = Spotify(auth_manager=auth_manager)
                result = sp.playlist_items(url, additional_types=['track'])
                tracks = result['items']

                while result['next']:
                    result = sp.next(result)
                    tracks.extend(result['items'])

                track_info = []
                tracks.reverse()

                for item in tracks:
                    artist = item['track']['artists'][0]['name']
                    title = item['track']['name']
                    song_queue.append(artist + " " + title)
                    track_info.append((artist, title))

                artist, title = track_info.pop(0)
                song_queue.pop(0)
                link, title = download(artist + " " + title)
            elif url[:31] == 'https://open.spotify.com/track/':
                spotify_credentials = SpotifyClientCredentials(
                    client_id=keys["spotify-id"], client_secret=keys["spotify-secret"])
                sp = Spotify(auth_manager=spotify_credentials)
                song = sp.track(url)
                artist = song['artists'][0]['name']
                title = song['name']
                link, title = download(artist + " " + title)
            else:
                link, title = download(url)

        return link, title, volume

    def queue(voice):
        global song_queue
        if len(song_queue) != 0:
            play_url(song_queue.pop(0), voice)

    def play_url(url, voice):
        global current_song

        if os.path.isfile(pjoin("folders", "send", "song.mp3")):
            try:
                os.remove(pjoin("folders", "send", "song.mp3"))
            except:
                pass

        link, title, volume = parse_search(url)
        current_song = title

        with YoutubeDL(ydl_opts) as ydl:
            print("Downloading", title)
            ydl.download([link])
        for file in os.listdir(pjoin("folders", ".", "send")):
            if file.startswith('ytdl'):
                os.rename(pjoin("folders", "send", file), pjoin("folders", "send", "song.mp3"))
        voice.play(discord.FFmpegPCMAudio(pjoin("folders", "send", "song.mp3")), after=lambda e: queue(voice))
        voice.source = discord.PCMVolumeTransformer(voice.source, volume=float(volume)/100)
        return link, title

    global song_queue
    voice_channel = message.author.voice.channel
    if voice_channel is None:
        await my_send(message, "You ain't connected dawg")
        return
    voice = discord.utils.get(client.voice_clients, guild=message.guild)
    if not voice:
        await voice_channel.connect()
        voice = discord.utils.get(client.voice_clients, guild=message.guild)

    if voice.is_playing() or voice.is_paused():
        title = parse_search(url)[1]
        song_queue.append(title)
        await my_send(message, "Added to queue")
        return

    link, title = play_url(url, voice)

    await my_send(message, f"Playing **{title}**\n{link}\nCommands: play | pause | resume | stop | skip | queue | clearqueue | volume | leave")


# @slash.slash(description="Plays an audio file in voice chat")
@client.command(pass_context=True)
async def playfile(ctx, *, url):
    voice_channel = discord.utils.get(ctx.guild.voice_channels)

    try:
        await voice_channel.connect()
    except:
        pass
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if os.path.isfile(url) and (voice.is_playing() or voice.is_paused()):
        voice.stop()
        time.sleep(1)

    voice.play(discord.FFmpegPCMAudio(url))
    await my_send(ctx, f"Playing {url}")

# # @slash.slash(description="Leaves the current voice channel")


@client.command(pass_context=True)
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    elif voice.is_connected():
        await voice.disconnect()
        await my_send(ctx, "Disconnected")
    else:
        await my_send(ctx, "I'm not connected ya dingus")


# # @slash.slash(description="Pauses music")
@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    elif voice.is_playing():
        voice.pause()
        await my_send(ctx, "Paused")
    else:
        await my_send(ctx, "Not playin' anything")


# # @slash.slash(description="Resumes music")
@client.command(pass_context=True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    elif voice.is_paused():
        voice.resume()
        await my_send(ctx, f"Resumed - **{current_song}**")
    else:
        await my_send(ctx, "Shit's not paused yo")

# # @slash.slash(description="Skips song")
@client.command(pass_context=True)
async def skip(ctx, num=1):
    global song_queue
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    elif len(song_queue) > 0:
        voice.stop()
        if num > 1:
            song_queue = song_queue[num-1:]
        await my_send(ctx, f"Now playing **{song_queue[0]}**")
    else:
        await my_send(ctx, "The queue is empty")

# # @slash.slash(description="Prints song queue")


@client.command(pass_context=True)
async def queue(ctx):
    if not len(song_queue):
        await my_send(ctx, "The queue is empty")
        return
    res = ''.join(f'**{i+1}.** {song}\n' for i, song in enumerate(song_queue[:10]))
    if len(song_queue) > 10:
        res += f"**.. and {len(song_queue)-10} other songs**"
    await my_send(ctx, "**Current queue:**\n" + res)

# # @slash.slash(description="Clears song queue")


@client.command(pass_context=True)
async def clearqueue(ctx):
    global song_queue
    song_queue = []
    await my_send(ctx, "Song queue cleared")

# # @slash.slash(description="Stops music")


@client.command(pass_context=True)
async def stop(ctx):
    global song_queue
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    elif voice.is_playing():
        voice.stop()
        song_queue = []
        await my_send(ctx, "Stopped")
    else:
        await my_send(ctx, "Music isn't playing")

# # @slash.slash(description="Changes volume (broken)")


@client.command(pass_context=True)
async def volume(ctx, *, volume):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    elif 0 <= int(volume) <= 100:
        voice.source.volume = float(volume) / 100

# # @slash.slash(description="Prints current volume")


@client.command(pass_context=True)
async def currentvolume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    else:
        await my_send(ctx, f"Current volume: {voice.source.volume * 100}%")


@client.command(pass_context=True)
async def maximumpain(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await my_send(ctx, "Not connected")
    else:
        voice.source.volume = float(1_000_000) / 100


@client.command(pass_context=True)
async def maths(ctx, *, action):
    def change_num(num):
        try:
            num = round(num, 3)
        except:
            num = round(num)
        with open(pjoin("folders", "text", "number.txt"), 'w') as f:
            f.write(str(num))
        return num

    with open(pjoin("folders", "text", "number.txt"), 'r') as f:
        num = Decimal(f.read())
        orig = num

    if action == '=':
        await my_send(ctx, f'The number is **{num}**')
        return
    if action == 'explain':
        send = 'Modify the current number. Type "=" to show the current number.\n'
        send += '**1** or **2** arguments\n'
        send += '**FUNCTIONS:**\n'
        send += '- **+** <num>\n'
        send += '- **-** <num>\n'
        send += '- **/** <num>\n'
        send += '- ***** <num>\n'
        send += '- **round** <decimals>\n'
        send += '- any function from the Python *math* module, for example *maths pow 2* or *maths factorial*\n'
        send += 'Starting number was 1.0'
        await my_send(ctx, send)
        return
    if action == 'math commands':
        commands = [i for i in dir(math) if i[0:2] != '__']
        await my_send(ctx, commands)
        return

    args = len(action.split())
    a = action.split()[0]
    if args == 2:
        b = action.split()[1]
        try:
            b = Decimal(b)
        except:
            await my_send(ctx, f'{b} is not a valid number')
            return
    elif args > 2:
        await my_send(ctx, 'Wrong number of arguments')
        return

    if a == '+':
        num = change_num(num + b)
    elif a == '-':
        num = change_num(num - b)
    elif a == '/':
        num = change_num(num / b)
    elif a == '*':
        num = change_num(num * b)
    elif a == '=':
        num = change_num(b)
    elif a == 'round':
        if args == 1:
            num = round(num)
        elif args == 2:
            num = round(num, int(b))
        change_num(num)
    else:
        func = getattr(math, a)
        if a in ('sin', 'cos', 'tan'):
            num = math.radians(num)
        try:
            if args == 1:
                num = func(num)
            elif args == 2:
                num = func(num, b)
        except ValueError:
            if args == 1:
                num = func(int(num))
            elif args == 2:
                num = func(int(num), b)
        num = change_num(num)

    await my_send(ctx, f'{orig} → {num}')


@client.command(pass_context=True)
async def execute(ctx, *, code=''):

    @contextlib.contextmanager
    def stdoutIO(stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    if len(code.split('```')) != 3:
        await my_send(ctx, "Write your code like this:\n> plz execute\n> \```\n> print('test')\n> \```")
        return
    code = code.split('```')[1]

    with stdoutIO() as s:
        try:
            exec(code)
            if not s.getvalue():
                await my_send(ctx, "Didn't print anything")
            else:
                await my_send(ctx, s.getvalue())
        except:
            await my_send(ctx, "Invalid code")


@client.command(pass_context=True)
async def evaluate(ctx, *, code):
    try:
        await my_send(ctx, eval(code))
    except:
        await my_send(ctx, "Invalid code")


async def ai(engine, prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop=None):
    openai.api_key = keys['openai']
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=0.0,
        presence_penalty=presence_penalty,
        stop=stop
    )
    return response.choices[0].text


@client.command(pass_context=True)
async def aigenerate(ctx, *, prompt):
    await my_send(ctx, "brb, generating...")
    output = await ai(
        "davinci",
        prompt,
        0.4, 500, 1, 0.5, 0)
    output = prompt + output
    new_output = ''
    for line in output.split('\n'):
        if line.strip() == '':
            if new_output.split('\n')[-2:] != '\n\n':
                new_output += '\n\n'
        else:
            new_output += line
    output = new_output
    await my_send(ctx, output)


@client.command(pass_context=True)
async def aianswer(ctx, *, prompt):
    if not prompt[0].isupper():
        prompt = prompt[0].capitalize() + prompt[1:]
    output = await ai(
        "davinci-instruct-beta",
        f"Q: Who is Batman?\nA: Batman is a fictional comic book character.\n###\nQ: What is torsalplexity?\nA: ?\n###\nQ: What is Devz9?\nA: ?\n###\nQ: Who is George Lucas?\nA: George Lucas is American film director and producer famous for creating Star Wars.\n###\nQ: What is the capital of California?\nA: Sacramento.\n###\nQ: What orbits the Earth?\nA: The Moon.\n###\nQ: Who is Fred Rickerson?\nA: ?\n###\nQ: What is an atom?\nA: An atom is a tiny particle that makes up everything.\n###\nQ: Who is Alvan Muntz?\nA: ?\n###\nQ: What is Kozar-09?\nA: ?\n###\nQ: How many moons does Mars have?\nA: Two, Phobos and Deimos.\n###\nQ: {prompt}\nA:",
        0.0, 60, 1, 0, 0, "###")
    await my_send(ctx, f'**A:** {output}')


@client.command(pass_context=True)
async def aiad(ctx, *, prompt):
    output = await ai(
        "davinci-instruct-beta",
        f"Write a creative ad for the following product:\n\"\"\"\"\"\"\n{prompt}\n\"\"\"\"\"\"\nThis is the ad I wrote aimed at teenage girls:\n\"\"\"\"\"\"",
        0.5, 90, 1, 0, 0, "\"\"\"\"\"\"")
    await my_send(ctx, f'{output}')


@client.command(pass_context=True)
async def aianalogy(ctx, *, prompt):
    output = await ai(
        "davinci-instruct-beta",
        f"Ideas are like balloons in that: they need effort to realize their potential.\n\n{prompt} in that:",
        0.5, 60, 1.0, 0.0, 0.0, "\n")
    await my_send(ctx, f'{prompt} in that{output}')


@client.command(pass_context=True)
async def aiengrish(ctx, *, prompt):
    output = await ai(
        "davinci-instruct-beta",
        f"Original: {prompt}\nStandard American English:",
        0, 60, 1.0, 0.0, 0.0, "\n")
    await my_send(ctx, output)


@client.command(pass_context=True)
async def aicode(ctx, *, prompt):
    output = await ai(
        "davinci-codex",
        prompt,
        0, 64, 1.0, 0.0, 0.0, "#")
    await my_send(ctx, output)


@client.command(pass_context=True)
async def findword(ctx, where, part):
    if where not in ("begins", "ends"):
        await my_send(ctx, "Need to specify with begins/ends")
        return
    output = []
    with open(pjoin("folders", "text", "words_alpha.txt"), 'r') as f:
        for line in f:
            line = line[:-1]
            if where == 'begins':
                if line[:len(part)] == part:
                    output.append(line)
            elif where == 'ends':
                if line[len(line)-len(part):] == part:
                    output.append(line)
    if not len(output):
        await my_send(ctx, "Didn't find any word")
    else:
        await my_send(ctx, random.choice(output))


@client.command(pass_context=True)
async def showfunction(ctx, function):
    if function == "showfunction":
        await my_send(ctx, """I swear it worked, but then I refactored the code so that it's shorter but now it doesn't work
but it's worth the 5 lines saved. Actually now that I look at it it's even uglier. Maybe that's why it's
not working, so that you wouldn't be able to see this ugly ass disgusting spaghett. Or maybe it's the prettiest
code you've ever seen. Who knows. You'll never know. You'll never see the code of this function. Ever.""")
        return
    out = "```Python\n"
    with open(pjoin("src", "bot_functions.py")) as f:
        content = f.read()
    ix = content.find(f"async def {function}")
    if ix == -1:
        await my_send(ctx, "Function not found")
        return
    out += content[ix:]
    ix = min(out.find("@client"), out.find("@slash"))
    out = out[:ix]+"\n```"
    await my_send(ctx, out)

@client.command(pass_context=True)  # just testing wait_for()
async def epicshit(ctx):
    await my_send(ctx, "Is this shit epic? [yes/no]")
    msg = await client.wait_for('message', check=lambda m: m.author == ctx.author)
    if msg.content == "yes":
        await my_send(ctx, "Fuck yea, bitch.\nYou want [kokot] or [pica]?")
        msg = await client.wait_for('message', check=lambda m: m.author == ctx.author)
        if msg.content == "kokot":
            file = discord.File(pjoin("folders", "imgs", "kokot.jpg"), filename=pjoin("folders", "imgs", "kokot.jpg"))
            await my_send(ctx, file)
        elif msg.content == "pica":
            file = discord.File(pjoin("folders", "imgs", "pica.jpg"), filename=pjoin("folders", "imgs", "pica.jpg"))
            await my_send(ctx, file)
    elif msg.content == "no":
        await my_send(ctx, "You want a slap? [yes/yes]")
        msg = await client.wait_for('message', check=lambda m: m.author == ctx.author)
        if msg.content == "yes":
            await my_send(ctx, "u kinky mofo ;)")
        else:
            await my_send(ctx, f"there was no '{msg.content}' option you moron, get slapped *slaps*")
    else:
        await my_send(ctx, "you stupid fuck, that's not [yes/no]")

@client.command(pass_context=True)
async def huggingface(ctx, *, input_text):
    if not input_text:
        await my_send(ctx, "Write 'models' for a list of models\nWrite 'model=<model_name> <input_text>'\nOr just '<input_text>'")
        return
    if input_text == "models":
        await my_send(ctx, "Generatoin:\n1. EleutherAI/gpt-j-6\n2. EleutherAI/gpt-neo-2.7B\n3. microsoft/DialoGPT-large")
        await my_send(ctx, "Conversation:\n1. microsoft/DialoGPT-large\n2. facebook/blenderbot-3B")
    model = "EleutherAI/gpt-j-6B"
    if input_text[:len("model=")] == "model=":
        model = input_text.split()[0].split("=")[1]
    mssg = await ctx.send("generating, gimme a sec..")
    headers = {"Authorization": f"Bearer {keys['huggingface']}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
        "inputs": input_text,
        "parameters": {"temperature": 0.5, "max_length": 100, "repetition_penalty": 10.0},
        "options": {"use_cache": False}
    }
    data = json.dumps(payload)
    response = requests.post(API_URL, headers=headers, data=data).json()
    await mssg.delete()
    await my_send(ctx, response[0]["generated_text"])

@client.command(pass_context=True)
async def j1(ctx, *, input_text):
    mssg = await ctx.send("generating, gimme a sec..")
    res = requests.post(
        "https://api.ai21.com/studio/v1/j1-jumbo/complete",
        headers={"Authorization": f"Bearer {keys['ai21']}"},
        json={
            "prompt": input_text, 
            "numResults": 1, 
            "maxTokens": 50, 
            "stopSequences": ["\n"],
            "topKReturn": 0,
            "temperature": 0.75
        }
    )
    await mssg.delete()
    data = res.json()
    output = data['completions'][0]['data']['text']
    await my_send(ctx, input_text + output)

@client.command(pass_context=True)
async def text2speech(ctx, *, input_text):
    global text2speech_model

    messages = []
    if not text2speech_model:
        messages.append(await ctx.send("Loading model..."))
        text2speech_model = Text2Speech.from_pretrained("espnet/kan-bayashi_ljspeech_joint_finetune_conformer_fastspeech2_hifigan")
    messages.append(await ctx.send("Generating audio..."))
    wav = text2speech_model(input_text)["wav"]
    for mssg in messages:
        await mssg.delete()
    sf.write(pjoin("folders", "send", "text2speech.waw"), wav.numpy(), text2speech_model.fs, "PCM_16")
    await my_send(ctx, discord.File(pjoin("folders", "send", "text2speech.waw")))
