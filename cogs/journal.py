import json
import os
import pathlib
import random
import re
import shelve
import shutil
import time

from io import StringIO
from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Context
from collections import Counter

with open("config.json") as file:
    config = json.load(file)


class Finder:

    def __init__(self, files: list[str]):
        self.files = files
        self.occurrences = 0
        self.find_output = StringIO()
        self.exact_match = False

    def find(self, word: str, exact_match: bool):
        self.exact_match = exact_match
        self.find_output = StringIO()
        self.files_output = {}
        self.occurrences = 0
        word = word.lower()
        for file in self.files:
            self._find_word_in_file(file, word)

    def _find_word_in_file(self, file: str, word: str):
        with open(file, encoding="utf-8") as f:
            file_content = f.read()
        date_inserted = False
        sentences = self._split_text_into_sentences(file_content)
        for sentence in sentences:
            if not self.is_word_in_sentence(sentence, word):
                continue
            if not date_inserted:
                self._insert_date(file)
                date_inserted = True
            self._find_word_in_sentence(sentence, word)
        if date_inserted:
            self.find_output.write("\n")

    def _split_text_into_sentences(self, text: str):
        split_regex = r"(?<=[.!?\n])\s+"
        return [sentence.strip() for sentence in re.split(split_regex, text)]

    def _find_word_in_sentence(self, sentence: str, word: str):
        highlight_style = "**"
        for curr_word in sentence.split():
            if self.is_the_same_word(curr_word, word):
                self.occurrences += 1
                self.find_output.write(f"{highlight_style}{curr_word}{highlight_style} ")
            else:
                self.find_output.write(f"{curr_word} ")
        self.find_output.write("\n")

    def is_word_in_sentence(self, sentence: str, word: str):
        return any(
            self.is_the_same_word(curr_word, word)
            for curr_word in sentence.split()
        )

    def is_the_same_word(self, word1: str, word2: str):
        if self.exact_match:
            return word1.lower() == word2.lower()
        if len(word2) > len(word1):  # word1 longer or same
            word1, word2 = word2, word1
        if len(word1) - len(word2) >= len(word2):
            return False
        word1 = word1.lower()
        word2 = word2.lower()
        return word2 in word1

    def _insert_date(self, file_name: str):
        file_date_begin = file_name.index("2")
        file_date_end = file_name.index(".txt")
        year, month, day = file_name[file_date_begin: file_date_end].split("-")
        date_style = "*"
        self.find_output.write(f"{date_style}Date: {day}.{month}.{year}{date_style}\n")

    def get_current_output(self):
        return self.find_output.getvalue()


