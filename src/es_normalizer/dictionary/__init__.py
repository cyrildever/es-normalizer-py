from .address import ADDRESS
from .firstname import FIRST_NAME
from .title import TITLE


class Dictionary:
    """
    Translates words through a set of `word -> translation` pairs, an empty translation dropping the word; a key of several words translates them together, the longest first
    """

    def __init__(self, data_set: dict):
        self.set = data_set
        self.phrases = sorted((tuple(key.split(" ")) for key in data_set if " " in key), key=len, reverse=True)

    def translate_text(self, text: str) -> str:
        words = text.split(" ")
        translated = []
        i = 0
        while i < len(words):
            phrase = next((p for p in self.phrases if tuple(words[i : i + len(p)]) == p), None)
            if phrase is not None and self.set[" ".join(phrase)] is not None:
                translated.append(self.set[" ".join(phrase)])
                i += len(phrase)
                continue
            translated.append(self.translate_word(words[i]))
            i += 1
        return " ".join(word for word in translated if word != "")

    def translate_word(self, word: str) -> str:
        translation = self.set.get(word)
        return word if translation is None else translation


def get_set(data: str) -> dict:
    """
    Reads a dictionary written one `word<TAB>translation` pair per line; a line without a tab translates nothing
    """
    data_set = {}
    for line in data.split("\n"):
        # As JavaScript's `split('\t', 2)`: anything after a second tab is dropped
        parts = line.split("\t")[:2]
        data_set[parts[0]] = parts[1] if len(parts) > 1 else None
    return data_set


address_dictionary = Dictionary(get_set(ADDRESS))
first_name_dictionary = Dictionary(get_set(FIRST_NAME))
title_dictionary = Dictionary(get_set(TITLE))
