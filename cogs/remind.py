import asyncio

from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Context


class Remind(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.stop = False
        self.remindrun = False

    async def remind(self, ctx: Context, *, string):
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
            await bot_send(ctx, f'Reminding in {when} minutes')
            mul = 60
        else:
            if when % 1 == 0:
                await bot_send(ctx, f'Reminding in {round(when)} hours')
            else:
                await bot_send(ctx, f'Reminding in {round(when // 1)}h{round((when % 1) * 60)}m')
            mul = 3600
        self.remindrun = True
        if repeat:
            self.stop = False
            for _ in range(100):
                if self.stop:
                    break
                await asyncio.sleep(round(when * mul))
                await bot_send(ctx, send)
        else:
            await asyncio.sleep(round(when * mul))
            await bot_send(ctx, send)
            self.remindrun = False

    async def remind_active(self, ctx: Context):
        if self.remindrun:
            await bot_send(ctx, 'Ye')
        else:
            await bot_send(ctx, 'Nah')

    async def remind_stop(self, ctx: Context):
        print('Stopped reminder')
        self.stop = True


def setup(bot):
    bot.add_cog(Remind(bot))
