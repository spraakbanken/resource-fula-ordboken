import re
import unicodedata
from pathlib import Path
from typing import Dict, Generator, Iterable, Optional, Tuple

import json_arrays
import typer
from karp.lex_core import EntryDto
from tqdm import tqdm

# from sb_karp.utility import text
from resource_fula_ordboken import text

EM_PROG = re.compile(r"<em>([a-zA-ZåäöÅÄÖ0-9, \-]+)[\.,]?</em>")
JFR_PROG = re.compile(r"Jfr(.*)</p>")
ALSO_PROG = re.compile(r"(?:Ä|ä)ven <em>(.*?)</em>")


def shave_marks(txt: str) -> str:
    """Remove all diacritic marks."""
    norm_txt = unicodedata.normalize("NFD", txt)
    shaved = "".join(c for c in norm_txt if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", shaved)


class FulaOrdTxt2JsonConverter:
    def __init__(self) -> None:
        self.fulaord_ids = set()
        self.fulaord_wordforms = {}

    def generate_id(self, baseform: str) -> str:
        i = 1
        baseform = baseform.replace(" ", "_").replace(",", "_").lower()
        baseform = shave_marks(baseform)
        entry_id = f"{baseform}..{i}"
        while entry_id in self.fulaord_ids:
            i += 1
            entry_id = f"{baseform}..{i}"
        self.fulaord_ids.add(entry_id)
        return entry_id

    def convert_entry(self, fp) -> Generator[Dict, None, None]:
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
                wordforms = list(map(lambda s: s.strip(), _wordforms[1:]))
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
            yield entry

    def update_jfr(self, lex_iter: Iterable[Dict]) -> Generator[Dict, None, None]:
        for obj in lex_iter:
            if "jfr" in obj:
                new_jfrs = []
                for jfr in obj["jfr"]:
                    if jfr in self.fulaord_wordforms:
                        new_jfrs.append(self.fulaord_wordforms[jfr])
                    else:
                        new_jfrs.append(jfr)
                obj["jfr"] = new_jfrs
            yield obj


subapp = typer.Typer()


@subapp.command()
def convert(path: Path, output: Optional[Path] = typer.Option(None, help="file to write to")):
    typer.echo(f"reading '{path}' ...", err=True)
    if not output:
        output = Path(f"{path}.jsonl")
    typer.echo(f"writing output to '{output}' ...", err=True)
    converter = FulaOrdTxt2JsonConverter()
    with open(path) as fp:
        typer.echo("converting entries ...", err=True)
        fulaord = list(converter.convert_entry(fp))
        typer.echo(f"updating 'jfr' and writing to '{output}' ...", err=True)
        json_arrays.dump_to_file(converter.update_jfr(fulaord), output)
        # for length, entry in enumerate(convert_entry(fp), 1):
        #     pass
        # print(f"number of words: {length}")


def find_updates_old_format(path: Path, baseline: Path) -> Tuple[list, list, list[str]]:
    base = {
        obj["id"]: obj
        for obj in tqdm(
            json_arrays.load_from_file(baseline),
            desc="Loading baseline",
            unit=" entries",
        )
    }

    curr = {
        obj["id"]: obj
        for obj in tqdm(
            json_arrays.load_from_file(path), desc="Loading current", unit=" entries"
        )
    }

    removes = [
        key
        for key in tqdm(base, desc="Finding entries to remove", unit=" entries")
        if key not in curr
    ]

    updates = []
    adds = []
    # find updated entries
    for key, value in tqdm(
        curr.items(), desc="Finding entries to add or update", unit=" entries"
    ):
        if key in base:
            if value != base[key]:
                updates.append({"entry_id": key, "entry": value})
        else:
            adds.append(value)

    return adds, updates, removes


def find_updates_from_export(path: Path, baseline: Path) -> Tuple[list, list, list[str]]:
    base = {
        obj["entry"]["id"]: EntryDto(**obj)
        for obj in tqdm(
            json_arrays.load_from_file(baseline),
            desc="Loading baseline",
            unit=" entries",
        )
    }

    curr = {
        obj["id"]: obj
        for obj in tqdm(
            json_arrays.load_from_file(path), desc="Loading current", unit=" entries"
        )
    }

    removes = [
        key
        for key in tqdm(base, desc="Finding entries to remove", unit=" entries")
        if key not in curr
    ]

    updates = []
    adds = []
    # find updated entries
    for key, curr_entry in tqdm(
        curr.items(), desc="Finding entries to add or update", unit=" entries"
    ):
        if key in base:
            if curr_entry != base[key].entry:
                updates.append(
                    {
                        "entity_id": base[key].entity_id,
                        "version": base[key].version,
                        "entry": curr_entry,
                    }
                )
        else:
            adds.append(curr_entry)

    return adds, updates, removes


@subapp.command()
def find_updates(
    path: Path,
    baseline: Path = typer.Option(...),
    from_export: bool = typer.Option(
        True, help="The baseline is exported from karp and has entity_ids"
    ),
):
    typer.echo(f"Using '{baseline}' as baseline", err=True)

    if from_export:
        adds, updates, removes = find_updates_from_export(path, baseline)
    else:
        adds, updates, removes = find_updates_old_format(path, baseline)

    output = Path(f"{path}.adds.jsonl")
    typer.echo(f"Writing adds to {output} ...", err=True)
    json_arrays.dump_to_file(adds, output)

    output = Path(f"{path}.removes.jsonl")
    typer.echo(f"Writing removes to {output} ...", err=True)
    json_arrays.dump_to_file(removes, output)

    output = Path(f"{path}.updates.jsonl")
    typer.echo(f"Writing updates to {output} ...", err=True)
    json_arrays.dump_to_file(updates, output)


def init_app(app):
    app.add_typer(subapp, name="fulaord")


if __name__ == "__main__":
    subapp()
