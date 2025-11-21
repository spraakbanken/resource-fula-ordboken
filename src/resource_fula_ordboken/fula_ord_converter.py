"""Converter for Fula Ordboken."""

import re
import unicodedata
from collections import defaultdict
from collections.abc import Generator, Iterable

from resource_fula_ordboken import text
from resource_fula_ordboken.models import FulaOrd

EM_PROG = re.compile(r"<em>([a-zA-ZåäöÅÄÖ0-9, \-]+)[\.,]?</em>")
JFR_PROG = re.compile(r"(?:Jfr|Jämför|Se även|Se också)(.*)</p>")
ALSO_PROG = re.compile(r"(?:Ä|ä)ven <em>(.*?)</em>")


# class _Entry(t.TypedDict):
#     baseform: str
#     id: str
#     wordforms: list[str]
#     text: str
#     jfr: list[str] | None


def shave_marks(txt: str) -> str:
    """Remove all diacritic marks."""
    norm_txt = unicodedata.normalize("NFD", txt)
    shaved = "".join(c for c in norm_txt if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", shaved)


WORDFORMS: dict[str, list[str]] = {
    "10-öres-brud": ["tioöresbrud"],
}


class FulaOrdTxt2JsonConverter:
    """Convert Fula Ordboken from txt to jsonl."""

    def __init__(self) -> None:
        """Construct the converter."""
        # self.fulaord_ids: set[str] = set()
        self.fulaord_wordforms: dict[str, set[str]] = defaultdict(set)

    def convert_entry(self, fp) -> Generator[FulaOrd, None, None]:  # noqa: ANN001
        """Generate converted entries from file."""
        next_word = None
        while True:
            try:
                if next_word:
                    word_word = next_word
                    next_word = None
                else:
                    word_word = next(fp)
            except StopIteration:
                break
            word_text = ""
            while True:
                try:
                    word_text_ = next(fp)
                except StopIteration:
                    break
                if word_text_.startswith("%word_word%"):
                    next_word = word_text_
                    break
                else:
                    word_text += word_text_
            word_word_ = text.unescape_str(word_word.split("%word_word%")[-1])
            if "%word_text%" in word_word_:
                tmp_words_ = word_word_.split("%word_text%")
                words = text.unescape_str(tmp_words_[0])
                word_text_ = text.unescape_str(tmp_words_[-1])
                if word_text:
                    word_text_ += word_text
            else:
                words = word_word_
                word_text_ = text.unescape_str(word_text.split("%word_text%")[-1].strip())
            wordforms_ = words.split(", ")
            # entry: _Entry = {"baseform": wordforms_[0].strip()}
            baseform = wordforms_[0].strip()
            # entry_id = self.generate_id(baseform)
            # entry["id"] = self.generate_id(entry["baseform"])
            # self.fulaord_wordforms[entry["baseform"]] = entry["id"]
            self.fulaord_wordforms[baseform].add(baseform)
            if len(wordforms_) > 1:
                wordforms = [s.strip() for s in wordforms_[1:]]
                for wordform in wordforms:
                    self.fulaord_wordforms[wordform].add(baseform)
            else:
                wordforms = []
            if also_match := ALSO_PROG.findall(word_text_):
                for m in also_match:
                    wordforms.extend(m.split(", "))
            if baseform in WORDFORMS:
                wordforms.extend(WORDFORMS[baseform])
            # entry["wordforms"] = wordforms
            # entry["word"] = words.strip()
            # entry["text"] = word_text_.strip()
            entry_text = word_text_.strip()
            jfr_match = JFR_PROG.search(word_text_)
            jfr = None
            if jfr_match:
                jfr_text = jfr_match.group(0)
                jfr = EM_PROG.findall(jfr_text)
                # entry["jfr"] = jfr
            yield FulaOrd(baseform=baseform, wordforms=wordforms, text=entry_text, jfr=jfr)

    def update_jfr(self, lex_iter: Iterable[FulaOrd]) -> Generator[FulaOrd, None, None]:
        """Update jfr field."""
        for obj in lex_iter:
            if obj.jfr:
                new_jfrs = set()
                for jfr in obj.jfr:
                    if jfr in self.fulaord_wordforms:
                        new_jfrs.update(self.fulaord_wordforms[jfr])
                    else:
                        new_jfrs.add(jfr)
                obj.jfr = list(new_jfrs)
            yield obj
