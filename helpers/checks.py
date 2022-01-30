import json
from disnake.ext import commands


def is_owner():
    async def predicate(context: commands.Context) -> bool:
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id != data["owner"]:
            raise commands.MissingPermissions(["not owner lol"])
        return True

    return commands.check(predicate)


def is_trustworthy():
    async def predicate(context: commands.Context) -> bool:
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id not in (*data["trusted"], data["owner"]):
            raise commands.MissingPermissions(["idk, try asking for permission"])
        return True

    return commands.check(predicate)
