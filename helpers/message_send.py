from __future__ import annotations

import re

import disnake
from disnake.ext.commands import Context

max_message_length = 1950


async def bot_send(ctx: Context, mssg: str | disnake.File) -> None:
    """
    Splits messages if they are longer than the character limit.
    """
    if isinstance(mssg, disnake.File):
        await ctx.send(file=mssg)
    elif len(mssg) > max_message_length:
        for m in split_long(mssg):
            await bot_send(ctx, m)
    else:
        await ctx.send(mssg)


def split_long(text: str) -> list[str]:
    messages = []

    while text != "":
        curr_mssg = text[:max_message_length]
        text = text[max_message_length:]
        formatting_char = find_formatting_characters(curr_mssg)
        if formatting_char is not None:
            curr_mssg += formatting_char
            text = formatting_char + text
        messages.append(curr_mssg)

    return messages


def find_formatting_characters(text: str) -> str | None:
    """
    If a message gets split without getting the ending part of markdown,
    the next message will not continue with the proper formatting.
    That's why I find if there's a markdown missing (not even count)
    and return it, so that I can add it to the end of the current message
    and to the beginning of the next message.
    """
    markdown_expressions = [  # ordered from most common to least common for performance
        r"\b[*]\b",  # * -> italics
        r"\b[*]{2}\b",  # ** -> bold
        r"\b[_]\b",  # _ -> italics
        r"\b[`]\b",  # ` -> one line code
        r"\b[`]{3}\b",  # ``` -> multiline code
        r"\b[*]{3}\b",  # *** -> bold italics
        r"\b[__]{2}\b",  # __ -> underline
    ]
    for expression in markdown_expressions:
        matches = re.findall(expression, text)
        if len(matches) % 2 != 0:
            return matches[0]

    return None
