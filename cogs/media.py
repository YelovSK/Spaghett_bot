import disnake
import random
import os

from message_send import bot_send
from disnake.ext import commands
from PIL import Image, ImageFont, ImageDraw
from disnake.ext.commands import Context
from os.path import join as pjoin


class Media(commands.Cog):

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
        await self.send_video(ctx, "aaa.mp4")
        
    @commands.command()
    async def EEE(self, ctx: Context):
        await self.send_video(ctx, "EEE.mp4")
        
    @commands.command()
    async def AAAEEE(self, ctx: Context):
        await self.send_video(ctx, "AAAEEE.mp4")
        
    @commands.command()
    async def whOMEGALUL(self, ctx: Context):
        await self.send_video(ctx, "who" + str(random.randint(1, 4)) + ".mp4")
        
    @commands.command()
    async def deth(self, ctx: Context):
        await self.send_file(ctx, "tod.mp3")
        
    @commands.command()
    async def aeoo(self, ctx: Context):
        await self.send_file(ctx, "aeoo.mp3")
        
    @commands.command()
    async def meme(self, ctx: Context):
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
        if not img_name:
            path = pjoin("folders", "imgs")
            files = [f[:-4] for f in os.listdir(path) if os.path.isfile(pjoin(path, f))]
            send = "\n".join(files)
            await bot_send(ctx, 'Send with <image_name> <text>')
            await bot_send(ctx, f'Image list:\n{send}')
            return

        basewidth = 1200
        img = None
        for ext in (".png", ".jpg", ".bmp", ".jpeg"):
            curr_path = pjoin("folders", "imgs", img_name + ext)
            if os.path.exists(curr_path):
                img = Image.open(curr_path)
                break
        if img is None:
            await self.my_send(ctx, "Image not found")
            return

        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        draw = ImageDraw.Draw(img)

        message = ' '.join(list(text))

        char_count = len(message)
        for offset, col in ((230, "black"), (200, "white")):
            font = ImageFont.truetype(pjoin("folders", "assets", "font.ttf"), int((basewidth + offset) / ((char_count / 2) + 4)))
            fontsize = int((basewidth + offset) / ((char_count / 2) + 3))
            w, _ = draw.textsize(message, font=font)
            draw.text(((img.width-w) / 2, img.height - (fontsize / 1.2) - 30), message, font=font, fill=col)
        img.save(pjoin(self.media_path, "meme.png"))

        await self.send_file(ctx, "meme.png")
        
    @commands.command()
    async def video(self, ctx: Context, *, video=''):
        videos = [f for f in os.listdir(self.videos_path) if f.endswith(".mp4")]

        if not video:
            vid_list = ''.join(f"{vid[:vid.find('.')]}, " for vid in videos)
            await bot_send(ctx, f'List of videos: {vid_list}')
            return

        if f"{video}.mp4" not in videos:
            await bot_send(ctx, 'No such video.')
        else:
            await self.send_video(ctx, f"{video}.mp4")
            
    @commands.command()
    async def text(self, ctx: Context, filename=''):
        if not filename:
            await bot_send(ctx, 'specify file name')
            return
        await bot_send(ctx, "".join(open(pjoin("folders", "text", f"{filename}.txt")).readlines()))


def setup(bot):
    bot.add_cog(Media(bot))
