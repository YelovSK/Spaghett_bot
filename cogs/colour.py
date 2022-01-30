import disnake
import random
import os

from helpers.message_send import bot_send
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
        self.file_path = pjoin("folders", "text", "colours.txt")
        self.colour_path = pjoin("folders", "send", "colour.jpg")
        if not os.path.exists(self.file_path):
            with open(self.file_path) as f:
                pass

    @commands.command()
    async def colour(self, ctx: Context):
        """Sends an image of a random colour and prompts to give it a name.

        Syntax: ```plz colour```
        """
        r, g, b = random.randrange(256), random.randrange(256), random.randrange(256)
        img = Image.new(mode="RGB", size=(400, 400), color=(r, g, b))
        img.save(self.colour_path)
        await bot_send(ctx, disnake.File(self.colour_path, filename="colour.jpg"))
        await bot_send(ctx, "Give name (or 'no' to exit'):")
        response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        name = response.content
        if name.lower() == "no":
            sad_answers = ("rude", "pff, k", "the color is crying, u happy?", "'no' deez nuts")
            await bot_send(ctx, random.choice(sad_answers))
            return
        with open(self.file_path, 'a') as f:
            f.write(f'{r} {g} {b} : {name}\n')

    @commands.command()
    async def colourlist(self, ctx: Context):
        """Lists the names of all named colours.

        Syntax: ```plz colourlist```
        """
        await bot_send(ctx, "\n".join(self.get_names_cols_map().keys()))

    @commands.command()
    async def showcolour(self, ctx: Context, *, name):
        """Shows a colour with the given name.

        Syntax: ```plz showcolour <name>```
        Example: ```plz showcolour literally piss```
        """
        colours = self.get_names_cols_map()
        if name not in colours.keys():
            await bot_send(ctx, "Colour not found")
            return
        r, g, b = [int(c) for c in colours[name].split()]
        img = Image.new('RGB', (400, 400), (r, g, b))
        img.save(self.colour_path)
        await bot_send(ctx, disnake.File(self.colour_path,
                                         self.colour_path))

    @commands.command()
    async def deletecolour(self, ctx: Context, *, name):
        """Deletes a colour with the given name.

        Syntax: ```plz deletecolour <name>```
        Example: ```plz deletecolour literally piss```
        """
        colours = self.get_names_cols_map()
        if name not in colours.keys():
            await ctx.send("Colour not found")
            return
        del colours[name]
        with open(self.file_path, "w") as f:
            for curr_name, curr_colour in colours.items():
                f.write(f"{curr_colour} : {curr_name}\n")
        await ctx.send(f"Deleted '{name}'")

    def get_names_cols_map(self) -> dict[str, str]:
        res = {}
        with open(self.file_path) as f:
            for line in f:
                col, name = line.strip().split(" : ")
                res[name] = col
        return res


def setup(bot):
    bot.add_cog(Colour(bot))
