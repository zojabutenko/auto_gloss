import re

TEXT_FILE_NAME = "text.txt"
DICT_FILE_NAME = "dictionary.txt"
TRANSLATION_FILE_NAME = "translation.txt"


def check_glosses(tag):
    attrs = re.split(r'\W', tag)
    seps = re.findall(r'\W', tag)
    out = ''
    for a in range(len(attrs)):
        if attrs[a].upper() in gloss_names:
            out += attrs[a].upper()
        else:
            out += attrs[a]
        if attrs[a] != attrs[-1]:
            out += seps[a]
    return out


def format_word(word: str):
    for char in ",.;:()?!\n ":
        word = word.replace(char, "")
    return word


def format_gloss(gloss: str):
    for char in "()\n ":
        gloss = gloss.replace(char, "")
    correct_gloss = check_glosses(gloss)
    return correct_gloss


def get_gloss(word: str, dictionary: dict):
    # if word is a set of words returns a set of glosses
    if word.count("/") > 0:
        res = []
        for word in word.split("/"):
            res.append(get_gloss(word, dictionary))
        return "/".join(res)

    formatted_word = format_word(word)
    gloss = dictionary.get(formatted_word, "___")

    if word.startswith("("):
        gloss = f"({gloss}"
    if word.endswith(")"):
        gloss = f"{gloss})"
    return gloss


def get_formated_text_and_translation(words: list, glosses: list) -> (str, str):
    formatted_text = ""
    formatted_translation = "\t"
    for word, gloss in zip(words, glosses):
        word_tab_len = (len(word)) // 8
        gloss_tab_len = (len(gloss)) // 8
        needed_tab_len = max(word_tab_len, gloss_tab_len)
        formatted_text += word + "\t" * (1 + needed_tab_len - word_tab_len)
        formatted_translation += gloss + "\t" * (1 + needed_tab_len - gloss_tab_len)
    return formatted_text, formatted_translation


# Get translation of text
def translate_text(dictionary: dict, text: str):
    translation = []

    for line in text:
        words = line.split()
        glosses = []
        for word in words:
            glosses.append(get_gloss(word, dictionary))

        formated_line, formated_result = get_formated_text_and_translation(words, glosses)
        translation.extend([formated_line, formated_result])

    return translation


def split_and_format_line(line: str) -> list:
    line = line.replace(" ", "\t").replace("\\", "\t")
    line = re.sub("\t+", "\t", line)
    return line.split("\t")


# Get dictionary by text and translation of it
def create_dict_by_translation(text_and_trans: list):
    text = text_and_trans[0::2]
    translation = text_and_trans[1::2]
    dictionary = {}

    if len(text) != len(translation):
        raise (RuntimeError("Number of lines in text doesn't equal the number of lines in translation"))

    for orig, trans in zip(text, translation):
        words = split_and_format_line(orig)
        glosses = split_and_format_line(trans)

        words = map(format_word, words)
        words = filter(lambda x: x != "", words)
        words = list(words)

        glosses = map(format_gloss, glosses)
        glosses = list(glosses)

        if len(words) != len(glosses):
            print(f"WARNING!\nNumber of words doesn't equal the number of glosses at:\n{orig}\n{trans}")
            continue

        for word, gloss in zip(words, glosses):
            word = format_word(word)
            gloss = format_gloss(gloss)
            if dictionary.get(word) and dictionary.get(word) != gloss:
                print(
                    f"WARNING!\nRedefinition the gloss of word \"{word}\": "
                    f"{dictionary.get(word)}->{gloss} at\n{orig}\n{trans}")

            dictionary[word] = gloss

    return dictionary


def create_dict(dictionary_text: str) -> dict:
    dictionary = {}
    for line in dictionary_text:
        words = line.split("\t")
        dictionary[words[0]] = words[1][:-1]

    return dictionary


def save_dict(dictionary: dict, file_name: str):
    with open(file_name, "w") as out:
        for key in sorted(dictionary.keys()):
            out.write(f"{key}\t{dictionary[key]}\n")


with open('all_glosses.txt', 'r', encoding='utf-8') as file:
    gloss_names = file.read()
    gloss_names = gloss_names.split('\n')

with open(TEXT_FILE_NAME, "r", encoding="utf-8") as f:
    text = f.readlines()

with open(DICT_FILE_NAME, "r", encoding="utf-8") as f:
    dictionary_text = f.readlines()

with open(TRANSLATION_FILE_NAME, "r", encoding="utf-8") as f:
    translation = f.readlines()

dictionary = create_dict_by_translation(translation)
save_dict(dictionary, DICT_FILE_NAME)

translation = translate_text(dictionary, text)

with open("result.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(translation))
