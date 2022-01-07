import disnake
import random
import os
import asyncio
import praw
import urllib

from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Context
from os.path import join as pjoin
from PIL import Image


class NSFW(commands.Cog):
    """lewd uwu"""

    COG_EMOJI = "😋"

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def fap(self, ctx: Context, *, folder=''):
        """Sends a fap image. Random folder or specified [folder].

        Syntax: ```plz fap [folder]```
        Example: ```plz fap Asuka```
        """
        if not folder:
            folders = open(pjoin("folders", "text", "fap.txt")).read().splitlines()
            folder = random.choice(folders)

        path = pjoin("F:\\Desktop start menu", "homework", folder)
        files = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f)) if os.path.getsize(pjoin(path, f)) < 8_000_000]
        file_path = pjoin("folders", "send", "homework.png")
        Image.open(pjoin(path, random.choice(files))).save(file_path)
        file = disnake.File(file_path, filename=file_path)
        await bot_send(ctx.channel, f'****Folder:**** {folder}')
        try:
            await bot_send(ctx, file)
        except Exception as error:
            await bot_send(ctx, 'oopsie, failed to upload, error kodiQ: ' + str(error))

    @commands.command()
    async def kawaii(self, ctx: Context, do=''):
        """Sends a kawaii image. Send with 'cum' to send every 4h or [image_name].

        Syntax: ```plz kawaii ["cum" / image_name]```
        Example: ```plz kawaii``` ```plz kawaii cum``` ```plz kawaii 1bunt.jpg```
        """
        channel = ctx.channel
        if do == 'cum':
            channel = self.bot.get_channel(680494725165219958)

        if do and do != 'cum':
            file = disnake.File(pjoin("folders", "send", "kawaii", do),
                                filename=pjoin("folders", "send", "kawaii", do))
            await bot_send(channel, file)
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
        file = disnake.File(save, filename=save)
        try:
            await bot_send(channel, file)
        except Exception as error:
            await bot_send(channel, 'oopsie, failed to upload kawaii')
            print(error + '\n' + choice)
        if do:
            await asyncio.sleep(3600*4)
            await self.kawaii(ctx, 'cum')
            
    @commands.command()
    async def reddit(self, ctx: Context, sub, text=None):
        """Sends a Reddit post from subreddit.

        Syntax: ```plz reddit <subreddit> ["text"]```
        Example: ```plz reddit 2meirl4meirl``` ```plz reddit askreddit text```
        """
        data = open(pjoin("folders", "text", "reddit.txt")).read().splitlines()

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
                        await bot_send(ctx, f'****Subreddit:**** r/{sub}\n****Title:**** {post.title}\n{post.ups}⇧ | {post.downs}⇩ \n\n{post.selftext}')
                        return
                except Exception as e:
                    print(e)
            await bot_send(ctx, 'No post with selftext.')
            return

        for post in posts:
            url = post.url
            ext = url[-4:]
            if ext in (".jpg", ".png"):
                urllib.request.urlretrieve(url, pjoin("folders", "send", "reddit.png"))
                break
            if post == posts[-1]:
                await bot_send(ctx, "*Couldn't find an image.*")
                return
        await bot_send(ctx, f'****Subreddit****: r/{sub}')
        await bot_send(ctx.channel, disnake.File(pjoin("folders", "send", "reddit.png"), pjoin("folders", "send", "reddit.png")))
            
    @commands.command()
    async def coomer(self, ctx: Context):
        """Sends an image from a random lewd subreddit.

        Syntax: ```plz coomer```
        """
        channel = ctx.channel
        chose = random.choice(["petitegonewild", "gonewild", "shorthairedwaifus", "zettairyouiki", "hentai",
                            "asiansgonewild", "averageanimetiddies", "upskirthentai", "thighhighs", "rule34",
                            "chiisaihentai"])

        await bot_send(channel, f'r/{chose}')
        await self.reddit(ctx, chose)

def setup(bot):
    bot.add_cog(NSFW(bot))
