from bot_functions import *


@client.event
async def on_ready():
    print('Spaghett connected to the mainframe')
    activity_name = "slash '/' (cool, ain't it)"
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_name))

with open('ClientKey.txt') as f:
    client.run(keys['client'])