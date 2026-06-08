#!/usr/bin/env python3
"""Sync the three calling layers from the single source of truth in engine/.

Edit ONLY engine/score.py (algorithm) and engine/data.json (reference table +
weights). Then run `python build.py` to regenerate every layer. Never hand-edit
the generated files listed below — they are overwritten.

Generated:
  claude-skill/supplement-scorer/scripts/score.py        (copy of engine)
  claude-skill/supplement-scorer/references/ingredients.json  (copy of data)
  chatgpt/score.py                                        (self-contained: data embedded)
  web/index.html  (the CFG + REFERENCE block between GENERATED:DATA markers)
"""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "engine" / "data.json").read_text(encoding="utf-8"))
engine_src = (ROOT / "engine" / "score.py").read_text(encoding="utf-8")


def claude_skill():
    dst = ROOT / "claude-skill" / "supplement-scorer"
    (dst / "scripts").mkdir(parents=True, exist_ok=True)
    (dst / "references").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "engine" / "score.py", dst / "scripts" / "score.py")
    (dst / "references" / "ingredients.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  claude-skill: score.py + references/ingredients.json")


def chatgpt():
    embedded = "EMBEDDED_DATA = " + repr(data) + "\n\n"
    (ROOT / "chatgpt" / "score.py").write_text(embedded + engine_src, encoding="utf-8")
    print("  chatgpt: self-contained score.py (data embedded)")


def web():
    idx = ROOT / "web" / "index.html"
    html = idx.read_text(encoding="utf-8")
    block = ("/* === GENERATED:DATA START — do not edit, run build.py === */\n"
             "const CFG=" + json.dumps(data["config"], ensure_ascii=False) + ";\n"
             "const REFERENCE=" + json.dumps(data["nutrients"], ensure_ascii=False) + ";\n"
             "/* === GENERATED:DATA END === */")
    new, count = re.subn(
        r"/\* === GENERATED:DATA START.*?GENERATED:DATA END === \*/",
        lambda m: block, html, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("ERROR: GENERATED:DATA markers not found in web/index.html")
    idx.write_text(new, encoding="utf-8")
    print("  web: CFG + REFERENCE block regenerated in index.html")


if __name__ == "__main__":
    print("Building all layers from engine/ ...")
    claude_skill()
    chatgpt()
    web()
    print("Done. Source of truth: engine/data.json + engine/score.py")
