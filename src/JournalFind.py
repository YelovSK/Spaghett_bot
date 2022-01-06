from collections import Counter
from os.path import join as pjoin
from pathlib import Path
import os
import random
import re
import shelve


class Journal:

    def __init__(self):
        self.base = pjoin("folders", "Journal format")
        self.path = pjoin(self.base, "Diarium")
        self.files = list(os.listdir(self.path))
        self.years = self.get_years()
        self.word_count_list = []
        self.word_count_dict = {}
        self.files_list_path = pjoin(self.base, "files.txt")
        self.check_file_count_mismatch()

    def check_file_count_mismatch(self):
        if not os.path.exists(self.files_list_path):
            open(self.files_list_path, "w").write("-1")
        files_num = int(open(self.files_list_path).read())
        # files_num -> last checked number of files
        # len(self.files) -> number of files in the Diarium folder
        if files_num != len(self.files):
            self.console.print("File count mismatch, formatting...")
            self.write_dict()
            self.update_file_count()
        else:
            self.init_dict()

    def init_dict(self):
        try:
            self.read_dict()
        except KeyError:
            self.write_dict()
        except FileNotFoundError:
            Path(pjoin(self.base, "shelve")).mkdir(parents=True, exist_ok=True)
            self.write_dict()

    def read_dict(self):
        with shelve.open(pjoin(self.base, "shelve", "journal")) as jour:
            self.word_count_list = jour["words"]
            self.word_count_dict = jour["freq"]

    def write_dict(self):
        self.create_word_frequency()
        with shelve.open(pjoin(self.base, "shelve", "journal")) as jour:
            jour["words"] = self.word_count_list
            jour["freq"] = self.word_count_dict
            
    def create_word_frequency(self):
        file_content_list = []
        for file in self.files:
            with open(pjoin(self.path, file), encoding="utf-8") as f:
                file_content_list.append(f.read())
        content = "".join(file_content_list).lower()
        self.word_count_dict = Counter(re.findall("\w+", content))
        self.word_count_list = sorted(self.word_count_dict.items(), key=lambda x: x[1], reverse=True)

    def get_years(self):
        YEAR_START_IX = 8
        YEAR_END_IX = YEAR_START_IX + 4
        return {int(file[YEAR_START_IX : YEAR_END_IX]) for file in self.files}

    def update_file_count(self):
        open(self.files_list_path, "w").write(str(len(self.files)))

    def get_most_frequent_words(self, count=20):
        return self.word_count_list[:count]

    def get_unique_word_count(self):
        return len(self.word_count_dict)

    def get_total_word_count(self):
        return sum(self.word_count_dict.values())

    def find_word_in_journal(self, word):
        self.occurences = 0
        self.output_list = []
        for file in self.files:
            self._find_word_in_file(file, word)

    def _find_word_in_file(self, file, word):
        file_content = open(pjoin(self.path, file), encoding="utf-8").read()
        date_inserted = False
        sentences = self._split_text_into_sentences(file_content)
        for sentence in sentences:
            if not re.search(word, sentence, re.IGNORECASE):
                continue
            if not date_inserted:
                self._insert_date(file)
                date_inserted = True
            self._find_word_in_sentence(sentence, word)
        if date_inserted:
            self.output_list.append("\n")

    def _split_text_into_sentences(self, text):
        split_regex = "(?<=[.!?\n])\s+"
        return [sentence.strip() for sentence in re.split(split_regex, text)]
            
    def _find_word_in_sentence(self, sentence, word):
        highlight_style = "**"
        for curr_word in sentence.split():
            if word.lower() in curr_word.lower():
                self.occurences += 1
                self.output_list.append(f"{highlight_style}{curr_word}{highlight_style}")
            else:
                self.output_list.append(curr_word)
        self.output_list[-1] += "\n"

    def _insert_date(self, file_name):
        file_date_begin = file_name.index("2")
        file_date_end = file_name.index(".txt")
        year, month, day = file_name[file_date_begin : file_date_end].split("-")
        date_style = "*"
        self.output_list.append(f"{date_style}Date: {day}.{month}.{year}{date_style}\n")

    def get_random_day(self):
        return open(pjoin(self.path, random.choice(self.files)), encoding="utf-8").read()
