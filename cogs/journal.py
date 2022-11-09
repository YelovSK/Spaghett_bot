from __future__ import annotations

import json
import os
import random
import sqlite3
import time
from collections import Counter
from io import StringIO

from disnake.ext import commands
from disnake.ext.commands import Context

from helpers import checks
from helpers.helper_methods import *
from helpers.message_send import bot_send

with open("config.json") as cfg:
    config = json.load(cfg)


class Finder:

    def __init__(self, entries: dict[str, str]):
        self.entries = entries
        self.occurrences = 0
        self.exact_match = False

    def find_and_get_output(self, word: str, exact_match: bool) -> tuple[str, int]:
        return self._find(word, exact_match), self.occurrences

    def find_and_get_occurrences(self, word: str, exact_match: bool) -> int:
        self._find(word, exact_match)
        return self.occurrences

    def _find(self, word: str, exact_match: bool) -> str:
        self.exact_match = exact_match
        self.occurrences = 0
        word = word.lower()
        return "".join(
            self._find_word_in_file(entry, word)
            for entry in self.entries.items()
        )

    def _find_word_in_file(self, entry: tuple[str, str], word: str) -> str:
        file_output = StringIO()
        date, text = entry

        sentences = self.split_text_into_sentences(text)
        sentences_containing_word = [s for s in sentences if self._is_word_in_sentence(s, word)]
        if not sentences_containing_word:
            return file_output.getvalue()

        file_output.write(date + "\n")
        for sentence in sentences_containing_word:
            file_output.write(self._find_word_in_sentence(sentence, word) + "\n")
        file_output.write("\n")

        return file_output.getvalue()

    @staticmethod
    def split_text_into_sentences(text: str) -> list[str]:
        split_regex = r"(?<=[.!?\n])\s+"
        return [sentence.strip() for sentence in re.split(split_regex, text)]

    def _find_word_in_sentence(self, sentence: str, word: str) -> str:
        sentence_output = StringIO()
        highlight_style = "**"

        for curr_word in sentence.split():
            if self._is_the_same_word(curr_word, word):
                self.occurrences += 1
                sentence_output.write(f"{highlight_style}{curr_word}{highlight_style} ")
            else:
                sentence_output.write(f"{curr_word} ")

        return sentence_output.getvalue()

    def _is_word_in_sentence(self, sentence: str, word: str) -> bool:
        return any(
            self._is_the_same_word(curr_word, word)
            for curr_word in sentence.split()
        )

    def _is_the_same_word(self, word1: str, word2: str) -> bool:
        if self.exact_match:
            return word1.lower() == word2.lower()
        if len(word2) > len(word1):  # word1 longer or same
            word1, word2 = word2, word1
        if len(word1) - len(word2) >= len(word2):
            return False

        word1 = word1.lower()
        word2 = word2.lower()

        return word2 in word1


