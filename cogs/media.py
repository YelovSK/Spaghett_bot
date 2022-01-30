import disnake
import random
import os

from helpers.message_send import bot_send
from helpers import checks
from disnake.ext import commands
from PIL import Image, ImageFont, ImageDraw
from disnake.ext.commands import Context
from os.path import join as pjoin


class Media(commands.Cog):
    """sending images/videos/audio"""

    COG_EMOJI = "🎥"

    def __init__(self, bot):
        self.bot = bot
        self.videos_path = pjoin("folders", "send", "videos")
        self.media_path = pjoin("folders", "send")

    async def send_video(self, ctx: Context, name):
        send = pjoin(self.videos_path, name)
        await bot_send(ctx, disnake.File(send, send))

    async def send_file(self, ctx: Context, name):
        send = pjoin(self.media_path, name)
        await bot_send(ctx, disnake.File(send, send))

    @commands.command()
    async def AAA(self, ctx: Context):
        """Sends shinji_scream.mp4.

        Syntax: ```plz AAA```
        """
        await self.send_video(ctx, "aaa.mp4")

    @commands.command()
    async def EEE(self, ctx: Context):
        """Sends subaru_scream.mp4.

        Syntax: ```plz EEE```
        """
        await self.send_video(ctx, "EEE.mp4")

    @commands.command()
    async def AAAEEE(self, ctx: Context):
        """Sends EoE_ptsd.mp4.

        Syntax: ```plz AAAEEE```
        """
        await self.send_video(ctx, "AAAEEE.mp4")

    @commands.command()
    async def whOMEGALUL(self, ctx: Context):
        """Sends a random video making fun of Rem disappearing.

        Syntax: ```plz whOMEGALUL```
        """
        await self.send_video(ctx, "who" + str(random.randint(1, 4)) + ".mp4")

    @commands.command()
    async def deth(self, ctx: Context):
        """Sends Komm Susser Tod..

        Syntax: ```plz deth```
        """
        await self.send_file(ctx, "tod.mp3")

    @commands.command()
    async def aeoo(self, ctx: Context):
        """Sends Sends a spook sound from Re:Zero.

        Syntax: ```plz aeoo```
        """
        await self.send_file(ctx, "aeoo.mp3")

    @commands.command()
    async def meme(self, ctx: Context):
        """Sends a random meme.

        Syntax: ```plz meme```
        """
        path = pjoin("folders", "memes")
        files = [f for f in os.listdir(path) if os.path.isfile(pjoin(path, f))]
        choice = random.choice(files)
        img = Image.open(pjoin(path, choice))

        save = pjoin(self.media_path, "meme.png")

        img.save(save)
        file = disnake.File(save, filename=save)
        await bot_send(ctx, file)

    @commands.command()
    async def image(self, ctx: Context, img_name='', *, text=''):
        """Puts text on an image. Lists images if no argument.

        Syntax: ```plz image [image] [text]```
        Example: ```plz image //lists images``` ```plz image adolf haha funny hitler```
        """
        if not img_name:
            path = pjoin("folders", "imgs")
            files = [f[:-4] for f in os.listdir(path) if os.path.isfile(pjoin(path, f))]
            send = "\n".join(files)
            await bot_send(ctx, 'Send with <image_name> <text>')
            await bot_send(ctx, f'Image list:\n{send}')
            return

        base_width = 1200
        img = None
        for ext in (".png", ".jpg", ".bmp", ".jpeg"):
            curr_path = pjoin("folders", "imgs", img_name + ext)
            if os.path.exists(curr_path):
                img = Image.open(curr_path)
                break
        if img is None:
            await bot_send(ctx, "Image not found")
            return

        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), Image.ANTIALIAS)
        draw = ImageDraw.Draw(img)

        message = ' '.join(list(text))

        char_count = len(message)
        for offset, col in ((230, "black"), (200, "white")):
            font = ImageFont.truetype(pjoin("folders", "assets", "font.ttf"),
                                      int((base_width + offset) / ((char_count / 2) + 4)))
            fontsize = int((base_width + offset) / ((char_count / 2) + 3))
            w, _ = draw.textsize(message, font=font)
            draw.text(((img.width - w) / 2, img.height - (fontsize / 1.2) - 30), message, font=font, fill=col)
        img.save(pjoin(self.media_path, "meme.png"))

        await self.send_file(ctx, "meme.png")

    @commands.command()
    async def video(self, ctx: Context, *, video=''):
        """Sends a video. Send with no argument for list of videos.

        Syntax: ```plz video [video_name]```
        Examples: ```plz video //lists videos``` ```plz video AAA```
        """
        videos = [f for f in os.listdir(self.videos_path) if f.endswith(".mp4")]

        if not video:
            vid_list = ", ".join(videos)
            await bot_send(ctx, f'List of videos: {vid_list}')
            return

        if f"{video}.mp4" not in videos:
            await bot_send(ctx, 'No such video.')
        else:
            await self.send_video(ctx, f"{video}.mp4")

    @commands.command()
    @checks.is_owner()
    async def text(self, ctx: Context, filename=''):
        """Sends a text file.

        Syntax: ```plz text <filename>```
        """
        with open(pjoin("folders", "text", f"{filename}.txt")) as f:
            await bot_send(ctx, f.read())


def setup(bot):
    bot.add_cog(Media(bot))
