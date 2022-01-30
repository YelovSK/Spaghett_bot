import disnake
import random
import math
import json
import sys
import contextlib

from io import StringIO
from datetime import timezone
from PyDictionary import PyDictionary
from helpers.message_send import bot_send
from helpers import checks
from disnake.ext import commands
from disnake.ext.commands import Bot
from disnake.ext.commands import Context
from os.path import join as pjoin
from pyowm.owm import OWM


with open("config.json") as cfg:
    config = json.load(cfg)


class Misc(commands.Cog):
    """idk, random stuff"""

    COG_EMOJI = "💡"

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def insult(self, ctx: Context, *, username):
        """Randomly generated insult. Argument is username, not nick.

        Syntax: ```plz insult <username>```
        Example: ```plz insult yomama```
        """
        username = username.lower()
        if username == ctx.author.name:
            await bot_send(ctx, "Ye, same buddy, I also hate myself")
            return
        if username == "spaghett bot":
            with open(pjoin("folders", "text", "insult_bot_message.txt")) as f:
                await bot_send(ctx, f.read().replace("*name*", ctx.author.mention))
                return
        for member in ctx.guild.members:
            if member.name.lower() == username:
                with open(pjoin("folders", "text", "insults.json"), encoding="utf-8-sig") as f:
                    insults = json.load(f)
                adj = random.choice(insults["adjectives"])
                noun = random.choice(insults["nouns"])
                act = random.choice(insults["actions"])
                await bot_send(ctx, f"{ctx.author.mention} go {act}, you {adj} {noun}.")
                return
        await bot_send(ctx, "No such member. Dumb fuck.")

    @commands.command()
    async def fuck(self, ctx: Context):
        """Random swear word.

        Syntax:```plz fuck```
        """
        with open(pjoin("folders", "text", "swear.txt")) as f:
            words = f.read().splitlines()
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

        with open(pjoin("folders", "text", "f.txt"), "w") as f:
            f.write("\n".join(order))

        await bot_send(ctx, choice)

    @commands.command()
    async def addf(self, ctx: Context, *, string):
        """Adds message to the f list (when using plz f).

        Syntax: ```plz addf <message>```
        Example: ```plz addf very many sad :cccc```
        """
        with open(pjoin("folders", "text", "f.txt"), "a") as file:
            file.write(f"{string}\n")

    @commands.command()
    async def a(self, ctx: Context):
        """Prints 4-20 A-s. Keeps track of stats with plz staats.

        Syntax: ```plz a```
        """
        auth = str(ctx.author)[: str(ctx.author).find("#")]
        if random.randrange(50) == 22:
            await bot_send(ctx, f"****a.****\n{auth}")
            return
        num = random.randint(4, 20)
        curr_user = str(ctx.author)
        send = ["A" * num]
        if num == 20:
            send.append("Full-length A")
        elif num == 4:
            send.append(f"ngl {auth}, that's kinda cringe")

        await bot_send(ctx, "\n".join(send))
        stats = self.read_a_stats()
        self.write_a_stats(stats, curr_user, num)

    def read_a_stats(self):
        stats = {}
        with open(pjoin("folders", "text", "a_stats.txt")) as f:
            for split_line in [l.split() for l in f]:
                stats[split_line[0]] = [int(s) for s in split_line[1:]]
        return stats

    def write_a_stats(self, stats: dict, user: str, num: int):
        with open(pjoin("folders", "text", "a_stats.txt"), "w") as f:
            for name, stat in stats.items():
                guess_count, twenty_count, total_sum = stat
                if name == user:
                    guess_count += 1
                    total_sum += num
                if num == 20:
                    twenty_count += 1
                f.write(f"{name} {guess_count} {twenty_count} {total_sum}\n")

    @commands.command()
    async def staats(self, ctx: Context, everyone=""):
        """Stats for the plz a function. Percetange of full-length A-s. Argument ["all"] for everyone's stats.

        Syntax: ```plz staats ["all"]```
        Example: ```plz staats all```
        """
        curr_user = str(ctx.author)
        stats = self.read_a_stats()
        out = []
        for name, stat in stats.items():
            guess_count, twenty_count, total_sum = stat
            if guess_count == 0:
                continue
            if name == curr_user or everyone == "all":
                max = round(twenty_count/guess_count*100, 2)
                avg = round(total_sum/guess_count, 2)
                curr_name = name[:name.find("#")]
                out.append(f"""{curr_name}: MAX - {max}% | AVG - {avg} | ALL - {guess_count}""")
        await bot_send(ctx, "\n".join(out))

    @commands.command()
    async def dict(self, ctx: Context, *, word: str, action: str):
        """Online dictionary for synonyms, antonyms and definitions.

        Syntax: ```plz dict <word> ["synonyms" / "antonyms" / "define"]```
        Example: ```plz dict sadness antonyms```
        """
        dictionary = PyDictionary()
        output = ""
        if action == "define":
            output += f"**Definitions of {word}**\n"
            definitions = dictionary.meaning(word)
            for type, meanings in definitions.items():
                output += f"*{type}:*\n"
                for meaning in meanings:
                    output += f"- {meaning}\n"
        elif action in ("synonyms", "antonyms"):
            if action == "synonyms":
                words = dictionary.synonym(word)
            else:
                words = dictionary.antonym(word)
            if not words:
                await bot_send(ctx, "Didn't find any words")
                return
            output += f"**{action.capitalize()} of {word}:** "
            for word in words:
                output += f"{word}, "
            output = output[:-2]
        await bot_send(ctx, output)

    @commands.command()
    async def weather(self, ctx: Context, *, specify=""):
        """Shows weather info.

        Syntax: ```plz weather [info]```
        Example: ```plz weather temperature``` ```plz weather in Tokyo```
        """
        owm = OWM(config["owm"])
        mgr = owm.weather_manager()
        info = {"location": specify[2:] if specify.startswith("in") else "Modra, SK"}
        try:
            place = mgr.weather_at_place(info["location"])
        except Exception as e:
            await bot_send(ctx, f"Error: {e}")
            return
        weather = place.weather
        temp = weather.temperature("celsius")["temp"]
        info["temperature"] = f"""{weather.temperature('celsius')['temp']}°C"""
        info["humidity"] = f"{weather.humidity}%"
        info["status"] = weather.detailed_status
        info["wind"] = f"""{weather.wind(unit='meters_sec')['speed']}km/h"""
        info["sunrise"] = weather.sunrise_time(timeformat="date")
        info["sunset"] = weather.sunset_time(timeformat="date")

        with open(pjoin("folders", "text", "weather_comment.json"), encoding="utf-8-sig") as f:
            comments = json.load(f)

        temp_rounded = math.floor(temp)
        if temp_rounded in comments:
            info["temperature"] += f" (*{random.choice(comments[temp_rounded])}*)"

        def utc_to_local(utc_dt):
            return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%X")

        info["sunrise"] = utc_to_local(info["sunrise"])
        info["sunset"] = utc_to_local(info["sunset"])

        if not specify or specify.startswith("in"):
            out = "\n".join([f"**{key.capitalize()}:** {val}" for key, val in info.items()])
            await bot_send(ctx, out)
        else:
            send = info[specify.lower()]
            await bot_send(ctx, f"""**{specify.capitalize()}:** {send}""")

    @commands.command()
    async def word(self, ctx: Context):
        """Local dictionary. Usage via prompts.

        Syntax: ```plz word```
        """
        await bot_send(ctx, "What do you want? [list / define / add]")
        response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        answer = response.content
        if answer not in ("list", "define", "add"):
            await bot_send(ctx, "Invalid response")
            return
        dictionary_path = pjoin("folders", "text", "dictionary.txt")
        if answer == "list":
            with open(dictionary_path) as f:
                words = [line.split(" : ")[0] for line in f.read().splitlines()]
            await bot_send(ctx, "\n".join(words))
        elif answer == "define":
            await bot_send(ctx, "Word to define:")
            response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
            word_find = response.content
            with open(dictionary_path) as f:
                for line in f:
                    word, definition = line.strip().split(" : ")
                    if word == word_find:
                        await bot_send(ctx, definition)
                        return
            await bot_send(ctx, "Word not found")
        elif answer == "add":
            await bot_send(ctx, "Word to add:")
            response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
            word_add = response.content
            await bot_send(ctx, "Definition:")
            response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
            definition_add = response.content
            with open(dictionary_path, "a") as f:
                f.write(f"{word_add} : {definition_add}\n")

    @commands.command()
    async def findword(self, ctx: Context, where: str, part: str):
        """Finds a word that begins/ends with <word_part>

        Syntax: ```plz findword <"begins"/"ends"> <word_part>```
        Example: ```plz findword begins holo```  ```plz findword ends caust```
        """
        if where not in ("begins", "ends"):
            await bot_send(ctx, "Need to specify with begins/ends")
            return
        words = set()
        with open(pjoin("folders", "text", "words_alpha.txt")) as f:
            for line in f:
                words.add(line.strip())
        found_words = []
        if where == "begins":
            for word in words:
                if word.startswith(part):
                    found_words.append(word)
        elif where == "ends":
            for word in words:
                if word.endswith(part):
                    found_words.append(word)
        if found_words:
            await bot_send(ctx, random.choice(found_words))
        else:
            await bot_send(ctx, "Didn't find any word")

    @commands.command()
    async def no(self, ctx: Context):
        """Sends 30 empty lines (for when you don't want to see something).

        Syntax: ```plz no```
        """
        out = "‎\n" * 30
        await bot_send(ctx, out)

    @commands.command()
    async def asdlkj(self, ctx: Context):
        """Sends 2000 random characters.

        Syntax: ```plz asdlkj```
        """
        if str(ctx.author)[: str(ctx.author).find("#")] != "Yelov":
            await bot_send(
                ctx, "What is asdlkj. Wtf do u want from me. Stop typing random shit on your keyboard."
            )
            return
        send = "".join(chr(random.randint(33, 126)) for _ in range(2000))
        await bot_send(ctx, send)

    @commands.command()
    async def answer(self, ctx: Context, *, question):
        """Magic 8-ball.

        Syntax: ```plz answer <question>```
        Example: ```plz answer is life worth living?```
        """
        yes = (
            "for sure dawg",
            "you fucking bet",
            "you didn't even have to ask",
            "obviously yes",
            "yeh i would say so",
            "sadly yah",
            "+",
        )
        maybe = (
            "idk, like 32.2% no",
            "haha idk lmao",
            "not 100% sure",
            "rather yes than no",
            "why r u asking that",
            "i think so",
            "idk and idc",
            "maybe yes, maybe no, maybe go fuck yourself",
            "50/50",
            "49/51",
        )
        no = (
            "wtf, no dude",
            "hell nawh",
            "0",
            "1",
            "the electricity pole or smth, the - one",
            "N. O.",
            "prolly no",
            "my dog says no",
            "most probably not if i do say so myself",
            "anta baka?!?!! zettai chigau!",
        )
        answers = (yes, maybe, no)
        await bot_send(
            ctx, f"**{ctx.author.name}:** {question}\n**Answer:** {random.choice(random.choice(answers))}"
        )

    @commands.command()
    async def cut(self, ctx: Context, *, message):
        """Splits the message into multiple lines.

        Syntax: ```plz cut <text>```
        Example: ```plz cut good jokes mate real funny see you at FUCK YOUJ```
        """
        if len(message.split()) == 1:
            await bot_send(ctx, "\n".join(list(message)))
        else:
            await bot_send(ctx, "\n".join(message.split()))

    @commands.command()
    async def delete(self, ctx: Context, num=1):
        """Deletes the last [num] messages. Default is 1.

        Syntax: ```plz delete [num]```
        Example: ```plz delete``` ```plz delete 5```
        """
        last_messages = await ctx.channel.history().flatten()
        bot_messages = [mssg for mssg in last_messages if mssg.author == self.bot.user][:num]
        print(f"Gonna delete {len(bot_messages)} messages")
        for bot_message in bot_messages:
            await bot_message.delete()
        print(f"Deleted {len(bot_messages)} messages")

    @commands.command()
    async def deleteuser(self, ctx: Context, num=1):
        """Deletes the last [num] messages of a user. Default is 1.
        Will get prompted to give username.

        Syntax: ```plz deleteuser [num]```
        Example: ```plz deleteuser``` ```plz deleteuser 5```
        """
        await bot_send(ctx, "Give username:")
        username_mssg: disnake.Message = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        username = username_mssg.content
        last_messages = await ctx.channel.history().flatten()
        username_mssgs = [mssg for mssg in last_messages if mssg.author.name == username][:num]
        print(f"Gonna delete {len(username_mssgs)} messages")
        for user_mssg in username_mssgs:
            await user_mssg.delete()
        print(f"Deleted {len(username_mssgs)} messages")

    @commands.command()
    async def guess(self, ctx: Context, *, num):
        """Higher/lower guessing game. Generated number is from 0 to 10_000.

        Syntax: ```plz guess <num>```
        Example: ```plz guess 322```
        """
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
            await bot_send(
                ctx,
                f"""Guessed in {int(guesses)+1}
    tries\n{curr_user[:curr_user.find("#")]} guessed correctly
    {users[curr_user]+1} times""",
            )
            change = True

        if change:
            with open(pjoin("folders", "text", "guess.txt"), "w") as file:
                file.write(str(random.randrange(10_000)) + "\n" + "0")
            with open(pjoin("folders", "text", "guess_stats.txt"), "w") as file:
                for name, points in users.items():
                    if name == curr_user:
                        points += 1
                    file.write(f"{name} {points}\n")
            return

        if int(num) < int(current):
            await bot_send(ctx, "Higher")
        else:
            await bot_send(ctx, "Lower")
        with open(pjoin("folders", "text", "guess.txt"), "w") as file:
            file.write(f"{current}\n{int(guesses)+1}")

    @commands.command()
    async def number(self, ctx: Context, *, num):
        """Guess a number from 1 to 100.

        Syntax: ```plz number <num>```
        Example: ```plz number 69```
        """
        with open(pjoin("folders", "text", "num_answers.json"), encoding="utf-8-sig") as f:
            responses = json.load(f)
        if not num.isnumeric():
            await bot_send(ctx, f'Ah yes, {num} - the perfect "num". Moron.')
            return
        num_int = int(num)
        random_num = random.randint(1, 100)
        if num_int == random_num:
            await bot_send(ctx, random.choice(responses["good"]))
        else:
            await bot_send(ctx, random.choice(responses["bad"]))
            await bot_send(ctx, f"The number was {random_num}")

    @commands.command()
    async def randomword(self, ctx: Context):
        """Sends a random word from the dictionary.

        Syntax: ```plz randomword```
        """
        with open(pjoin("folders", "text", "words_alpha.txt")) as f:
            words = f.read().splitlines()
        await bot_send(ctx, random.choice(words))

    @commands.command()
    @checks.is_trustworthy()
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

        if len(code.split("```")) != 3:
            await bot_send(ctx, "Type 'plz help execute' for proper syntax")
            return
        code = code.split("```")[1]

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
        await bot_send(ctx, "look at your stupid fucking ugly face")
        await bot_send(ctx, ctx.author.avatar)
        await bot_send(ctx, f"{ctx.author.mention} go commit die")

    @commands.command()
    async def goodbot(self, ctx: Context):
        """Compliments spaghett.

        Syntax: ```plz goodbot```
        """
        await bot_send(ctx, "ty")

    @commands.command()
    async def me(self, ctx: Context):
        """Sends your name.

        Syntax: ```plz me```
        """
        await bot_send(ctx, f"{ctx.author.mention} - {ctx.author}")
        await bot_send(ctx, ctx.author.avatar.url)

    @commands.command()
    async def sorry(self, ctx: Context, name):
        """Sends a heartfelt apology.

        Syntax: ```plz sorry <name>```
        Example: ```plz sorry Yelov```
        """
        curr_user = str(ctx.author)[: str(ctx.author).find("#")]
        if name.lower() == "spaghett bot":
            await bot_send(ctx, "ye no problem bro")
        elif name.lower() == ctx.author.name.lower():
            await bot_send(ctx, "i'm sorry but the results came in - you're a narcissist")
        else:
            for member in ctx.guild.members:
                if name.lower() == member.name.lower():
                    with open(pjoin("folders", "text", "sry.txt")) as f:
                        send = f.read().replace("*", member.name)
                    await bot_send(ctx, f"{member.mention}\n{send}")
                    return
            await bot_send(ctx, "Sorry to a non-existent user")

    @commands.command()
    async def epicshit(self, ctx: Context):
        """Just follow the instructions.

        Syntax: ```plz epicshit```
        """
        await bot_send(ctx, "Is this shit epic? [yes/no]")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        if msg.content == "yes":
            await bot_send(ctx, "Fuck yea, bitch.\nYou want [kokot] or [pica]?")
            msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
            if msg.content == "kokot":
                file = disnake.File(
                    pjoin("folders", "imgs", "kokot.jpg"), filename=pjoin("folders", "imgs", "kokot.jpg")
                )
                await bot_send(ctx, file)
            elif msg.content == "pica":
                file = disnake.File(
                    pjoin("folders", "imgs", "pica.jpg"), filename=pjoin("folders", "imgs", "pica.jpg")
                )
                await bot_send(ctx, file)
        elif msg.content == "no":
            await bot_send(ctx, "You want a slap? [yes/yes]")
            msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
            if msg.content == "yes":
                await bot_send(ctx, "u kinky mofo ;)")
            else:
                await bot_send(ctx, f"there was no '{msg.content}' option you moron, get slapped *slaps*")
        else:
            await bot_send(ctx, "you stupid fuck, that's not [yes/no]")


def setup(bot):
    bot.add_cog(Misc(bot))
