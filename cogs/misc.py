from io import StringIO
import disnake
import random
import math
import json
import sys
import contextlib

from datetime import timezone
from PyDictionary import PyDictionary
from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Bot
from disnake.ext.commands import Context
from os.path import join as pjoin
from pyowm.owm import OWM


with open("config.json") as file:
    config = json.load(file)

class Misc(commands.Cog):
    """idk, random stuff"""
    
    COG_EMOJI = "💡"

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def insult(self, ctx: Context, *, ping):
        """Randomly generated insult. Argument is username, not nick.

        Syntax: ```plz insult <username>```
        Example: ```plz insult yomama```
        """
        channel = ctx.channel
        found = False
        curr_user = str(ctx.author)[:str(ctx.author).find("#")]

        for member in ctx.guild.members:
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
                await bot_send(ctx, f.read().replace("*name*", f"<@{name}>"))
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
            await bot_send(channel, 'No such member. Dumb fuck.')
        else:
            adj = random.choice(adjectives)
            noun = random.choice(nouns)
            act = random.choice(actions)
            await bot_send(channel, f"<@{name}> go {act}, you {adj} {noun}.")

    @commands.command()
    async def fuck(self, ctx: Context):
        """Random swear word.

        Syntax:```plz fuck```
        """
        words = list(open(pjoin("folders", "text", "swear.txt")))
        await bot_send(ctx, random.choice(words))

    @commands.command()
    async def f(self, ctx: Context):
        """Random sad/angry message.

        Syntax: ```plz f```
        """
        with open(pjoin("folders", "text", "f.txt")) as f:
            order = f.read().splitlines()

        choice = random.choice(order[:10])
        order.remove(choice)
        order.append(choice)

        with open(pjoin("folders", "text", "f.txt"), 'w') as f:
            f.write("\n".join(order))

        await bot_send(ctx, choice)

    @commands.command()
    async def addf(self, ctx: Context, *, string):
        """Adds message to the f list (when using plz f).

        Syntax: ```plz addf <message>```
        Example: ```plz addf very many sad :cccc```
        """
        with open(pjoin("folders", "text", "f.txt"), 'a') as file:
            file.write(f'{string}\n')

    @commands.command()
    async def a(self, ctx: Context):
        """Prints 4-20 A-s. Keeps track of stats with plz staats.

        Syntax: ```plz a```
        """
        auth = str(ctx.author)[:str(ctx.author).find('#')]
        # if auth != "Yelov":
        #     await mySend(message, 'no')
        #     return
        if random.randrange(50) == 22:
            await bot_send(ctx, f'****a.****\n{auth}')
            return
        num = random.randint(4, 20)
        stats = {}
        curr_user = str(ctx.author)
        got_max = False
        send = ['A' * num]
        if num == 20:
            got_max = True
            send.append("Full-length A")
        elif num == 4:
            send.append(f"ngl {auth}, that's kinda cringe")
        send = "\n".join(send)

        await bot_send(ctx, send)

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
                
    @commands.command()
    async def staats(self, ctx: Context, everyone=''):
        """Stats for the plz a function. Percetange of full-length A-s. Argument ["all"] for everyone's stats.

        Syntax: ```plz staats ["all"]```
        Example: ```plz staats all```
        """
        stats = {}
        channel = ctx.channel

        if everyone in ['me', '']:
            evr = False
        elif everyone == 'all':
            evr = True
        curr_user = str(ctx.author)

        with open(pjoin("folders", "text", "a_stats.txt")) as f:
            for line in f:
                spl = line.split()
                stats[spl[0]] = [spl[1], spl[2], spl[3]]
                if spl[0] == curr_user and not evr:
                    try:
                        await bot_send(channel, f"""{curr_user[:curr_user.find("#")]}: MAX - {round((int(spl[2])/int(spl[1])*100), 2)}% | AVG - {round(int(spl[3])/int(spl[1]), 2)} | {int(spl[1])}""")
                    except ZeroDivisionError:
                        await bot_send(channel, 'imagine dividing by zero. yikes :feelsweird:')
                    break

        if not evr:
            return
        out = ''
        for name, stat in stats.items():
            short = name[:name.find('#')]
            if int(stat[1]) != 0 or int(stat[0]) != 0 or int(stat[2]) != 0:
                out += f"""{short}: MAX - {round((int(stat[1]) / int(stat[0])*100), 2)}% | AVG - {round(int(stat[2])/int(stat[0]), 2)} | {int(stat[0])}\n"""

        await bot_send(ctx, out)
                
    @commands.command()
    async def dict(self, ctx: Context, *, word_do=''):
        """Dictionary.

        Syntax: ```plz dict <word> ["synonyms" / "antonyms" / "define"]```
        Example: ```plz dict sadness antonyms```
        """
        if len(word_do.split()) != 2:
            await bot_send(ctx, 'What word am I supposed to find dumbo')
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
                await bot_send(ctx, "Didn't find any words")
                return
            output += f'**{do.capitalize()} of {word}:** '
            for word in words:
                output += f'{word}, '
            output = output[:-2]
        await bot_send(ctx, output)
        
    @commands.command()
    async def weather(self, ctx: Context, *, specify=''):
        """Shows weather info.

        Syntax: ```plz weather [info]```
        Example: ```plz weather temperature``` ```plz weather in Bratislava```
        """
        owm = OWM(config['owm'])
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
            await bot_send(ctx, 'Either calls per minute exceeded or API shat itself.')
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
            temp_rounded = math.floor(temp)
            if temp_rounded in comments:
                info['temperature'] += f' (*{random.choice(comments[temp_rounded])}*)'

        def utc_to_local(utc_dt):
            return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%X')
        info['sunrise'] = utc_to_local(info['sunrise'])
        info['sunset'] = utc_to_local(info['sunset'])

        if not specify:
            out = ''
            for send in ('location', 'temperature', 'humidity', 'status', 'wind', 'sunrise', 'sunset'):
                out += f'**{send.capitalize()}:** {info[send]}\n'
            await bot_send(ctx, out)
        elif specify:
            send = info[specify.lower()]
            await bot_send(ctx, f'''**{specify.capitalize()}:** {send}''')
            
    @commands.command()
    async def word(self, ctx: Context, do='', *, word=''):
        """Local dictionary.

        Syntax: ```plz word ["list" / "define" <word> / "add" <word> : <definition>]```
        Example: ```plz word define hentai``` ```plz add chinchin : cute stick```
        """
        dick = {}
        if len(word.split()) > 1:
            word, definition = word.split(':')
            word.strip()
            definition.strip()

        dictionary_path = pjoin("folders", "text", "dictionary.txt")
        if not do:
            await bot_send(ctx, '"list" / "define <word>" / "add <word : definition>"')
        elif do in 'add':
            with open(dictionary_path) as file:
                for line in file:
                    index = line.find(':')
                    dick[line[:index-1]] = line[index+2:]

            if word not in dick.keys():
                with open(dictionary_path, 'a') as file:
                    file.write(f'{word}:{definition}\n')
                    print(f'Added {word}')

        elif do == 'define':
            with open(dictionary_path) as file:
                for line in file:
                    index = line.find(':')
                    if line[:index-1] == word:
                        await bot_send(ctx, f'Definition of {word} -> {line[index+2:]}')

        elif do == 'list':
            send = ''
            with open(dictionary_path) as file:
                for line in file:
                    index = line.find(':')
                    send += f'{line[:index-1]}\n'
            await bot_send(ctx, send)

    @commands.command()
    async def findword(self, ctx: Context, where, part):
        """Finds a word that begins/ends with <word_part>

        Syntax: ```plz findword <"begins"/"ends"> <word_part>```
        Example: ```plz findword begins holocau```
        """
        if where not in ("begins", "ends"):
            await bot_send(ctx, "Need to specify with begins/ends")
            return
        output = []
        with open(pjoin("folders", "text", "words_alpha.txt")) as f:
            for line in f:
                line = line[:-1]
                if where == 'begins':
                    if line[:len(part)] == part:
                        output.append(line)
                elif where == 'ends':
                    if line[len(line)-len(part):] == part:
                        output.append(line)
        if not len(output):
            await bot_send(ctx, "Didn't find any word")
        else:
            await bot_send(ctx, random.choice(output))

    @commands.command()
    async def no(self, ctx: Context):
        """Sends 30 empty lines (for when you don't want to see something).

        Syntax: ```plz no```
        """
        out = "‎\n"*30
        await bot_send(ctx, out)
        
    @commands.command()
    async def asdlkj(self, ctx: Context):
        """Sends 2000 random characters.

        Syntax: ```plz asdlkj```
        """
        if str(ctx.author)[:str(ctx.author).find('#')] != "Yelov":
            await bot_send(ctx, 'What is asdlkj. Wtf do u want from me. Stop typing random shit on your keyboard.')
            return
        send = "".join(chr(random.randint(33, 126)) for _ in range(2000))
        await bot_send(ctx, send)
        
    @commands.command()
    async def answer(self, ctx: Context, *, question):
        """Magic 8-ball.

        Syntax: ```plz answer <question>```
        Example: ```plz answer is life worth living?```
        """
        auth = str(ctx.author)[:str(ctx.author).find("#")]
        yes = ("for sure dawg", "you fucking bet", "you didn't even have to ask",
            "obviously yes", "yeh i would say so", "sadly yah", "+")
        maybe = ("idk, like 32.2% no", "haha idk lmao", "not 100% sure", "rather yes than no",
                "why r u asking that", "i think so", "idk and idc", "maybe yes, maybe no, maybe go fuck yourself", "50/50", "49/51")
        no = ("wtf, no dude", "hell nawh", "0", "1", "the electricity pole or smth, the - one", "N. O.",
            "prolly no", "my dog says no", "most probably not if i do say so myself", "anta baka?!?!! zettai chigau!")
        answers = (yes, maybe, no)
        await bot_send(ctx, f"****{auth}:**** {question}\n****Answer:**** {random.choice(random.choice(answers))}")
        
    @commands.command()
    async def cut(self, ctx: Context, *, message):
        """Splits the mesage into multiple lines.

        Syntax: ```plz cut <text>```
        Example: ```plz cut good jokes mate real funny see you at FUCK YOUJ```
        """
        if len(message.split()) == 1:
            await bot_send(ctx, "\n".join(list(message)))
        else:
            await bot_send(ctx, "\n".join(message.split()))

    @commands.command()
    async def delete(self, ctx: Context, num=1):
        """Deletes the last [num] messages. Set [num] to '-1' to delete all messages.

        Syntax: ```plz delete [num]```
        Example: ```plz delete``` ```plz delete 5```
        """
        prev_messages = []
        with open(pjoin("folders", "text", "prev_mssg_ids.txt")) as f:
            for line in f.read().splitlines():
                channel_id, mssg_id = line.split()
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    orig_mssg = await channel.fetch_message(int(mssg_id))
                    prev_messages.append(orig_mssg)
                except:
                    print(f"Message with ID {mssg_id} was prolly already deleted")
        if not prev_messages:
            await ctx.send("No message history")
            return
        with open(pjoin("folders", "text", "prev_mssg_ids.txt"), "w") as f:  # to clear broken messages
            for mssg in prev_messages:
                f.write(f'{mssg.channel.id} {mssg.id}\n')

        if num == -1:
            await ctx.send(f"Type 'yes' if you want to delete {len(prev_messages)} messages.")
            msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            if msg.content != "yes":
                return
            num = len(prev_messages)

        msg = await ctx.send(f"Deleting {num} messages")
        for _ in range(num):
            await prev_messages.pop().delete()
            if not prev_messages:
                break
        with open(pjoin("folders", "text", "prev_mssg_ids.txt"), "w") as f:
            f.write("\n".join([f"{mssg.channel.id} {mssg.id}" for mssg in prev_messages]))
        await msg.delete()
        
    @commands.command()
    async def guess(self, ctx: Context, *, num):
        """Higher/lower guessing game. Generated number is from 0 to 10_000.

        Syntax: ```plz guess <num>```
        Example: ```plz guess 322```
        """
        channel = ctx.channel
        change = False
        current, guesses = None, None
        users = {}
        with open(pjoin("folders", "text", "guess_stats.txt")) as f:
            for line in f:
                split = line.split()
                if len(split) <= 2:
                    users[line.split()[0]] = int(line.split()[1])

        curr_user = str(ctx.author)

        with open(pjoin("folders", "text", "guess.txt")) as file:
            for i, line in enumerate(file):
                line = line.strip()
                if i == 0:
                    current = line
                elif i == 1:
                    guesses = line

        if int(current) == int(num):
            await bot_send(channel, f'''Guessed in {int(guesses)+1}
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
            await bot_send(channel, 'Higher')
        else:
            await bot_send(channel, 'Lower')
        with open(pjoin("folders", "text", "guess.txt"), 'w') as file:
            file.write(f'{current}\n{int(guesses)+1}')

    @commands.command()
    async def number(self, ctx: Context, *, num):
        """Guess a number from 1 to 100.

        Syntax: ```plz number <num>```
        Example: ```plz number 69```
        """
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
            await bot_send(ctx, f'Ah yes, {num} - the perfect "num". Moron.')
            return
        num_int = int(num)
        cis = random.randint(1, 100)
        ans = random.choice(good) if num_int == cis else random.choice(bad)
        await bot_send(ctx, f'Guessed {num}\n{ans}')
        print(f'Guessed {num}, was {cis}')

    @commands.command()
    async def randomword(self, ctx: Context):
        """Sends a random word from the dictionary.

        Syntax: ```plz randomword```
        """
        words = open(pjoin("folders", "text", "words_alpha.txt")).read().splitlines()
        await bot_send(ctx, random.choice(words))
        
    @commands.command()
    async def execute(self, ctx: Context, *, code):
        """Executes a piece of code.

        Syntax: ```plz execute <code>```
        Example: \n> plz execute\n> \```\n> print('test')\n> \```
        """
        @contextlib.contextmanager
        def stdoutIO(stdout=None):
            old = sys.stdout
            if stdout is None:
                stdout = StringIO()
            sys.stdout = stdout
            yield stdout
            sys.stdout = old

        if len(code.split('```')) != 3:
            await bot_send(ctx, "Type 'plz help execute' for proper syntax")
            return
        code = code.split('```')[1]

        with stdoutIO() as s:
            try:
                exec(code)
                if not s.getvalue():
                    await bot_send(ctx, "Didn't print anything")
                else:
                    await bot_send(ctx, s.getvalue())
            except:
                await bot_send(ctx, "Invalid code")

    @commands.command()
    async def badbot(self, ctx: Context):
        """Don't you dare.

        Syntax: ```plz badbot```
        """
        string = str(ctx.author)
        string = string[:string.find("#")]
        await bot_send(ctx.channel, f'{string} go commit die')

    @commands.command()
    async def goodbot(self, ctx: Context):
        """Compliments spaghett.

        Syntax: ```plz goodbot```
        """
        await bot_send(ctx, 'ty')

    @commands.command()
    async def me(self, ctx: Context):
        """Sends your name.

        Syntax: ```plz me```
        """
        channel = ctx.channel
        await bot_send(channel, ctx.author)

    @commands.command()
    async def sorry(self, ctx: Context, name=''):
        """Sends a heartfelt apology.

        Syntax: ```plz sorry <name>```
        Example: ```plz sorry Yelov```
        """
        channel = ctx.channel
        curr_user = str(ctx.author)[:str(ctx.author).find("#")]
        if not name:
            await bot_send(channel, "u r sorry to whom? dumbass")
        elif name.lower() == 'spaghett bot':
            await bot_send(channel, 'ye no problem bro')
        elif name.lower() == curr_user.lower():
            await bot_send(channel, "i'm sorry but the results came in - you're a narcissist")
        else:
            found = False
            for member in ctx.guild.members:
                name_d = str(member)[:str(member).find('#')]
                print(name, name_d)
                if name.lower() == name_d.lower():
                    name_d = member.id
                    found = True
                    break
            if not found:
                await bot_send(channel, """i'm sorry to user who doesn't exist.. 
    or mby it was someone's nickname, but i deleted that cuz of some bug i can't be bothered to fix :)""")
                return
            with open(pjoin("folders", "text", "sry.txt")) as f:
                send = f.readline()
            await bot_send(channel, f"<@{name_d}> {send}")

    @commands.command()
    async def epicshit(self, ctx: Context):
        """Just follow the instructions.

        Syntax: ```plz epicshit```
        """
        await bot_send(ctx, "Is this shit epic? [yes/no]")
        msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        if msg.content == "yes":
            await bot_send(ctx, "Fuck yea, bitch.\nYou want [kokot] or [pica]?")
            msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            if msg.content == "kokot":
                file = disnake.File(pjoin("folders", "imgs", "kokot.jpg"), filename=pjoin("folders", "imgs", "kokot.jpg"))
                await bot_send(ctx, file)
            elif msg.content == "pica":
                file = disnake.File(pjoin("folders", "imgs", "pica.jpg"), filename=pjoin("folders", "imgs", "pica.jpg"))
                await bot_send(ctx, file)
        elif msg.content == "no":
            await bot_send(ctx, "You want a slap? [yes/yes]")
            msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            if msg.content == "yes":
                await bot_send(ctx, "u kinky mofo ;)")
            else:
                await bot_send(ctx, f"there was no '{msg.content}' option you moron, get slapped *slaps*")
        else:
            await bot_send(ctx, "you stupid fuck, that's not [yes/no]")

def setup(bot):
    bot.add_cog(Misc(bot))
