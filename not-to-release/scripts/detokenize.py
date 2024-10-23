import sys
import os
import re


# source: https://github.com/stanfordnlp/stanza/blob/main/stanza/utils/datasets/common.py
def read_sentences_from_conllu(filename):
    """
    Reads a conllu file as a list of list of strings

    Finding a blank line separates the lists
    """
    sents = []
    cache = []
    with open(filename, encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if len(line) == 0:
                if len(cache) > 0:
                    sents.append(cache)
                    cache = []
                continue
            cache.append(line)
        if len(cache) > 0:
            sents.append(cache)
    return sents

def write_sentences_to_file(outfile, sents):
    for lines in sents:
        for line in lines:
            print(line, file=outfile)
        print("", file=outfile)

def write_sentences_to_conllu(filename, sents):
    with open(filename, 'w', encoding="utf-8") as outfile:
        write_sentences_to_file(outfile, sents)


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


def handle_line(line, text, pieces, start, idx, sent):
    t = text.find(pieces[1], start)
    if t == -1:
        print(f"{pieces[1]} NOT IN {text}")
        print(f"\t=> {line}")
    else:
        start = t+len(pieces[1])
    if idx < (len(sent)-1):
        try:
            if text[t+len(pieces[1])] != " ":
                if pieces[-1] == "_":
                    pieces[-1] = "SpaceAfter=No"
                else:
                    pieces[-1] += "|SpaceAfter=No"
        except IndexError as err:
            print(f"t={t}, start={start}, idx={idx}, pieces[1]={pieces[1]}, len(sent)={len(sent)}")
            print(f"len(text)={len(text)}, len(pieces[1])={len(pieces[1])}")
            print(f"text={text}")
            raise err
    return start


def process_file(conllu_file, out_file):
    mwl_pat = re.compile(r"^([0-9]+)-([0-9]+)\t")
    sents = read_sentences_from_conllu(conllu_file)
    i = 0
    for sent in sents:
        done_idx = []
        start = 0
        for idx, line in enumerate(sent):
            if line.startswith("# text = "):
                line = line.strip()
                text = line[9:]
                text = detokenize(text)
                sent[idx] = "# text = "+text
                i += 1
            elif line.startswith("#"):
                continue
            elif mwl_pat.match(line):
                pieces = line.split("\t")
                [idx_from, idx_to] = pieces[0].split("-")
                idx_from = int(idx_from)
                idx_to = int(idx_to)
                for x in range(idx_from, idx_to+1):
                    done_idx.append(x)
                start = handle_line(line, text, pieces, start, idx, sent)
                sent[idx] = "\t".join(pieces)
            else:
                pieces = line.split("\t")
                if int(pieces[0]) in done_idx:
                    continue
                else:
                    start = handle_line(line, text, pieces, start, idx, sent)
                    sent[idx] = "\t".join(pieces)

    write_sentences_to_conllu(out_file, sents)
    print(f"\t{i} Sätze.")


if __name__ == "__main__":
    conllu_dir = sys.argv[1]
    out_dir = sys.argv[2]
    files = os.listdir(conllu_dir)
    for file in files:
        if file.endswith(".conllu"):
            print(file+" -> "+out_dir+"/"+file)
            process_file(conllu_dir+"/"+file, out_dir+"/"+file)
