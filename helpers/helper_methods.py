from __future__ import annotations

import datetime
import re
from html.entities import name2codepoint


def decode_entities(text: str) -> str:
    def unescape(match):
        code = match.group(1)
        if code:
            return chr(int(code, 10))
        code = match.group(2)
        if code:
            return chr(int(code, 16))
        code = match.group(3)
        if code in name2codepoint:
            return chr(name2codepoint[code])
        return match.group(0)

    entity_pattern = re.compile(r"&(?:#(\d+)|#x([\da-fA-F]+)|([a-zA-Z]+));")
    return entity_pattern.sub(unescape, text)


def get_date_from_tick(ticks: int) -> str:
    date = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=ticks // 10)
    return date.strftime(r"%d.%m.%Y")
