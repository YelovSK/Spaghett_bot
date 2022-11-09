import os
import random
import urllib.request
from os.path import join as pjoin

import disnake
import praw
from disnake.ext import commands
from disnake.ext.commands import Context

from helpers import checks
from helpers.message_send import bot_send


class NSFW(commands.Cog):
    """lewd uwu"""

    COG_EMOJI = "😋"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_trustworthy()
    async def fap(self, ctx: Context, *, folder=""):
        """Sends a fap image. Random folder or specified [folder].

        Syntax: ```plz fap [folder]```
        Example: ```plz fap Asuka```
        """
        if folder != "":
            with open(pjoin("folders", "text", "fap.txt")) as f:
                folders = f.read().splitlines()
            folder = random.choice(folders)

        path = pjoin("F:\\Desktop start menu", "homework", folder)
        files = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f)) if
                 os.path.getsize(pjoin(path, f)) < 8_000_000]  # only files smaller than 8 MB
        chosen_file = pjoin(path, random.choice(files))
        file = disnake.File(chosen_file)
        await bot_send(ctx, f'****Folder:**** {folder}')
        try:
            await bot_send(ctx, file)
        except Exception as error:
            await bot_send(ctx, f"oopsie, failed to upload, error kodiQ: {error}")

    @commands.command()
    @checks.is_trustworthy()
    async def kawaii(self, ctx: Context, image_name=""):
        """Sends a kawaii image. Can send with [image_name].

        Syntax: ```plz kawaii [image_name]```
        Example: ```plz kawaii``` ```plz kawaii 1bunt.jpg```
        """

        if image_name != "":
            file = disnake.File(pjoin("folders", "send", "kawaii", image_name),
                                filename=pjoin("folders", "send", "kawaii", image_name))
            await bot_send(ctx, file)
            return

        with open(pjoin("folders", "text", "pseudorandom_kawaii.txt")) as f:
            order = f.readlines()
        path = pjoin("folders", "send", "kawaii")
        files = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f))]
        choice = random.choice(files[5:])

        with open(pjoin("folders", "text", "pseudorandom_kawaii.txt"), 'w') as f:
            o = order[1:] if len(order) == len(files) else order
            for img in o:
                f.write(img)
            f.write(f'{choice}\n')

        try:
            await bot_send(ctx, disnake.File(pjoin(path, choice)))
        except Exception as error:
            await bot_send(ctx, "oopsie, failed to upload kawaii")
            print(str(error) + '\n' + choice)

    @commands.command()
    async def reddit(self, ctx: Context, sub, text=None):
        """Sends a Reddit post from subreddit.

        Syntax: ```plz reddit <subreddit> ["text"]```
        Example: ```plz reddit 2meirl4meirl``` ```plz reddit askreddit text```
        """
        with open(pjoin("folders", "text", "reddit.txt")) as f:
            data = f.read().splitlines()

        reddit = praw.Reddit(client_id=data.pop(),
                             client_secret=data.pop(),
                             username=data.pop(),
                             password=data.pop(),
                             user_agent=data.pop())

        subreddit = reddit.subreddit(sub)

        posts = [post for post in subreddit.hot(limit=10) if not post.stickied]
        random.shuffle(posts)

        if text == "text":
            posts = [post for post in posts if post.selftext]
            if not posts:
                await bot_send(ctx, "No post with selftext.")
                return
            await bot_send(ctx, f"**Subreddit**: r/{sub}")
            await bot_send(ctx, f"**Title**: {posts[0].title}")
            await bot_send(ctx, f"{posts[0].ups}⇧ | {posts[0].downs}⇩ \n\n{posts[0].selftext}")
            return

        for post in posts:
            url = post.url
            if url.endswith(".jpg") or url.endswith(".png"):
                urllib.request.urlretrieve(url, pjoin("folders", "send", "reddit.png"))
                await bot_send(ctx, f"**Subreddit**: r/{sub}")
                await bot_send(ctx, f"**Title**: {post.title}")
                await bot_send(ctx, disnake.File(pjoin("folders", "send", "reddit.png")))
                return
        await bot_send(ctx, "*Couldn't find an image.*")

    @commands.command()
    async def coomer(self, ctx: Context):
        """Sends an image from a random lewd subreddit.

        Syntax: ```plz coomer```
        """
        subreddit = random.choice(("petitegonewild", "gonewild", "shorthairedwaifus", "zettairyouiki", "hentai",
                                   "asiansgonewild", "averageanimetiddies", "upskirthentai", "thighhighs", "rule34",
                                   "chiisaihentai"))

        await self.reddit(ctx, subreddit)


def setup(bot):
    bot.add_cog(NSFW(bot))
