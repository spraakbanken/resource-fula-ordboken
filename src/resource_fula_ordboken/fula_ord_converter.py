"""Converter for Fula Ordboken."""

import re
import unicodedata
from collections.abc import Generator, Iterable

from resource_fula_ordboken import text
from resource_fula_ordboken.models import FulaOrd

EM_PROG = re.compile(r"<em>([a-zA-ZåäöÅÄÖ0-9, \-]+)[\.,]?</em>")
JFR_PROG = re.compile(r"Jfr(.*)</p>")
ALSO_PROG = re.compile(r"(?:Ä|ä)ven <em>(.*?)</em>")


def shave_marks(txt: str) -> str:
    """Remove all diacritic marks."""
    norm_txt = unicodedata.normalize("NFD", txt)
    shaved = "".join(c for c in norm_txt if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", shaved)


class FulaOrdTxt2JsonConverter:
    """Convert Fula Ordboken from txt to jsonl."""

    def __init__(self) -> None:
        """Construct the converter."""
        self.fulaord_ids: set[str] = set()
        self.fulaord_wordforms: dict[str, str] = {}

    def generate_id(self, baseform: str) -> str:
        """Generate id unique for this resource."""
        i = 1
        baseform = baseform.replace(" ", "_").replace(",", "_").lower()
        baseform = shave_marks(baseform)
        entry_id = f"{baseform}..{i}"
        while entry_id in self.fulaord_ids:
            i += 1
            entry_id = f"{baseform}..{i}"
        self.fulaord_ids.add(entry_id)
        return entry_id

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
                    _word_text = next(fp)
                except StopIteration:
                    break
                if _word_text.startswith("%word_word%"):
                    next_word = _word_text
                    break
                else:
                    word_text += _word_text
            _word_word = text.unescape_str(word_word.split("%word_word%")[-1])
            if "%word_text%" in _word_word:
                _tmp_words = _word_word.split("%word_text%")
                words = text.unescape_str(_tmp_words[0])
                _word_text = text.unescape_str(_tmp_words[-1])
                if word_text:
                    _word_text += word_text
            else:
                words = _word_word
                _word_text = text.unescape_str(word_text.split("%word_text%")[-1].strip())
            _wordforms = words.split(", ")
            entry = {"baseform": _wordforms[0].strip()}
            entry["id"] = self.generate_id(entry["baseform"])
            self.fulaord_wordforms[entry["baseform"]] = entry["id"]
            if len(_wordforms) > 1:
                wordforms = [s.strip() for s in _wordforms[1:]]
                for wordform in wordforms:
                    self.fulaord_wordforms[wordform] = entry["id"]
            else:
                wordforms = []
            if also_match := ALSO_PROG.findall(_word_text):
                for m in also_match:
                    wordforms.extend(m.split(", "))
            entry["wordforms"] = wordforms
            # entry["word"] = words.strip()
            entry["text"] = _word_text.strip()
            jfr_match = JFR_PROG.search(_word_text)
            jfr = None
            if jfr_match:
                jfr_text = jfr_match.group(0)
                jfr = EM_PROG.findall(jfr_text)
                entry["jfr"] = jfr
            yield FulaOrd(**entry)

    def update_jfr(self, lex_iter: Iterable[FulaOrd]) -> Generator[FulaOrd, None, None]:
        """Update jfr field."""
        for obj in lex_iter:
            if obj.jfr:
                new_jfrs = []
                for jfr in obj.jfr:
                    if jfr in self.fulaord_wordforms:
                        new_jfrs.append(self.fulaord_wordforms[jfr])
                    else:
                        new_jfrs.append(jfr)
                obj.jfr = new_jfrs
            yield obj
