import sys
import os
import random
import re


def detokenize(text):
    text = text.replace(" !", "!")
    text = text.replace(" ?", "?")
    text = text.replace(" :", ":")
    text = text.replace(" ;", ";")
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace(" )", ")")
    text = text.replace("( ", "(")
    text = text.replace("[ ", "[")
    text = text.replace(" ]", "]")
    text = text.replace(" %", "%")

    i = 0
    a = 0
    neu = []
    do_not_store_next = False
    for c in text:
        do_not_store_this = True if do_not_store_next is True else False
        do_not_store_next = False
        if c == '"':
            a += 1
            if a % 2 == 0:
                if text[i-1] == " ":  # Zu
                    neu.pop()
            else:  # Auf
                if (i+1) < len(text) and text[i+1] == " ":
                    do_not_store_next = True
        if do_not_store_this is False:
            neu.append(c)
        i += 1

    # nichtgeschlossene Anführungsstriche am Ende korrigieren
    text = ''.join(neu)
    text = re.sub(r" (\"\s*)$", r"\1", text)

    return text


def insert_line_breaks(text):
    tokens = re.split(r"\s+", text)
    neu = []
    for token in tokens:
        neu.append(token)
        n = random.random()
        if n <= 0.01:
            neu.append("\n")
        else:
            neu.append(" ")
    neu.pop()  # letztes "\n" oder " " wieder entfernen

    # am Ende entweder "\n" oder " " anhängen
    is_ueberschrift = False
    if re.search(r"[\.\?!]$", neu[-1]) is None:
        is_ueberschrift = True
        neu.insert(0, "\n")  # Überschrift steht allein auf Zeile
    n = random.random()
    if n <= 0.1 or is_ueberschrift:
        neu.append("\n")
    else:
        neu.append(" ")
    return ''.join(neu)


def process_file(conllu_file, txt_file):
    with open(conllu_file, "rt", encoding="utf-8") as conllu, open(txt_file, "wt", encoding="utf-8") as txt:
        i = 0
        for line in conllu:
            line = line.strip()
            if line.startswith("# text = "):
                text = line[9:]
                text = detokenize(text)
                text = insert_line_breaks(text)
                txt.write(text)
                i += 1
    print("\t"+str(i)+" Sätze.")


if __name__ == "__main__":
    conllu_dir = sys.argv[1]
    files = os.listdir(conllu_dir)
    for file in files:
        if file.endswith(".conllu"):
            neu = file[:-6] + "txt"
            print(file+" -> "+neu)
            process_file(conllu_dir+"/"+file, conllu_dir+"/"+neu)