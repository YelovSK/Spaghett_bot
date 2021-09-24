import discord, time, random, asyncio, praw, urllib.request, time, shelve, os, youtube_dl, spotipy, re, math, openai, sys, contextlib
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import *
from decimal import *
from os import listdir
from os.path import isfile, join, getsize
from PIL import Image, ImageFont, ImageDraw
from pyowm.owm import OWM
from datetime import timezone
from pathlib import Path
from PyDictionary import PyDictionary
from io import StringIO

from help import *


stop = False
remindrun = False
prev_messages = []
users_allowed = ("Yelov#5021", "Averso#5633", "jozko#1351", "AltheaZ0rg#8216")
song_queue = []
current_song = ''
keys = {}
with open("ClientKey.txt") as f:
    for line in f:
        line = line[:-1]
        key, val = line.split()
        keys[key] = val

def splitLong(text):
    mssgs = []
    for _ in range((len(text)//2000) + 1):
        mssgs.append(text[:2000])
        text = text[2000:]
    if text:
        mssgs.append(text)
    return mssgs

@slash.slash(description='example: 1 hour 5 minutes <message> /repeat/')
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
        await ctx.send(f'Reminding in {when} minutes')
        mul = 60
    else:
        if when % 1 == 0:
            await ctx.send(f'Reminding in {round(when)} hours')
        else:
            await ctx.send(f'Reminding in {round(when // 1)}h{round((when % 1) * 60)}m')
        mul = 3600
    remindrun = True
    if repeat:
        stop = False
        for _ in range(100):
            if stop:
                break
            await asyncio.sleep(round(when * mul))
            await ctx.send(send)
    else:
        await asyncio.sleep(round(when * mul))
        await ctx.send(send)
        remindrun = False

@slash.slash(description='is timer active?')
async def remind_active(ctx):
    global remindrun
    if remindrun:
        await ctx.send('Ye')
    else:
        await ctx.send('Nah')

@slash.slash(description='stops timer')
async def remind_stop(ctx):
    global stop
    print('Stopped reminder')
    stop = True

@slash.slash(description='guess number from 1 to 100')
async def number(ctx, *, num):
    good = ['Nice flex faggit',
            'Lucky fuck',
            'Boohoo do u want me to suck your dick?',
            'Grats, ur life is still shit',
            'That wont make ur parents be proud of you',
            'That number was so fucking predictable']
    bad = ['AHahha so bad',
           'Oh no, cant guess a simple number?',
           'Wrong choice, like every choice uve made in ur life',
           'Kid, how to say this. U bad.',
           'U wouldve gotten ur dick sucked if u got this number. Shame.',
           'CONGRATS! ur wrong',
           'R u pretending?',
           'Imagine choosing that number, yikes',
           'Ur garbage sperm won a lottery yet u cant guess 1 number out of 100',
           'Pathetic',
           '?? you might have a small case of serious brain damage']
    try:
        numint = int(num)
        cis = random.randint(1, 100)
        if numint == cis:
            await ctx.send(f'Guessed {num}\n{random.choice(good)}')
        else:
            await ctx.send(f'Guessed {num}\n{random.choice(bad)}')
            print(f'Guessed {num}, was {cis}')
    except:
        await ctx.send(f'Ah yes, {num} - the perfect "number". Moron.')

@slash.slash(description='"list" / "add "word" / "define" <word : definition>')
async def word(ctx, do='', *, word=''):
    dick = {}
    if len(word.split()) > 1:
        word, definition = word.split(':')
        word.strip()
        definition.strip()

    if not do:
        await ctx.send('"list" / "define <word>" / "add <word : definition>"')
        
    elif do in 'add':
        with open('text/dictionary.txt', 'r') as file:
            for line in file:
                index = line.find(':')
                dick[line[:index-1]] = line[index+2:]

        if word not in dick.keys():
            with open('text/dictionary.txt', 'a') as file:
                file.write(f'{word}:{definition}\n')
                print(f'Added {word}')
                
    elif do == 'define':
        with open('text/dictionary.txt', 'r') as file:
            for line in file:
                index = line.find(':')
                if line[:index-1] == word:
                    await ctx.send(f'Definition of {word} -> {line[index+2:]}')

    elif do == 'list':
        send = ''

        with open('text/dictionary.txt', 'r') as file:
            for line in file:
                index = line.find(':')
                send += f'{line[:index-1]}\n'
        await ctx.send(send)

@slash.slash(description='<image name> <text> / img list when no argument')
async def image(ctx, img_name='', *, text=''):
    if not img_name:
        await ctx.send(f'Send with <image_name> <text>')
        send, path = "", "imgs"
        files = [f[:-4] for f in listdir(path) if isfile(join(path, f))]

        for file in files:
            send += f'{file}\n'
        await ctx.send(f'Image list:\n{send}')
    else:
        basewidth = 1200
        split = [img_name, text]
        num = split[0]
        try:
            img = Image.open(f'imgs/{num}.png')
        except:
            img = Image.open(f'imgs/{num}.jpg')

        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        draw = ImageDraw.Draw(img)

        message = ''.join(f'{i} ' for i in split[1:])

        chars = len(message)
        font = ImageFont.truetype("font.ttf", int((basewidth+230)/((chars/2)+4)))
        fontsize = int((basewidth+230)/((chars/2)+3))
        w, h = draw.textsize(message, font=font)
        draw.text(((img.width-w)/2, img.height-(fontsize/1.2)-30), message, font=font, fill='black')
        font = ImageFont.truetype("font.ttf", int((basewidth+200)/((chars/2)+4)))
        fontsize = int((basewidth+200)/((chars/2)+3))
        w, h = draw.textsize(message, font=font)
        draw.text(((img.width-w)/2, img.height-(fontsize/1.2)-30), message, font=font, fill='white')
        img.save('send/meme.png')

        file = discord.File("send/meme.png", filename="send/meme.png")
        await ctx.send(file=file)

@slash.slash(description='random fap image, can be sent with <folder_name>')
async def fap(message, *, folder=''):
    if not folder:
        with open("text/fap.txt", 'r') as f:
            folders = [line[:-1] for line in f]
        folder = random.choice(folders)

    path = f"F:\Desktop start menu\homework\{folder}"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    choice = random.choice(files)
    final_path = f'{path}\{choice}'
    size = round(getsize(final_path) / 1048576, 2)
    while size > 8:
        size = round(getsize(final_path) / 1048576, 2)
        prev_messages.append(await message.send(f'{choice} is too large ({size} MB)'))
        choice = random.choice(files)
        final_path = f'{path}\{choice}'
    img = Image.open(final_path)

    save = 'send/homework.png'

    img.save(save)
    file = discord.File(save, filename=save)
    prev_messages.append(await message.channel.send(f'****Folder:**** {folder}'))
    try:
        prev_messages.append(await message.send(file=file))
    except Exception as error:
        await message.send('oopsie, failed to upload, error kodiQ: ' + str(error))
        prev_messages.append(await message.send(f'{choice} is (prolly?) too large ({size} MB)'))

@slash.slash(description='[plz delete <msg_num>] no argument deletes all messages')
async def delete(message, number=0):
    global prev_messages
    if not number:
        number = len(prev_messages)
    await message.send(f"Deleting {number} messages")
    for msg in prev_messages[-number:]:
        await msg.delete()
    prev_messages = prev_messages[:-number]

@slash.slash(description='(mostly) sfw')
async def kawaii(message, do='', image=None):
    channel = message.channel
#     if str(message.author) not in users_allowed:
#         await channel.send("""i would let u, but a small chance of
# small nsfw might give u sexual trauma :c""")
#         return 0

    # await message.message.delete()
    global prev_messages

    if do == 'cum':
        channel = client.get_channel(680494725165219958)

    path = "send/kawaii"
    if do and do != 'cum':
        file = discord.File(f'send/kawaii/{do}', filename=f'send/kawaii/{do}')
        prev_messages.append(await channel.send(file=file))
        return

    with open('text/pseudorandom_kawaii.txt', 'r') as f:
        order = []
        for line in f:
            if line.find('\n') == -1:
                order.append(line)
            else:
                order.append(line[:line.find('\n')])

    files = [f for f in listdir(path) if isfile(join(path, f))]
    choice = random.choice(files[5:])

    with open('text/pseudorandom_kawaii.txt', 'w') as f:
        o = order[1:] if len(order) == len(files) else order
        for img in o:
            f.write(f'{img}\n')
        f.write(f'{choice}\n')

    img = Image.open(f'{path}\{choice}')

    save = 'send/kawaii.png'

    img.save(save)
    file = discord.File(save, filename=save)
    try:
        prev_messages.append(await channel.send(file=file))
    except Exception as error:
        await channel.send('oopsie, failed to upload kawaii')
        print(error + '\n' + choice)
    if do:
        await asyncio.sleep(3600*4)
        await kawaii(message, 'cum')

@slash.slash(description='higher-lower game //0 to 10000//')
async def guess(message, *, num):
    channel = message.channel
    change = False
    current, guesses = None, None
    users = {}
    
    with open('text/guess_stats.txt') as f:
        for line in f:
            split = line.split()
            if len(split) <= 2:
                users[line.split()[0]] = int(line.split()[1])
        
    curr_user = str(message.author)

    with open('text/guess.txt') as file:
        for i, line in enumerate(file):
            if i == 0:
                current = line[:-1]
            elif i == 1:
                guesses = line[:-1]

    if int(current) == int(num):
        await channel.send(f'''Guessed in {int(guesses)+1}
tries\n{curr_user[:curr_user.find("#")]} guessed correctly
{users[curr_user]+1} times''')
        change = True

    if change:
        cis = random.randrange(10000)
        with open('text/guess.txt', 'w') as file:
            file.write(f'{cis}\n0\n')
        with open('text/guess_stats.txt', 'w') as file:
            for name, points in users.items():
                if name == curr_user:
                    file.write(f'{name} {points+1}\n')
                else:
                    file.write(f'{name} {points}\n')
    else:
        if int(num) < int(current):
            await channel.send('Higher')
        else:
            await channel.send('Lower')
        with open('text/guess.txt', 'w') as file:
            file.write(f'{current}\n{int(guesses)+1}\n')

@slash.slash(description='you')
async def me(message):
    channel = message.channel
    await channel.send(message.author)

@slash.slash(description='random swear word')
async def fuck(message):
    with open('text/swear.txt', 'r') as file:
        words = [line for line in file]

    await message.send(random.choice(words))

@slash.slash(description='insults <discord_name>')
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
        await channel.send(f"""<@{name}> I'm gonna fuck you up. I'm gonna
 hurt you real bad. I'm gonna find you, and it won't be nice for you.
 A few body parts might get accidentally sawed off. You might be awake for
 days in incredible pain. Don't worry, I'll keep you alive. Enjoy your day
 <@{name}> :)""")
    else:
        for i in 'nouns', 'adjectives', 'actions':
            with open(f'text/{i}.txt', 'r') as file:
                if i == 'nouns':
                    nouns = [line[:-1] for line in file]
                elif i == 'adjectives':
                    adjectives = [line[:-1] for line in file]
                elif i == 'actions':
                    actions = [line[:-1] for line in file]

        if not found:
            await channel.send('No such member. Dumb fuck.')
        else:
            adj = random.choice(adjectives)
            noun = random.choice(nouns)
            act = random.choice(actions)
            await channel.send(f"<@{name}> go {act}, you {adj} {noun}.")

@slash.slash(description='4-20 A-s')
async def a(message):
    channel = message.channel
    auth = str(message.author)[:str(message.author).find('#')]
    # if auth != "Yelov":
    #     await message.send('no')
    #     return
    if random.randrange(50) == 22:
        await message.send(f'****a.****\n{auth}')
        return
    num = random.randint(4, 20)
    stats = {}
    curr_user = str(message.author), False
    additional, send = '', ''

    if num == 20:
        curr_user = str(message.author), True
        additional = (f'\nFull-length A')

    elif num == 4:
        additional = (f"\nngl {auth}, that's kinda cringe")

    send += 'A' * num
    send += additional

    await message.send(send)

    with open('text/a_stats.txt', 'r') as f:
        for line in f:
            spl = line.split()
            stats[spl[0]] = [spl[1], spl[2], spl[3]]
    rnd = ('write random u fkin cat', 'something something random', 'go do rng', 'go post fucky wucky in rand..ucky')
    with open('text/a_stats.txt', 'w') as f:
        for name, stat in stats.items():
            if name == curr_user[0]:
                if name == "Averso#5633" and not int(stat[0]) % 10:
                    await channel.send(random.choice(rnd))
                if curr_user[1]:
                    f.write(f'{name} {int(stat[0])+1} {int(stat[1])+1} {int(stat[2])+num}\n')
                else:
                    f.write(f'{name} {int(stat[0])+1} {int(stat[1])} {int(stat[2])+num}\n')
            else:
                f.write(f'{name} {int(stat[0])} {int(stat[1])} {int(stat[2])}\n')

@slash.slash(description="{All guesses/full-length}. Argument <all> for everyone's stats.")
async def staats(message, everyone = ''):
    stats = {}
    channel = message.channel
    
    if everyone in ['me', '']:
        evr = False
    elif everyone == 'all':
        evr = True
    curr_user = str(message.author)
    
    with open('text/a_stats.txt', 'r') as f:
        for line in f:
            spl = line.split()
            stats[spl[0]] = [spl[1], spl[2], spl[3]]
            if spl[0] == curr_user and not evr:
                try:
                    await channel.send(f"""{curr_user[:curr_user.find("#")]}: MAX - {round((int(spl[2])/int(spl[1])*100), 2)}% | AVG - {round(int(spl[3])/int(spl[1]), 2)} | {int(spl[1])}""")
                except:
                    await channel.send('imagine dividing by zero. yikes :feelsweird:')
                break

    if evr:
        out = ''
        for name, stat in stats.items():
            short = name[:name.find('#')]
            if int(stat[1]) != 0 or int(stat[0]) != 0 or int(stat[2]) != 0:
                out += f"""{short}: MAX - {round((int(stat[1]) / int(stat[0])*100), 2)}% | AVG - {round(int(stat[2])/int(stat[0]), 2)} | {int(stat[0])}\n"""

        await message.send(out)

@slash.slash(description='sad')
async def badbot(message):
    channel = message.channel
    string = str(message.author)
    string = string[:string.find("#")]
    await channel.send(f'{string} go commit die')

@slash.slash(description='owo')
async def goodbot(ctx):
    await ctx.send('ty')

@slash.slash(description='when u feel bad')
async def f(ctx):
    with open('text/f.txt', 'r') as f:
        order = []
        for line in f:
            if line.find('\n') == -1:
                order.append(line)
            else:
                order.append(line[:line.find('\n')])
        
    choice = random.choice(order[:10])

    with open('text/f.txt', 'w') as f:
        for line in order:
            if line != choice:
                f.write(f'{line}\n')
        f.write(f'{choice}\n')

    await ctx.send(choice)

@slash.slash(description='add something bad / sad / angry / depressing')
async def addf(ctx, *, string):
    with open('text/f.txt', 'a') as file:
        file.write(f'{string}\n')

@slash.slash(description='image from <subreddit>, add "text" at the end for text posts')
async def reddit(message, sub, text=None):
    with open('text/reddit.txt', 'r') as f:
        data = [line[:-1] for line in f]

    reddit = praw.Reddit(client_id = data.pop(),
                     client_secret = data.pop(),
                     username = data.pop(),
                     password = data.pop(),
                     user_agent = data.pop())

    subreddit = reddit.subreddit(sub)
    
    posts = [post for post in subreddit.hot(limit=10) if not post.stickied]
    random.shuffle(posts)

    if text == 'text':
        for post in posts:
            try:
                if post.selftext:
                    await message.send(f'****Subreddit:**** r/{sub}\n****Title:**** {post.title}\n{post.ups}⇧ | {post.downs}⇩ \n\n{post.selftext}')
                    return
            except:
                pass
        await message.send('No post with selftext.')
    else:
        for post in posts:
            url = post.url
            ext = url[-4:]
            if ext in (".jpg", ".png"):
                urllib.request.urlretrieve(url, 'send/reddit.png')
                break
            if post == posts[-1]:
                await message.send("*Couldn't find an image.*")
                return
        await message.send(f'****Subreddit****: r/{sub}')
        await message.channel.send(file = discord.File("send/reddit.png", "send/reddit.png")) 

@slash.slash(description='random coomer subreddit')
async def coomer(message):
    channel = message.channel

    if str(message.author) not in users_allowed:
        await message.send("""ye coming right up.... ooh im
sooorry, seems like your reddit karma is too low""")
        return 0
    
    chose = random.choice(["petitegonewild", "gonewild", "shorthairedwaifus", "zettairyouiki", "hentai",
            "asiansgonewild", "averageanimetiddies", "upskirthentai", "thighhighs", "rule34",
            "chiisaihentai"])

    await channel.send(f'r/{chose}')
    await reddit(message, chose)

@slash.slash(description='generates a random colour')
async def colour(ctx):
    r, g, b = random.randrange(256), random.randrange(256), random.randrange(256)
    img = Image.new('RGB', (400, 400), (r, g, b))
    img.save('colour.jpg')
    with open('text/colours.txt', 'a') as f:
        f.write(f'{r} {g} {b} : ')
    await ctx.send(file = discord.File("colour.jpg", "colour.jpg"))

@slash.slash(description='names the last generated colour')
async def namecolour(ctx, *, name):
    with open('text/colours.txt', 'a') as f:
        f.write(f'{name}\n')

@slash.slash(description='lists named colours')
async def colourlist(ctx):
    with open('text/colours.txt', 'r') as f:
        arr = [line[line.find(':')+2 : -1] for line in f]
    send = ''.join(f'{prvok}\n' for prvok in arr)
    await ctx.send(send)

@slash.slash(description='shows <name> colour')
async def showcolour(ctx, *, name):
    with open('text/colours.txt', 'r') as f:
        for line in f:
            if line[line.find(':')+2 : -1] == name:
                r, g, b = line[:line.find(':')-1].split()
                img = Image.new('RGB', (400, 400), (int(r), int(g), int(b)))
                img.save('send/colour.jpg')
                await ctx.send(file = discord.File('send/colour.jpg', 'send/colour.jpg'))
                break

@slash.slash(description='<video_name> / lists videos when no argument')
async def video(ctx, *, video=''):
    path = 'D:\Desktop/Spaghett_bot/send/videos'
    videos = [f for f in listdir(path) if isfile(join(path, f)) and (f[-4:] == '.mp4')]

    if not video:
        vid_list = ''.join(f"{vid[:vid.find('.')]}, " for vid in videos)
        await ctx.send(f'List of videos: {vid_list}')
    else:
        found = False
        for vid in videos:
            if vid[:vid.find('.')] == video:
                found = True
                send = f'send/videos/{vid}'
        if not found:
            await ctx.send('No such video.')
        else:
            await ctx.send(file = discord.File(send, send))

@slash.slash(description='when a is not enough')
async def AAA(ctx):
    send = 'send/videos/AAA.mp4'
    await ctx.send(file = discord.File(send, send))

@slash.slash(description='could i feel normal for one fucking moment please')
async def EEE(ctx):
    send = 'send/videos/EEE.mp4'
    await ctx.send(file = discord.File(send, send))

@slash.slash(description='ptsd end of eva warning')
async def AAAEEE(ctx):
    send = 'send/videos/AAAEEE.mp4'
    await ctx.send(file = discord.File(send, send))

@slash.slash(description='i love emilia')
async def whOMEGALUL(ctx):
    i = random.randint(1, 4)
    send = f'send/videos/who{i}.mp4'
    await ctx.send(file = discord.File(send, send))

@slash.slash(description='plz audio <filename> (no extension)')
async def audio(ctx, *filename):
    await ctx.send(file = discord.File(f'send/{" ".join(filename)}.mp3'))

@slash.slash(description="tumblin' down")
async def deth(ctx):
    send = 'send/tod.mp3'
    await ctx.send(file = discord.File(send, send))

@slash.slash(description='re:zero spook sound')
async def aeoo(ctx):
    send = 'send/aeoo.mp3'
    await ctx.send(file = discord.File(send, send))

@slash.slash(description='random meme')
async def meme(ctx): 
    path = f"D:\Desktop\Spaghett_bot\memes"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    choice = random.choice(files)
    img = Image.open(f'{path}\{choice}')

    save = 'send/meme.png'

    img.save(save)
    file = discord.File(save, filename=save)
    await ctx.send(file=file)

@slash.slash(description='Cuts message into multiple lines.')
async def cut(ctx, *, message):
    send = ''
    if len(message.split()) == 1:
        for i in message:
            send += f'{i}\n'
    else:
        for i in message.split():
            send += f'{i}\n'
    await ctx.send(send)

@slash.slash(description='Argument is the name of the text file to be sent.')
async def text(message, filename=''):
    if not filename:
        await message.send('specify file name')
    else:
        out = ''
        with open(f'text/{filename}.txt', 'r') as f:
            for line in f:
                out += line
        await message.send(out)

@slash.slash(description='You can specify with argument, e.g. "temperature", "humidity", ..')
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
        await ctx.send('Either calls per minute exceeded or API shat itself.')
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

    with open('text/weather_comment.txt', 'r') as f:
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
        await ctx.send(out)
    elif specify:
        send = info[specify.lower()]
        await ctx.send (f'''**{specify.capitalize()}:** {send}''')

@slash.slash(description='When you need a sincere apology. Name of user as an argument.')
async def sorry(message, name=''):
    channel = message.channel
    curr_user = str(message.author)[:str(message.author).find("#")]
    if not name:
        await channel.send("u r sorry to whom? dumbass")
    elif name.lower() == 'spaghett bot':
        await channel.send('ye no problem bro')
    elif name.lower() == curr_user.lower():
        await channel.send("i'm sorry but the results came in - you're a narcissist")
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
            await channel.send("""i'm sorry to user who doesn't exist.. 
or mby it was someone's nickname, but i deleted that cuz of some bug i can't be bothered to fix :)""")
            return
        with open('text/sry.txt', 'r') as f:
            send = f.readline()
        await channel.send(f"<@{name_d}> {send}")
    
@slash.slash(description='2000 random characters')
async def asdlkj(message):
    if str(message.author)[:str(message.author).find('#')] != "Yelov":
        await message.send('What is asdlkj. Wtf do u want from me. Stop typing random shit on your keyboard.')
        return
    send = "".join(chr(random.randint(33, 126)) for _ in range(2000))
    await message.send(send)

@slash.slash(description='Magic 8-ball')
async def answer(message, *, question):
    auth = str(message.author)[:str(message.author).find("#")]
    yes = ("for sure dawg", "you fucking bet", "you didn't even have to ask", "obviously yes", "yeh i would say so", "sadly yah",
    "+")
    maybe = ("idk, like 32.2% no", "haha idk lmao", "not 100% sure", "rather yes than no",
    "why r u asking that", "i think so", "idk and idc", "maybe yes, maybe no, maybe go fuck yourself", "50/50",
    "49/51")
    no = ("wtf, no dude", "hell nawh", "0", "1", "the electricity pole or smth, the - one", "N. O.",
    "prolly no", "my dog says no", "most probably not if i do say so myself", "anta baka?!?!! zettai chigau!")
    answers = (yes, maybe, no)
    await message.send(f"****{auth}:**** {question}\n****Answer:**** {random.choice(random.choice(answers))}")

# @client.command(pass_context=True)
@slash.slash(description='Random entry if no argument. <word> - word to find, <additional> - "count" / "allinfo"')
async def journal(message, word='', additional=None):

    class Journal:

        def __init__(self):
            self.time = time.time()
            self.base = "D:\\Desktop\\Spaghett_bot\\Journal format"
            self.path = "D:\\Desktop\\Spaghett_bot\\Journal format\\Diarium"
            self.files = [f for f in listdir(self.path)]
            self.count_all = 0
            with open(self.base+'\\files.txt') as f:
                files_count = int(f.read())
                if files_count != len(self.files):
                    print('Formatting')
                    self.format()
                    self.words = {}
                    self.count = 0
                    self.freq_table = self.freq()
                    with shelve.open(self.base+'\\journal') as jour:
                        jour['count_all'] = self.count_all
                        jour['words'] = self.words
                        jour['count'] = self.count
                        jour['freq'] = self.freq_table
                else:
                    with shelve.open(self.base+'\\journal') as jour:
                        self.count_all = jour['count_all']
                        self.words = jour['words']
                        self.count = jour['count']
                        self.freq_table = jour['freq']
            self.time = time.time() - self.time

        def format(self):
            for j in '2017', '2018', '2019', '2020', '2021':
                for i in range(1, 13):
                    Path(f'{j}/{str(i)}').mkdir(parents=True, exist_ok=True)
            self.files = [f for f in listdir(self.path) if isfile(join(self.path, f))]
            for file in self.files:
                with open(f'{self.path}\\{file}', 'r', errors='ignore') as f:
                    content = f.read()
                    txt = file[8:].split('-')
                    txt[2] = txt[2][:txt[2].find('.')]
                    if txt[2][0] == '0':
                        txt[2] = txt[2][1:]
                    if txt[1][0] == '0':
                        txt[1] = txt[1][1:]
                    with open(f'{txt[0]}/{txt[1]}/{txt[2]}.txt', 'w') as new:
                        new.write(content)
            with open(self.base+'\\files.txt', 'w') as f:
                f.write(str(len(self.files)))

        def freq(self):
            for file in self.files:
                with open(f'{self.path}\\{file}', 'r', encoding='utf-8') as f:
                    txt = f.read()
                    for sentence in re.split('[.\n]+', txt):
                        for word in sentence.split():
                            self.count_all += 1
                            if word[-1] == ',': word = word[:-1]
                            word = word.lower()
                            self.words[word] = self.words.get(word, 0) + 1
            freq = sorted(self.words.items(), key=lambda x: x[1], reverse=True)
            return freq

        def frequency_table(self, count=20):
            return self.freq_table[:count]

        def total_word_count(self, unique=False):
            if unique:
                return len(self.freq_table)
            return self.count_all

        def find_word(self, word):
            start = time.time()
            out = ''
            for file in self.files:
                with open(f'{self.path}\\{file}', 'r', encoding='utf-8') as f:
                    txt = f.read()
                    putDate, foundWord = False, False
                    for sentence in re.split('[.\n]+', txt):
                        sentence = sentence.strip()
                        if re.search(word, sentence, re.IGNORECASE):
                            if not putDate:
                                y, d, m = file[8:-4].split('-')
                                out += f'**Date: {d}.{m}.{y}**\n'
                            putDate, foundWord = True, True
                            self.count += len(re.findall(word, sentence, re.IGNORECASE))
                            out += sentence + '.\n'
                if foundWord:
                    out += '\n'
            find_time = time.time() - start
            self.time += find_time
            out += f'🡒 **{word}** was found **{self.count} times**\n'
            out += f'**🡒 WORD FOUND IN:** {round(find_time, 2)}s\n🡒 **TOTAL TIME (incl. dictionary):** {round(self.time, 2)}s'
            return out

        def random_entry(self):
            files = [f for f in listdir(self.path) if isfile(join(self.path, f))]
            with open(self.path+"\\"+random.choice(files), 'r', encoding='utf-8') as f:
                return f.read()

    if str(message.author)[:str(message.author).find("#")] != 'Yelov':
        await message.send("Ain't your journal bro")
        return

    global prev_messages

    journal_text = ""

    jour = Journal()
    if additional == "count":
        jour.find_word(word)
        prev_messages.append(await message.send(f'{word} found {jour.count} times'))
        return
    if word:
        print("trying to find", word)
        journal_text += f'{jour.find_word(word)}'
    else:
        journal_text += jour.random_entry()
    if additional == "allinfo":
        journal_text += f'\nAll words count: {jour.total_word_count(False)}\n'
        journal_text += f'Unique words count: {jour.total_word_count(True)}\n'
        journal_text += f'{jour.frequency_table()}\n'

    if len(journal_text) > 2000:
        for msg in splitLong(journal_text):
            prev_messages.append(await message.send(msg))
    else:
        prev_messages.append(await message.send(journal_text))

    # await message.message.delete()

@slash.slash(description='Random message from Discord. Argument specifies the channel, default is "main"')
async def sadboyz(message, channel='main', user=''):
    with open(f'SadBoyz/{channel}.txt', 'r', errors='ignore') as file:
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
        await message.send(random.choice(arr))
    else:
        out = arr.pop(random.randrange(len(arr)))
        while out.split()[0][2:-2] != user:
            out = arr.pop(random.randrange(len(arr)))
            if not len(arr):
                await message.send('Prolly wrong username or smth')
                return
        await message.send(out)

@slash.slash(description="plz dict <word> <define/synonyms/antonyms>")
async def dict(message, *, word_do=''):
    if len(word_do.split()) != 2:
        await message.send('What word am I supposed to find dumbo')
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
        output += f'**{do.capitalize()} of {word}:** '
        for word in words:
            output += f'{word}, '
        output = output[:-2]
    await message.send(output)

@slash.slash(description="Random word from a dictionary")
async def randomword(message):
    with open('text/words_alpha.txt', 'r') as f:
        words = [line[:-1] for line in f]
    await message.send(random.choice(words))

@slash.slash(description="no")
async def no(message):
    out = ''
    out += '‎\n'*30
    while True:
        await message.send(out)
        time.sleep(4)

@slash.slash(description="Continues text with GPT2 AI generation")
async def gpt2(message, input=""):
    if (input != ""):
        await message.send("generating...")
    else:
        await message.send("no input")
        return

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    inputs = tokenizer.encode(input, return_tensors='pt')
    outputs = model.generate(inputs, max_length=len(input.split())+30, do_sample=True)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    await message.send(input + text)

@slash.slash(description="Latency")
async def ping(message):
    await message.send(f'Pong! {round(client.latency,2)}s')

@slash.slash(description="not kokot")
async def kokot(ctx):
    send = 'send/kokot.mp3'
    await ctx.send(file = discord.File(send, send))

@slash.slash(description="Join the current voice channel")
async def joinvc(message):
    if not message.author.voice:
        await message.send("You aren't connected to a voice channel")
        return
    else:
        channel = message.author.voice.channel
    await channel.connect()

# @slash.slash(description="Plays a song. Search by YT/Spotify link or name. Optional [vol={XYZ}].")
@client.command(pass_context=True)
async def play(message, *, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': 'send/ytdl.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def parse_search(url, volume=100):
        '''Parses search for YouTube, returns YouTube link'''
        def download(search):
            customSearch = CustomSearch(search, None, limit = 1)
            link = customSearch.result()['result'][0]['link']
            title = customSearch.result()['result'][0]['title']
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

        with youtube_dl.YoutubeDL(ydl_opts) as ydl: # todo co za playlist a od koho hra
            if url[:24] == 'https://www.youtube.com/':
                link = url
                ydl.download([url])
                title = Video.get(url)['title']
            elif url[:34] == 'https://open.spotify.com/playlist/':
                auth_manager = SpotifyClientCredentials('bf8f3c6a05c249fcadb039311742fd07', 'e16b16e950974ddd9175976b16be3671')
                sp = spotipy.Spotify(auth_manager=auth_manager)
                tracks = []
                result = sp.playlist_items(url, additional_types=['track'])
                tracks.extend(result['items'])

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
                auth_manager = SpotifyClientCredentials('bf8f3c6a05c249fcadb039311742fd07', 'e16b16e950974ddd9175976b16be3671')
                sp = spotipy.Spotify(auth_manager=auth_manager)
                song = sp.track('https://open.spotify.com/track/6E3TudlZucyt2fxE8Ljgw6?si=6b123dd669914e7f')
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
        
        if os.path.isfile("send/song.mp3"):
            try:
                os.remove("send/song.mp3")
            except:
                pass

        link, title, volume = parse_search(url)
        current_song = title

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        for file in os.listdir("./send"):
            if file.startswith('ytdl'):
                os.rename(f'send/{file}', "send/song.mp3")
        voice.play(discord.FFmpegPCMAudio("send/song.mp3"), after=lambda e: queue(voice))
        voice.source = discord.PCMVolumeTransformer(voice.source, volume=float(volume)/100)
        return link, title

    global song_queue
    voiceChannel = message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=message.guild)
    if not voice:
        await voiceChannel.connect()
        voice = discord.utils.get(client.voice_clients, guild=message.guild)



    if voice.is_playing() or voice.is_paused():
        title = parse_search(url)[1]
        song_queue.append(title)
        await message.send("Added to queue")
        return

    link, title = play_url(url, voice)

    await message.send(f"Playing **{title}**\n{link}\nCommands: play | pause | resume | stop | skip | queue | clearqueue | volume | leave")

@slash.slash(description="Plays an audio file in voice chat")
async def playfile(ctx, *, url):
    song_there = os.path.isfile(url)
    voiceChannel = discord.utils.get(ctx.guild.voice_channels)

    try:
        await voiceChannel.connect()
    except:
        pass
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if song_there and (voice.is_playing() or voice.is_paused()):
        voice.stop()
        time.sleep(1)

    voice.play(discord.FFmpegPCMAudio(url))
    await ctx.send(f"Playing {url}")

# @slash.slash(description="Leaves the current voice channel")
@client.command(pass_context=True)
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    elif voice.is_connected():
        await voice.disconnect()
        await ctx.send("Disconnected")
    else:
        await ctx.send("I'm not connected ya dingus")


# @slash.slash(description="Pauses music")
@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    elif voice.is_playing():
        voice.pause()
        await ctx.send("Paused")
    else:
        await ctx.send("Not playin' anything")


# @slash.slash(description="Resumes music")
@client.command(pass_context=True)
async def resume(ctx):
    global current_song
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    elif voice.is_paused():
        voice.resume()
        await ctx.send(f"Resumed - **{current_song}**")
    else:
        await ctx.send("Shit's not paused yo")

# @slash.slash(description="Skips song")
@client.command(pass_context=True)
async def skip(ctx, number=1):
    global song_queue
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    elif len(song_queue) > 0:
        voice.stop()
        if number > 1:
            song_queue = song_queue[number-1:]
        await ctx.send(f"Now playing **{song_queue[0]}**")
    else:
        await ctx.send("The queue is empty")

# @slash.slash(description="Prints song queue")
@client.command(pass_context=True)
async def queue(ctx):
    global song_queue
    if not len(song_queue):
        await ctx.send("The queue is empty")
        return
    res = ''.join(f'**{i+1}.** {song}\n' for i, song in enumerate(song_queue[:10]))
    if len(song_queue) > 10:
        res += f"**.. and {len(song_queue)-10} other songs**"
    await ctx.send("**Current queue:**\n" + res)

# @slash.slash(description="Clears song queue")
@client.command(pass_context=True)
async def clearqueue(ctx):
    global song_queue
    song_queue = []
    await ctx.send("Song queue cleared")

# @slash.slash(description="Stops music")
@client.command(pass_context=True)
async def stop(ctx):
    global song_queue
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    elif voice.is_playing():
        voice.stop()
        song_queue = []
        await ctx.send("Stopped")
    else:
        await ctx.send("Music isn't playing")

# @slash.slash(description="Changes volume (broken)")
@client.command(pass_context=True)
async def volume(ctx, *, volume):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    elif 0 <= int(volume) <= 100:
        voice.source.volume = float(volume) / 100

# @slash.slash(description="Prints current volume")
@client.command(pass_context=True)
async def currentvolume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    else:
        await ctx.send(f"Current volume: {voice.source.volume*100}%")

@client.command(pass_context=True)
async def maximumpain(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Not connected")
    else:
        voice.source.volume = float(1000000) / 100

@client.command(pass_context=True)
async def maths(ctx, *, action):
    def change_num(num):
        try:
            num = round(num, 3)
        except:
            num = round(num)
        with open('text/number.txt', 'w') as f:
            f.write(str(num))
        return num

    with open('text/number.txt', 'r') as f:
        num = Decimal(f.read())
        orig = num
    
    if action == '=':
        await ctx.send(f'The number is **{num}**')
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
        await ctx.send(send)
        return
    if action == 'math commands':
        commands = [i for i in dir(math) if i[0:2] != '__']
        await ctx.send(commands)
        return

    args = len(action.split())
    a = action.split()[0]
    if args == 2:
        b = action.split()[1]
        try:
            b = Decimal(b)
        except:
            await ctx.send(f'{b} is not a valid number')
            return
    elif args > 2:
        await ctx.send('Wrong number of arguments')
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
                num = func(num,b)
        except ValueError:
            if args == 1:
                num = func(int(num))
            elif args == 2:
                num = func(int(num),b)
        num = change_num(num)

    await ctx.send(f'{orig} → {num}')

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
        await ctx.send("Write your code like this:\n> plz execute\n> \```\n> print('test')\n> \```")
        return
    code = code.split('```')[1]

    with stdoutIO() as s:
        try:
            exec(code)
            if not s.getvalue():
                await ctx.send("Didn't print anything")
            else:
                await ctx.send(s.getvalue())
        except:
            await ctx.send("Invalid code")

@client.command(pass_context=True)
async def evaluate(ctx, *, code):
    try:
        await ctx.send(eval(code))
    except:
        await ctx.send("Invalid code")

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
    def splitLong(text):
        mssgs = []
        for _ in range((len(text)//2000) + 1):
            mssgs.append(text[:2000])
            text = text[2000:]
        if text:
            mssgs.append(text)
        return mssgs

    await ctx.send("brb, generating...")
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
    if len(output) > 2000:
        for msg in splitLong(output):
            await ctx.send(msg)
    else:
        await ctx.send(output)

@client.command(pass_context=True)
async def aianswer(ctx, *, prompt):
    if not prompt[0].isupper():
        prompt = prompt[0].capitalize() + prompt[1:]
    output = await ai(
        "davinci-instruct-beta",
        f"Q: Who is Batman?\nA: Batman is a fictional comic book character.\n###\nQ: What is torsalplexity?\nA: ?\n###\nQ: What is Devz9?\nA: ?\n###\nQ: Who is George Lucas?\nA: George Lucas is American film director and producer famous for creating Star Wars.\n###\nQ: What is the capital of California?\nA: Sacramento.\n###\nQ: What orbits the Earth?\nA: The Moon.\n###\nQ: Who is Fred Rickerson?\nA: ?\n###\nQ: What is an atom?\nA: An atom is a tiny particle that makes up everything.\n###\nQ: Who is Alvan Muntz?\nA: ?\n###\nQ: What is Kozar-09?\nA: ?\n###\nQ: How many moons does Mars have?\nA: Two, Phobos and Deimos.\n###\nQ: {prompt}\nA:",
        0.0, 60, 1, 0, 0, "###")
    await ctx.send(f'**A:** {output}')

@client.command(pass_context=True)
async def aiad(ctx, *, prompt):
    output = await ai(
        "davinci-instruct-beta",
        f"Write a creative ad for the following product:\n\"\"\"\"\"\"\n{prompt}\n\"\"\"\"\"\"\nThis is the ad I wrote aimed at teenage girls:\n\"\"\"\"\"\"",
        0.5, 90, 1, 0, 0, "\"\"\"\"\"\"")
    await ctx.send(f'{output}')

@client.command(pass_context=True)
async def aianalogy(ctx, *, prompt):
    output = await ai(
        "davinci-instruct-beta",
        f"Ideas are like balloons in that: they need effort to realize their potential.\n\n{prompt} in that:",
        0.5, 60, 1.0, 0.0, 0.0, "\n")
    await ctx.send(f'{prompt} in that{output}')

@client.command(pass_context=True)
async def aiengrish(ctx, *, prompt):
    output = await ai(
        "davinci-instruct-beta",
        f"Original: {prompt}\nStandard American English:",
        0, 60, 1.0, 0.0, 0.0, "\n")
    await ctx.send(output)

@client.command(pass_context=True)
async def aicode(ctx, *, prompt):
    output = await ai(
        "davinci-codex",
        prompt,
        0, 64, 1.0, 0.0, 0.0, "#")
    await ctx.send(output)

@client.command(pass_context=True)
async def findword(ctx, where, part):
    if where not in ("begins", "ends"):
        await ctx.send("Need to specify with begins/ends")
        return
    output = []
    with open("text/words_alpha.txt", 'r') as f:
        for line in f:
            line = line[:-1]
            if where == 'begins':
                if line[:len(part)] == part:
                    output.append(line)
            elif where == 'ends':
                if line[len(line)-len(part):] == part:
                    output.append(line)
    if not len(output):
        await ctx.send("Didn't find any word")
    else:
        await ctx.send(random.choice(output))

@client.command(pass_context=True)
async def showfunction(ctx, function):
    global prev_messages
    out = "```Python\n"
    started = False
    finding = f"async def {function}"
    with open("bot_functions.py", "r") as f:
        for line in f:
            if not started and line[:len(finding)] == finding:
                started = True
                out += line
            elif started:
                if line[0] ==  "@":
                    out += "\n```"
                    if len(out) > 2000:
                        for msg in splitLong(out):
                            prev_messages.append(await ctx.send(msg))
                    else:
                        prev_messages.append(await ctx.send(out))
                    return
                else:
                    out += line
    if out == "```Python\n":
        await ctx.send("Function not found")
    else:
        if len(out) > 2000:
            for msg in splitLong(out):
                prev_messages.append(await ctx.send(msg))
        else:
            prev_messages.append(await ctx.send(out))
