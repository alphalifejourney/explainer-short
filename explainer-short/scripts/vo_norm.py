"""Shared text normalisation for comparing a script line with a Whisper transcript.

Whisper writes digits, joins or splits compounds (stock count / stockcount), and hears
homophones (won / one). The comparison therefore normalises numbers to words, maps known
spellings, and scores on the text with spaces removed as well as word by word, taking the
better of the two. A "missing" word only counts when it is also absent from the spaceless
transcript.
"""
import difflib
import re

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
        "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def num2words(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        rest = n % 100
        return ONES[n // 100] + " hundred" + ("" if rest == 0 else " " + num2words(rest))
    return str(n)


ORDINALS = {"1st": "first", "2nd": "second", "3rd": "third", "4th": "fourth", "5th": "fifth", "12th": "twelfth"}
SPELLING = {
    "enquiry": "inquiry", "enquiries": "inquiries", "enquired": "inquired", "enquires": "inquires",
    "a-i": "ai",
    "won": "one", "judgement": "judgment", "everyone": "every one", "vip": "v i p", "vp": "v i p",
    "lapse": "lapsed", "restocked": "restock", "typed": "type", "%": "percent", "pov": "point of view", "followups": "follow ups",
}
STOP = set("a an the and or of to in on at for with by is are was be it its this that as we you your our us".split())


def norm(text):
    t = text.lower().replace("%", " percent ")
    t = re.sub(r"(?<!\d):(?!\d)", " ", t)  # drop colons except inside times like 9:47
    t = re.sub(r"(\d)(am|pm)\b", r"\1 \2", t)  # Whisper writes "10 PM" as 10pm
    t = t.replace("-", " ").replace("/", " ").replace(":", " ")
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    out = []
    for w in t.split():
        w = ORDINALS.get(w, w)
        if w.isdigit() and len(w) <= 3:
            w = num2words(int(w))
        elif w.isdigit() and len(w) == 4 and int(w[:2]) < 24 and int(w[2:]) < 60:
            w = num2words(int(w[:2])) + " " + num2words(int(w[2:]))  # Whisper writes "ten forty seven" as 1047
        w = SPELLING.get(w, w)
        out.extend(w.split())
    return out


def compare(script, heard):
    """Return (ratio, missing_content_words)."""
    a, b = norm(script), norm(heard)
    word_ratio = difflib.SequenceMatcher(None, a, b).ratio()
    sa, sb = "".join(a), "".join(b)
    char_ratio = difflib.SequenceMatcher(None, sa, sb).ratio()
    sm = difflib.SequenceMatcher(None, a, b)
    missing = []
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ("delete", "replace"):
            # a word counts as missing only if neither it nor its stem was heard
            # (Whisper hears "book"/"booked", "reception is"/"receptionist", "brace"/"braces")
            missing += [w for w in a[i1:i2] if w not in STOP and w not in sb and w[:max(4, len(w) - 3)] not in sb]
    return max(word_ratio, char_ratio), missing


def acceptable(ratio, missing):
    return ratio >= 0.90 and len(missing) < 2
