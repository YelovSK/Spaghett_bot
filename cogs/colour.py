import disnake
import random

from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Context
from os.path import join as pjoin
from PIL import Image


class Colour(commands.Cog):
    """send and name colours"""

    COG_EMOJI = "🟣"

    def __init__(self, bot):
        self.bot = bot
        self.curr_colour = None


    @commands.command()
    async def colour(self, ctx: Context):
        """Sends an image of a random colour.

        Syntax: ```plz colour```
        """
        r, g, b = random.randrange(256), random.randrange(256), random.randrange(256)
        file_path = pjoin("folders", "send", "colour.jpg")
        Image.new('RGB', (400, 400), (r, g, b)).save(file_path)
        self.curr_colour = (r, g, b)
        await bot_send(ctx, disnake.File(file_path, filename="colour.jpg"))


    @commands.command()
    async def namecolour(self, ctx: Context, *, name):
        """Names the last generated colour.

        Syntax: ```plz namecolour <name>```
        Example: ```plz namecolour Shiny Boi```
        """
        if self.curr_colour is None:
            await bot_send(ctx, "No colour was generated")
            return
        r, g, b = self.curr_colour
        with open(pjoin("folders", "text", "colours.txt"), 'a') as f:
            f.write(f'{r} {g} {b} : {name}\n')


    @commands.command()
    async def colourlist(self, ctx: Context):
        """Lists the names of all named colours.

        Syntax: ```plz colourlist```
        """
        with open(pjoin("folders", "text", "colours.txt")) as f:
            arr = [line[line.find(':')+2: -1] for line in f]
        send = ''.join(f'{prvok}\n' for prvok in arr)
        await bot_send(ctx, send)


    @commands.command()
    async def showcolour(self, ctx: Context, *, name):
        """Shows a colour with the given name.

        Syntax: ```plz showcolour <name>```
        Example: ```plz showcolour literally piss```
        """
        for line in open(pjoin("folders", "text", "colours.txt")).read().splitlines():
            rgb, curr_name = line.split(" : ")
            if curr_name == name:
                r, g, b = [int(c) for c in rgb.split()]
                img = Image.new('RGB', (400, 400), (r, g, b))
                img.save(pjoin("folders", "send", "colour.jpg"))
                await bot_send(ctx, disnake.File(pjoin("folders", "send", "colour.jpg"), pjoin("folders", "send", "colour.jpg")))
                return

        await bot_send(ctx, "Colour not found")


def setup(bot):
    bot.add_cog(Colour(bot))
