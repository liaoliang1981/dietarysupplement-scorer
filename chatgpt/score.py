EMBEDDED_DATA = {'_note': 'v0 INTERNATIONAL BASELINE reference values. These are hand-curated illustrative figures, NOT authoritative. RDA/UL and permitted claims vary by country (US/EU/CN/TH/JP/BR differ). Before any production or consumer-facing use, every value must be reviewed by a qualified professional and ideally sourced to a citable authority (e.g. NIH ODS, EFSA, national DRIs) per target market.', 'config': {'weights': {'formula': 0.45, 'quality': 0.25, 'safety': 0.3}, 'quality_base': 45, 'cert_points': {'gmp': 12, 'third_party_tested': 18, 'nsf': 16, 'usp': 16, 'informed_sport': 10, 'non_gmo': 4}, 'bioavailable_bonus_per': 4, 'bioavailable_bonus_max': 15, 'form_bonus': 8, 'form_penalty': 10, 'fairy_dust_points': 20, 'below_range_points': 55, 'in_range_points': 100, 'above_range_points': 80}, 'nutrients': {'iron': {'unit': 'mg', 'ul': 45, 'eff': [14, 65], 'good': ['bisglycinate', 'fumarate'], 'poor': ['sulfate'], 'pregnancy': 'caution_high_dose', 'source': 'NIH ODS (baseline, US)'}, 'folate': {'unit': 'mcg', 'ul': 1000, 'eff': [400, 800], 'good': ['l-5-mthf', 'l-methylfolate', '5-mthf'], 'poor': ['folic acid'], 'pregnancy': 'recommended', 'source': 'NIH ODS (baseline, US)'}, 'vitamin_d': {'unit': 'iu', 'ul': 4000, 'eff': [1000, 4000], 'good': ['d3', 'cholecalciferol'], 'poor': ['d2', 'ergocalciferol'], 'source': 'NIH ODS (baseline, US)'}, 'vitamin_b12': {'unit': 'mcg', 'ul': None, 'eff': [2.4, 1000], 'good': ['methylcobalamin', 'adenosylcobalamin'], 'poor': ['cyanocobalamin'], 'source': 'NIH ODS (baseline, US)'}, 'vitamin_b6': {'unit': 'mg', 'ul': 100, 'eff': [1.3, 50], 'good': ['p-5-p', 'pyridoxal-5-phosphate'], 'poor': ['pyridoxine hcl'], 'source': 'NIH ODS (baseline, US)'}, 'vitamin_c': {'unit': 'mg', 'ul': 2000, 'eff': [75, 500], 'good': [], 'poor': [], 'source': 'NIH ODS (baseline, US)'}, 'vitamin_e': {'unit': 'mg', 'ul': 1000, 'eff': [15, 268], 'good': ['d-alpha', 'mixed tocopherol'], 'poor': ['dl-alpha'], 'source': 'NIH ODS (baseline, US)'}, 'vitamin_a': {'unit': 'mcg', 'ul': 3000, 'eff': [700, 3000], 'good': [], 'poor': [], 'source': 'NIH ODS (baseline, US, preformed retinol)'}, 'vitamin_k': {'unit': 'mcg', 'ul': None, 'eff': [90, 180], 'good': ['mk-7', 'mk-4'], 'poor': [], 'source': 'baseline'}, 'calcium': {'unit': 'mg', 'ul': 2500, 'eff': [500, 1200], 'good': ['citrate', 'malate'], 'poor': ['carbonate'], 'source': 'NIH ODS (baseline, US)'}, 'magnesium': {'unit': 'mg', 'ul': 350, 'eff': [200, 400], 'good': ['glycinate', 'citrate', 'malate'], 'poor': ['oxide'], 'source': 'NIH ODS (baseline, US, supplemental UL)'}, 'zinc': {'unit': 'mg', 'ul': 40, 'eff': [8, 25], 'good': ['bisglycinate', 'picolinate'], 'poor': ['oxide'], 'source': 'NIH ODS (baseline, US)'}, 'iodine': {'unit': 'mcg', 'ul': 1100, 'eff': [150, 220], 'good': [], 'poor': [], 'source': 'NIH ODS (baseline, US)'}, 'choline': {'unit': 'mg', 'ul': 3500, 'eff': [300, 550], 'good': [], 'poor': [], 'source': 'NIH ODS (baseline, US)'}, 'omega3_epa_dha': {'unit': 'mg', 'ul': None, 'eff': [250, 2000], 'good': ['triglyceride', 'rtg'], 'poor': ['ethyl ester'], 'source': 'baseline'}, 'melatonin': {'unit': 'mg', 'ul': None, 'eff': [0.5, 5], 'good': [], 'poor': [], 'source': 'baseline (sleep onset)'}, 'creatine': {'unit': 'g', 'ul': None, 'eff': [3, 5], 'good': ['monohydrate'], 'poor': ['hcl', 'ethyl ester'], 'source': 'baseline (maintenance)'}, 'coq10': {'unit': 'mg', 'ul': None, 'eff': [100, 200], 'good': ['ubiquinol'], 'poor': [], 'source': 'baseline'}, 'ashwagandha': {'unit': 'mg', 'ul': None, 'eff': [300, 600], 'good': ['ksm-66', 'sensoril'], 'poor': [], 'source': 'baseline (standardized extract)'}, 'collagen': {'unit': 'g', 'ul': None, 'eff': [2.5, 15], 'good': [], 'poor': [], 'source': 'baseline'}}}