class Journal(commands.Cog):

    def __init__(self, bot, base_folder: str = os.getcwd()):
        self.bot = bot
        base_folder = r"folders/Journal format"
        self.base = base_folder
        self.path = os.path.join(self.base, "Diarium")
        self.files = list(os.listdir(self.path))
        self.years = self.get_years()
        self.word_count_dict = {}
        self.files_list_path = os.path.join(self.base, "files.txt")
        self.check_file_count_mismatch()

    def check_file_count_mismatch(self):
        if not os.path.exists(self.files_list_path):
            with open(self.files_list_path, "w") as f:
                f.write("-1")
        with open(self.files_list_path) as f:
            files_num = int(f.read())
        # files_num -> last checked number of files
        # len(self.files) -> number of files in the Diarium folder
        if files_num != len(self.files):
            self.write_dict()
            self.update_file_count()
        else:
            self.init_dict()

    def init_dict(self):
        try:
            self.read_dict()
        except (KeyError, FileNotFoundError):
            self.write_dict()

    def read_dict(self):
        with shelve.open(os.path.join(self.base, "shelve", "journal")) as jour:
            self.word_count_dict = jour["freq"]

    def write_dict(self):
        self.create_word_frequency()
        pathlib.Path(os.path.join(self.base, "shelve")).mkdir(parents=True, exist_ok=True)
        with shelve.open(os.path.join(self.base, "shelve", "journal")) as jour:
            jour["freq"] = self.word_count_dict

    def create_word_frequency(self):
        file_content_list = []
        for file in self.files:
            with open(os.path.join(self.path, file), encoding="utf-8") as f:
                file_content_list.append(f.read())
        content = "".join(file_content_list).lower()
        self.word_count_dict = Counter(re.findall("\w+", content))

    def get_years(self):
        YEAR_START_IX = 8
        YEAR_END_IX = YEAR_START_IX + 4
        return {int(file[YEAR_START_IX: YEAR_END_IX]) for file in self.files}

    def create_tree_folder_structure(self):
        self.create_year_and_month_folders()
        self.create_day_files()
        self.update_file_count()

    def create_year_and_month_folders(self):
        for year in [str(y) for y in self.years]:
            if os.path.exists(os.path.join(self.base, year)):
                shutil.rmtree(os.path.join(self.base, year))
            for month in [str(m) for m in range(1, 12 + 1)]:
                pathlib.Path(os.path.join(year, month)).mkdir(parents=True, exist_ok=True)

    def create_day_files(self):
        for file in self.files:
            with open(os.path.join(self.path, file), errors="ignore") as f:
                file_content = f.read()
            year, month, day = file[file.index("2"):].split("-")
            if month[0] == "0":
                month = month[1:]
            if day[0] == "0":
                day = day[1:]
            with open(os.path.join(year, month, day), "w") as day_file:
                day_file.write(file_content)

    def update_file_count(self):
        with open(self.files_list_path, "w") as f:
            f.write(str(len(self.files)))

    def get_most_frequent_words(self, count):
        return sorted(self.word_count_dict.items(), key=lambda item: item[1], reverse=True)[:count]

    def get_unique_word_count(self):
        return len(self.word_count_dict)

    def get_total_word_count(self):
        return sum(self.word_count_dict.values())

    def find(self, word: str, exact_match: bool):
        files_full_path = [os.path.join(self.path, file) for file in self.files]
        self.finder = Finder(files_full_path)
        start = time.time()
        self.finder.find(word, exact_match)
        took_time = round(time.time() - start, 3)
        return self.finder.get_current_output() + f"\nSearched through {self.get_total_word_count()} words in {took_time}s"

    def get_random_day(self):
        with open(os.path.join(self.path, random.choice(self.files)), encoding="utf-8") as f:
            return f.read()

    @commands.command()
    async def journal(self, ctx: Context, *, action=None):
        """Searches through journal.
        -f {word} -> finds {word}
        -c {word} -> number of {word} occurences
        -r -> random day

        Syntax: ```plz journal <action> [word]```
        Example: ```plz journal -f kokot``` ```plz journal -c kokot``` ```plz journal -r```
        """
        if str(ctx.author)[:str(ctx.author).find("#")] != 'Yelov':
            await bot_send(ctx, "Ain't your journal bro")
            return

        if action is None:
            help_l = [
                '-f {word} -> finds {word}',
                '-fp {word} -> finds {word} (only exact matches)',
                '-c {word} -> number of {word} occurences',
                '-r -> random day',
            ]
            await bot_send(ctx, "\n".join(help_l))
            return

        if action[:2] not in ("-f", "-fp", "-c", "-r"):
            await bot_send(ctx, "Incorrect syntax")
            return

        do = action.split()[0]
        inp = " ".join(action.split()[1:]) if action != "-r" else ""
        journal_text = "if you are reading this then something bugged out"
        if do == "-f":
            journal_text = self.find(inp, exact_match=False)
        elif do == "-fp":
            journal_text = self.find(inp, exact_match=True)
        elif do == "-c":
            self.find(inp, exact_match=False)
            journal_text = f"The word **{inp}** was found {self.finder.occurrences} times"
            journal_text += f"\nNumber of exact matches is {self.word_count_dict[inp]}"
        elif do == "-r":
            journal_text = "**RANDOM ENTRY:**\n\n" + self.get_random_day()

        await bot_send(ctx, journal_text)


def setup(bot):
    bot.add_cog(Journal(bot))
