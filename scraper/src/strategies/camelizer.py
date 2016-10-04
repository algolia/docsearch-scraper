from .abstract_strategy import AbstractStrategy

class Camelizer:
    def __init__(self):
        pass

    @staticmethod
    def _uncamelize_word(word):
        s = ""
        for i in range(0, len(word)):
            if i > 0 and word[i].isupper() and \
                    not word[i - 1].isupper() and word[i - 1].isalnum() is True:
                s += u"\u2063"

            s += word[i]

        if s != word:
            s = s.strip()
            for tag in AbstractStrategy.keep_tags:
                s = s.replace("<" + tag + ">", "")
                s = s.replace("</" + tag + ">", "")

            parts = s.split(u"\u2063")

            while len(parts) > 1:
                from_s = ''.join(parts)
                to_s = " ".join(parts)

                Camelizer.synonyms.append({
                    'objectID': from_s,
                    'type': 'oneWaySynonym',
                    'input': from_s,
                    'synonyms': [to_s]
                })

                parts = parts[1:]

        return s

    @staticmethod
    def uncamelize_string(string):
        if string is None:
            return string

        return ' '.join([Camelizer._uncamelize_word(word) for word in string.split()])

    @staticmethod
    def uncamelize_hierarchy(hierarchy):
        uncamelized_hierarchy = hierarchy.copy()

        for level in uncamelized_hierarchy:
            uncamelized_hierarchy[level] = Camelizer.uncamelize_string(uncamelized_hierarchy[level])

        return uncamelized_hierarchy
