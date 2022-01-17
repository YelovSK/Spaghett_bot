import asyncio

from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Context


class Remind(commands.Cog):
    """nice memory pleb"""
    
    COG_EMOJI = "⌚"

    def __init__(self, bot):
        self.bot = bot
        self.stop = False
        self.reminder_active = False

    async def remind(self, ctx: Context, *, string):
        split = string.split()
        send = ''
        repeat = split[-1] == '/repeat/'
        if split[1] in ('hours', 'hour'):
            when = float(split[0])
            minute = False
        elif split[1] in ('minute', 'minutes'):
            when = int(split[0])
            minute = True
        for x in split[2:]:
            if repeat and x == split[-1]:
                break
            send += f'{x} '
        if minute:
            await bot_send(ctx, f'Reminding in {when} minutes')
            mul = 60
        else:
            if when % 1 == 0:
                await bot_send(ctx, f'Reminding in {round(when)} hours')
            else:
                await bot_send(ctx, f'Reminding in {round(when // 1)}h{round((when % 1) * 60)}m')
            mul = 3600
        self.reminder_active = True
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
            self.reminder_active = False

    async def remind_active(self, ctx: Context):
        if self.reminder_active:
            await bot_send(ctx, 'Ye')
        else:
            await bot_send(ctx, 'Nah')

    async def remind_stop(self, ctx: Context):
        print('Stopped reminder')
        self.stop = True


def setup(bot):
    bot.add_cog(Remind(bot))