class Journal(commands.Cog):
    """you can't use it anyway"""

    COG_EMOJI = "📕"

    def __init__(self) -> None:
        self.word_count_map = {}
        self.entries_map = {}
        self.loaded = False  # don't initialize when bot starts cuz it might take a bit

    def load_entries(self) -> None:
        self.update_entries_from_db()
        self.create_word_frequency()
        self.loaded = True

    def create_word_frequency(self) -> None:
        content = "".join(self.entries_map.values()).lower()
        self.word_count_map = Counter(re.findall(r"\w+", content))

    def update_entries_from_db(self) -> None:
        self.entries_map = {}
        entries = self.get_entries_from_db()
        for text_raw, ticks in entries:
            text = decode_entities(text_raw).replace("<p>", "").replace("</p>", "\n")
            date = get_date_from_tick(int(ticks))
            self.entries_map[date] = text

    @staticmethod
    def get_entries_from_db() -> list[str]:
        database_path = config["misc"]["diary.db path"]
        con = sqlite3.connect(database_path)
        entries = con.cursor().execute("SELECT Text, DiaryEntryId FROM Entries").fetchall()
        con.close()
        return entries

    def get_most_frequent_words(self, count: int) -> list:
        return sorted(self.word_count_map.items(), key=lambda item: item[1], reverse=True)[:count]

    def get_unique_word_count(self) -> int:
        return len(self.word_count_map)

    def get_total_word_count(self) -> int:
        return sum(self.word_count_map.values())

    def get_word_occurrences(self, word: str) -> int:
        return self.word_count_map[word] if word in self.word_count_map else 0

    def get_english_word_count(self) -> int:
        # not accurate cuz a word can be both Slovak and English and I don't have a database of Slovak words to compare
        with open(os.path.join("folders", "text", "words_alpha.txt")) as f:
            english_words = set(f.read().splitlines())

        return sum(count for word, count in self.word_count_map.items() if word in english_words)

    def get_entry_from_date(self, date: str) -> str | None:
        try:
            return self.entries_map[date]
        except KeyError:
            return None

    def get_random_day(self) -> str:
        date, text = random.choice(list(self.entries_map.items()))
        return date + "\n" + text

    def get_longest_day(self) -> str:
        date, text = sorted(self.entries_map.items(), key=lambda x: len(x[1].split()))[-1]
        return date + "\n" + text + "\n" + f"Word count: {len(text.split())}"

    def find_word(self, word: str, exact_match) -> str:
        start = time.time()
        output, occurrences = Finder(self.entries_map).find_and_get_output(word, exact_match)
        took_time = round(time.time() - start, 2)

        res = StringIO()
        res.write(output)
        res.write(f"\nThe word {word} was found {occurrences} times")
        res.write(f"\nSearched through {self.get_total_word_count()} words in {took_time}s")

        return res.getvalue()

    @commands.command()
    @checks.is_owner()
    async def journal_find(self, ctx: Context, word: str):
        """Returns sentences containing <word> and its derivatives.

        Syntax: ```plz journal_find <word>```
        """
        if not self.loaded:
            self.load_entries()

        await bot_send(ctx, self.find_word(word, exact_match=False))

    @commands.command()
    @checks.is_owner()
    async def journal_find_exact(self, ctx: Context, word: str):
        """Returns sentences containing <word>.

        Syntax: ```plz journal_find_exact <word>```
        """
        if not self.loaded:
            self.load_entries()

        await bot_send(ctx, self.find_word(word, exact_match=True))

    @commands.command()
    async def journal_count(self, ctx: Context, word: str):
        """Returns the number of occurrences of <word> in the journal.

        Syntax: ```plz journal_count <word>```
        """
        if not self.loaded:
            self.load_entries()

        await bot_send(ctx, f"The exact match of word '{word}' was found {self.get_word_occurrences(word)} times")
        occurrences = Finder(self.entries_map).find_and_get_occurrences(word=word, exact_match=False)
        await bot_send(ctx, f"The number of all occurrences (incl. variations) is {occurrences}")

    @commands.command()
    @checks.is_owner()
    async def journal_random(self, ctx: Context):
        """Returns a random entry from the journal.

        Syntax: ```plz journal_random```
        """
        if not self.loaded:
            self.load_entries()

        await bot_send(ctx, self.get_random_day())

    @commands.command()
    @checks.is_owner()
    async def journal_longest(self, ctx: Context):
        """Returns the longest entry from the journal.

        Syntax: ```plz journal_longest```
        """
        if not self.loaded:
            self.load_entries()

        await bot_send(ctx, self.get_longest_day())

    @commands.command()
    async def journal_stats(self, ctx: Context):
        """Shows stats for the journal.

        Syntax: ```plz journal_stats```
        """
        if not self.loaded:
            self.load_entries()

        result = StringIO()
        result.write(f"Entries: {len(self.entries_map)}\n")
        result.write(f"Words: {self.get_total_word_count()}\n")
        result.write(f"Unique words: {self.get_unique_word_count()}\n")
        result.write(str(self.get_most_frequent_words(10)))

        await bot_send(ctx, result.getvalue())


def setup(bot):
    bot.add_cog(Journal())
