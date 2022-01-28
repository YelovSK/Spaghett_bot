import json
import os
import pathlib
import random
import re
import shelve
import shutil
import sqlite3
import time
import datetime
from html.entities import name2codepoint
from io import StringIO
from typing import List, Dict, Tuple, Set
from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Context
from collections import Counter

with open("config.json") as cfg:
    config = json.load(cfg)


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


class Finder:

    def __init__(self):
        self.occurrences = 0
        self.exact_match = False

    def find_and_get_output(self, word: str, exact_match: bool) -> Tuple[str, int]:
        return self._find(word, exact_match), self.occurrences

    def find_and_get_occurrences(self, word: str, exact_match: bool) -> int:
        self._find(word, exact_match)
        return self.occurrences

    def _find(self, word: str, exact_match: bool) -> str:
        self.exact_match = exact_match
        self.occurrences = 0
        word = word.lower()
        with shelve.open(os.path.join(".shelve", "journal")) as jour:
            entries_map = jour["entries"]
        return "".join(
            self._find_word_in_file(entry, word)
            for entry in entries_map.items()
        )

    def _find_word_in_file(self, entry: Dict[str, str], word: str) -> str:
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
    def split_text_into_sentences(text: str) -> List[str]:
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

    def __init__(self) -> None:
        self.word_count_map = {}
        self.entries_map = {}
        self.init_dict()

    def init_dict(self) -> None:
        try:
            self.read_dict()
        except (KeyError, FileNotFoundError):
            self.write_dict()

    def read_dict(self) -> None:
        with shelve.open(os.path.join(".shelve", "journal")) as jour:
            self.word_count_map = jour["freq"]
            self.entries_map = jour["entries"]

    def write_dict(self) -> None:
        self.create_word_frequency()
        self.update_entries_from_db()
        pathlib.Path(os.path.join(".shelve")).mkdir(parents=True, exist_ok=True)
        with shelve.open(os.path.join(".shelve", "journal")) as jour:
            jour["freq"] = self.word_count_map
            jour["entries"] = self.entries_map

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
    def get_entries_from_db() -> List[str]:
        database_path = config["diary.db path"]
        con = sqlite3.connect(database_path)
        entries = con.cursor().execute("SELECT Text, DiaryEntryId FROM Entries").fetchall()
        con.close()
        return entries

    def get_years(self) -> Set[int]:
        return {int(date.split("-")[-1]) for date in self.entries_map.keys()}

    def create_tree_folder_structure(self) -> None:
        self.create_year_and_month_folders()
        self.create_day_files()

    def create_year_and_month_folders(self) -> None:
        for year in [str(y) for y in self.get_years()]:
            if os.path.exists(os.path.join("entries", year)):
                shutil.rmtree(os.path.join("entries", year))
            for month in [str(m) for m in range(1, 12 + 1)]:
                pathlib.Path(os.path.join("entries", year, month)).mkdir(parents=True, exist_ok=True)

    def create_day_files(self) -> None:
        for date, text in self.entries_map.items():
            day, month, year = date.split("-")
            day = day.lstrip("0")
            month = month.lstrip("0")
            with open(os.path.join("entries", year, month, day) + ".txt", "w", encoding="utf-8") as day_file:
                day_file.write(text)

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
        english_words = set()
        with open(os.path.join("folders", "text", "words_alpha.txt")) as f:
            for line in f:
                english_words.add(line.strip())
        return sum(count for word, count in self.word_count_map.items() if word in english_words)

    def get_entry_from_date(self, date: str) -> str:
        # date should be in the format DD.MM.YYYY
        try:
            return self.entries_map[date]
        except KeyError:
            return None

    def get_random_day(self) -> str:
        date, text = random.choice(list(self.entries_map.items()))
        return date + "\n" + text

    def get_longest_day(self) -> str:
        words_in_file = {}  # file: word_count
        for date, text in self.entries_map.items():
            words_in_file[date] = len(text.split())
        date, word_count = sorted(words_in_file.items(), key=lambda item: item[1])[-1]
        return f"{date}\nWord count: {word_count}\n\n{self.entries_map[date]}"

    def find_word(self, word: str, exact_match) -> str:
        start = time.time()
        output, occurrences = Finder().find_and_get_output(word, exact_match)
        took_time = round(time.time() - start, 2)
        res = StringIO()
        res.write(output)
        res.write(f"\nThe word {word} was found {occurrences} times")
        res.write(f"\nSearched through {self.get_total_word_count()} words in {took_time}s")
        return res.getvalue()

    @commands.command()
    async def journal_find(self, ctx: Context, word: str):
        """Returns sentences containing <word> and its derivatives.

        Syntax: ```plz journal_find <word>```
        """
        if str(ctx.author)[:str(ctx.author).find("#")] != "Yelov":
            await bot_send(ctx, "Ain't your journal bro")
            return

        await bot_send(ctx, self.find_word(word, exact_match=False))

    @commands.command()
    async def journal_find_exact(self, ctx: Context, word: str):
        """Returns sentences containing <word>.

        Syntax: ```plz journal_find_exact <word>```
        """
        if str(ctx.author)[:str(ctx.author).find("#")] != "Yelov":
            await bot_send(ctx, "Ain't your journal bro")
            return

        await bot_send(ctx, self.find_word(word, exact_match=True))

    @commands.command()
    async def journal_count(self, ctx: Context, word: str):
        """Returns the number of occurrences of <word> in the journal.

        Syntax: ```plz journal_count <word>```
        """
        await bot_send(ctx, f"The exact match of word '{word}' was found {self.get_word_occurrences(word)} times")
        occurrences = Finder().find_and_get_occurrences(word=word, exact_match=False)
        await bot_send(ctx, f"The number of all occurrences (incl. variations) is {occurrences}")

    @commands.command()
    async def journal_random(self, ctx: Context):
        """Returns a random entry from the journal.

        Syntax: ```plz journal_random```
        """
        if str(ctx.author)[:str(ctx.author).find("#")] != "Yelov":
            await bot_send(ctx, "Ain't your journal bro")
            return

        await bot_send(ctx, self.get_random_day())

    @commands.command()
    async def journal_longest(self, ctx: Context):
        """Returns the longest entry from the journal.

        Syntax: ```plz journal_longest```
        """
        if str(ctx.author)[:str(ctx.author).find("#")] != "Yelov":
            await bot_send(ctx, "Ain't your journal bro")
            return

        await bot_send(ctx, self.get_longest_day())

    @commands.command()
    async def journal_update(self, ctx: Context):
        """Updates the journal files.

        Syntax: ```plz journal_update```
        """
        entries_before = self.entries_map
        self.update_entries_from_db()
        entries_after = self.entries_map
        if entries_before != entries_after:
            await bot_send(ctx, f"Added {len(entries_after) - len(entries_before)} entries")
        word_count_before = self.get_total_word_count()
        self.write_dict()
        word_count_after = self.get_total_word_count()
        if word_count_after - word_count_before != 0:
            await bot_send(ctx, f"Added {word_count_after - word_count_before} words to the dictionary")


def setup(bot):
    bot.add_cog(Journal())
