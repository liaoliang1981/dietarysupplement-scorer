#!/usr/bin/env python3
"""Assertion battery for the canonical engine. Run: python engine/test_engine.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import score


def P(**kw):
    return kw


CASES = [
    ("quality single-product", P(name="Iron", certifications=["GMP", "third_party_tested"],
        ingredients=[{"name": "Iron", "nutrient": "iron", "form": "ferrous bisglycinate", "amount": 18, "unit": "mg"},
                     {"name": "Folate", "nutrient": "folate", "form": "L-5-MTHF", "amount": 400, "unit": "mcg"}]),
     lambda r: r["overall"] >= 90 and not r["flags"]),
    ("weak/cheap product", P(name="Cheap", certifications=[],
        ingredients=[{"name": "Iron", "nutrient": "iron", "form": "ferrous sulfate", "amount": 8, "unit": "mg"},
                     {"name": "D2", "nutrient": "vitamin_d", "form": "ergocalciferol", "amount": 400, "unit": "iu"}]),
     lambda r: r["overall"] < 65 and any("underdosed" in f for f in r["flags"])),
    ("over-UL safety", P(name="Mega",
        ingredients=[{"name": "VitA", "nutrient": "vitamin_a", "amount": 5000, "unit": "mcg"},
                     {"name": "Zinc", "nutrient": "zinc", "amount": 60, "unit": "mg"}]),
     lambda r: r["safety"] <= 70 and len([f for f in r["flags"] if "UL" in f]) >= 2),
    ("unknown ingredient surfaced", P(name="Adapt", certifications=["GMP"],
        ingredients=[{"name": "Ashwagandha", "nutrient": "ashwagandha", "form": "KSM-66", "amount": 600, "unit": "mg"},
                     {"name": "Rhodiola", "nutrient": "rhodiola", "amount": 200, "unit": "mg"}]),
     lambda r: r["coverage"] == "1/2" and "Rhodiola" in r["unknown"]),
    ("all unknown, no crash", P(name="Herbal",
        ingredients=[{"name": "Turmeric", "nutrient": "turmeric", "amount": 500},
                     {"name": "Rhodiola", "nutrient": "rhodiola", "amount": 200}]),
     lambda r: r["formula"] == 0 and r["coverage"] == "0/2"),
    ("empty", P(name="Empty", ingredients=[]),
     lambda r: r["formula"] == 0 and r["coverage"] == "0/0"),
]


def run():
    passed = 0
    for name, prod, chk in CASES:
        r = score(prod)
        ok = chk(r)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {name:<26} overall={r['overall']} cov={r['coverage']}")
    base = score(P(ingredients=[{"name": "Iron", "nutrient": "iron", "form": "bisglycinate", "amount": 40, "unit": "mg"}]))
    preg = score(P(ingredients=[{"name": "Iron", "nutrient": "iron", "form": "bisglycinate", "amount": 40, "unit": "mg"}]), pregnant=True)
    ok = preg["safety"] < base["safety"] and any("pregnan" in f.lower() for f in preg["flags"])
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'}  pregnancy toggle           safety {base['safety']}->{preg['safety']}")
    total = len(CASES) + 1
    print(f"\n{passed}/{total} passed")
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
