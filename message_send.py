from os.path import join as pjoin
from disnake.ext.commands import Context
import disnake

def split_long(text, max_len=2000):    # todo formatting breaks if split at **word
    mssgs = []
    for _ in range((len(text) // max_len) + 1):
        mssgs.append(text[:max_len])
        text = text[max_len:]
    if text:
        mssgs.append(text)
    return mssgs

async def bot_send(ctx: Context, mssg):
    if type(mssg) == disnake.File:
        sent_mssg = await ctx.send(file = mssg)
    elif len(mssg) > 2000:
        for m in split_long(mssg):
            await bot_send(ctx, m)
        return
    else:
        sent_mssg = await ctx.send(mssg)
    mssg_id, channel_id = sent_mssg.id, sent_mssg.channel.id
    curr_mssgs = open(pjoin("folders", "text", "prev_mssg_ids.txt")).read().splitlines()
    if len(curr_mssgs) > 25:
        curr_mssgs = curr_mssgs[-25:]
    curr_mssgs.append(f"{channel_id} {mssg_id}")
    open(pjoin("folders", "text", "prev_mssg_ids.txt"), "w").write("\n".join(curr_mssgs))
