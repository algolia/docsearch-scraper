from .abstract_strategy import AbstractStrategy
from six import string_types
from copy import deepcopy

class Camelizer:
    def __init__(self):
        pass

    @staticmethod
    def _uncamelize_word(word):
        s = ""
        for i in range(0, len(word)):
            if i > 1 and word[i].isupper() and \
                    not word[i - 1].isupper() and word[i - 1].isalnum() is True:
                s += u"\u2063"

            s += word[i]

        if s != word:
            s = s.strip()
            for tag in AbstractStrategy.keep_tags:
                s = s.replace("<" + tag + ">", "<" + tag + "> ")
                s = s.replace("</" + tag + ">", " </" + tag + ">")

            parts = s.split(u"\u2063")

            while len(parts) > 1:
                from_s = ''.join(parts)
                to_s = " ".join(parts)

                Camelizer.synonyms[from_s] = {
                    'objectID': from_s,
                    'type': 'oneWaySynonym',
                    'input': from_s,
                    'synonyms': [to_s]
                }

                parts = parts[1:]

        return s

    @staticmethod
    def uncamelize_string(string, strip_chars):
        if string is None:
            return string

        clean_string = string

        if '.' not in strip_chars:
            clean_string = string.replace('.', ' ')

        return ' '.join([Camelizer._uncamelize_word(word) for word in clean_string.split()])

    @staticmethod
    def uncamelize_hierarchy(hierarchy, strip_chars):
        uncamelized_hierarchy = deepcopy(hierarchy)

        for level in uncamelized_hierarchy:
            if uncamelized_hierarchy[level] is not None:
                if isinstance(uncamelized_hierarchy[level], string_types):
                    uncamelized_hierarchy[level] = Camelizer.uncamelize_string(uncamelized_hierarchy[level], strip_chars)
                else:
                    for key in uncamelized_hierarchy[level]:
                        uncamelized_hierarchy[level][key] = Camelizer.uncamelize_string(uncamelized_hierarchy[level][key], strip_chars)

        return uncamelized_hierarchy