#!/usr/bin/env python3
"""Canonical deterministic supplement scoring engine — SINGLE SOURCE OF TRUTH.

The algorithm lives here; the data + weights live in engine/data.json. Do NOT
hand-edit data in other layers — edit engine/data.json (and this file for
algorithm changes), then run `python build.py` to propagate to all layers.

Data is loaded in priority order:
  1. an EMBEDDED_DATA global (set when built self-contained, e.g. for ChatGPT)
  2. a data.json / ingredients.json next to this file
  3. ../references/ingredients.json (when deployed inside the Claude skill)
"""

import argparse
import json
import sys
from pathlib import Path


def _load_data():
    g = globals().get("EMBEDDED_DATA")
    if g:
        return g
    here = Path(__file__).resolve().parent
    for cand in (here / "data.json", here / "ingredients.json",
                 here.parent / "references" / "ingredients.json",
                 here / "references" / "ingredients.json"):
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
    raise FileNotFoundError("reference data (data.json / ingredients.json) not found")


_DATA = _load_data()
CONFIG = _DATA["config"]
REFERENCE = _DATA["nutrients"]


def _clamp(v):
    return int(round(max(0, min(100, v))))


def score(product, pregnant=False):
    cfg, ref_tbl = CONFIG, REFERENCE
    ings = product.get("ingredients", []) or []
    w = cfg["weights"]

    recognised, earned, unknown = 0, 0.0, []
    f_detail, flags = [], []
    for ing in ings:
        ref = ref_tbl.get((ing.get("nutrient") or "").lower())
        if not ref:
            unknown.append(ing.get("name") or ing.get("nutrient") or "unknown")
            continue
        recognised += 1
        amt = float(ing.get("amount") or 0)
        form = (ing.get("form") or "").lower()
        lo, hi = ref["eff"]
        if amt < lo * 0.5:
            pts, verdict = cfg["fairy_dust_points"], "underdosed (fairy dusting)"
            flags.append(f"{ing.get('name', '')} underdosed at {amt}{ref['unit']}")
        elif amt < lo:
            pts, verdict = cfg["below_range_points"], "below efficacious range"
        elif amt <= hi:
            pts, verdict = cfg["in_range_points"], "within efficacious range"
        else:
            pts, verdict = cfg["above_range_points"], "above typical range"
        if ref.get("good") and any(g in form for g in ref["good"]):
            pts = min(100, pts + cfg["form_bonus"]); fnote = "bioavailable form"
        elif ref.get("poor") and any(p in form for p in ref["poor"]):
            pts = max(0, pts - cfg["form_penalty"]); fnote = "lower-absorption form"
        else:
            fnote = "form unspecified"
        earned += pts
        f_detail.append(f"{ing.get('name', '')} {amt}{ref['unit']}: {verdict}, {fnote}")
    formula = _clamp(earned / recognised) if recognised else 0

    q = cfg["quality_base"]; q_detail = []
    for cert in product.get("certifications", []) or []:
        pts = cfg["cert_points"].get(cert.lower().replace(" ", "_"), 0)
        if pts:
            q += pts; q_detail.append(f"+{pts} {cert}")
    bio = sum(1 for ing in ings
              if (r := ref_tbl.get((ing.get("nutrient") or "").lower()))
              and r.get("good") and any(g in (ing.get("form") or "").lower() for g in r["good"]))
    if bio:
        b = min(cfg["bioavailable_bonus_max"], bio * cfg["bioavailable_bonus_per"])
        q += b; q_detail.append(f"+{b} bioavailable forms")
    if not (product.get("certifications") or []):
        q_detail.append("no certifications listed — quality unverifiable")
    quality = _clamp(q)

    s = 100.0; s_detail = []
    for ing in ings:
        ref = ref_tbl.get((ing.get("nutrient") or "").lower())
        if not ref:
            continue
        amt = float(ing.get("amount") or 0)
        ul = ref.get("ul")
        if ul and amt > ul:
            pen = 25 if amt > ul * 1.5 else 15
            s -= pen
            flags.append(f"{ing.get('name')} {amt}{ref['unit']} exceeds UL ({ul}{ref['unit']})")
            s_detail.append(f"-{pen} {ing.get('name')} above tolerable upper limit")
        if pregnant and ref.get("pregnancy") == "caution_high_dose" and ul and amt > ul * 0.8:
            s -= 10
            flags.append(f"{ing.get('name')} dose may warrant caution in pregnancy")
    if not s_detail:
        s_detail.append("all actives within tolerable upper limits")
    safety = _clamp(s)

    overall = _clamp(w["formula"] * formula + w["quality"] * quality + w["safety"] * safety)
    total = recognised + len(unknown)
    return {
        "product": product.get("name", ""), "brand": product.get("brand", ""),
        "formula": formula, "quality": quality, "safety": safety, "overall": overall,
        "flags": flags, "unknown": unknown,
        "coverage": f"{recognised}/{total}" if total else "0/0",
        "rationale": {"formula": f_detail, "quality": q_detail, "safety": s_detail},
        "disclaimer": ("General wellness information, not medical advice. Scores use a v0 "
                       "international baseline; reference values and permitted claims vary by "
                       "country. Not intended to diagnose, treat, cure, or prevent any disease. "
                       "Consult a qualified professional."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--json")
    ap.add_argument("--pregnant", action="store_true")
    a = ap.parse_args()
    try:
        if a.json:
            product = json.loads(a.json)
        elif a.file:
            product = json.loads(Path(a.file).read_text(encoding="utf-8"))
        else:
            product = json.loads(sys.stdin.read())
    except Exception as e:
        print(json.dumps({"error": f"could not parse product JSON: {e}"})); sys.exit(1)
    print(json.dumps(score(product, pregnant=a.pregnant), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
