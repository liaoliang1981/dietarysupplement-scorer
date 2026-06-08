---
name: supplement-scorer
description: Score, rate, evaluate, or compare any dietary supplement on three dimensions (formula, quality, safety) using a deterministic, evidence-anchored engine rather than the model's own guess. Brand-agnostic, works across markets and languages. Make sure to use this skill whenever the user pastes a supplement ingredient list, describes a vitamin / mineral / multivitamin / sleep / sports / herbal product, shares or photographs a supplement facts label, or asks things like 'is this supplement any good', 'which one should I buy', 'rate this formula', or 'compare these two' — even if they never say the word 'score'. The skill runs a Python engine for consistent, auditable numbers and supplies structure-function compliance guardrails.
license: MIT
---

# Supplement scorer

Turns a supplement product into auditable scores on **formula**, **quality**,
and **safety** (0-100 each, plus an overall). The numbers come from a
deterministic engine, never from your own estimation — so the same product
always gets the same score, and every number is explainable.

## Workflow

### 1. Build the product into this schema

Gather the product from whatever the user gave you — a pasted ingredient list, a
described product, or a supplement-facts photo (read the label; estimate doses
you can't read cleanly and say so).

```json
{
  "name": "Gentle Iron + Folate",
  "brand": "Acme",
  "certifications": ["GMP", "third_party_tested"],
  "ingredients": [
    {"name": "Iron", "nutrient": "iron", "form": "ferrous bisglycinate", "amount": 18, "unit": "mg"}
  ]
}
```

`nutrient` must be a key from `references/ingredients.json` (iron, folate,
vitamin_d, vitamin_b12, vitamin_b6, vitamin_c, vitamin_e, vitamin_a, vitamin_k,
calcium, magnesium, zinc, iodine, choline, omega3_epa_dha, melatonin, creatine,
coq10, ashwagandha, collagen). For an ingredient with no matching key, still
include it with its `name`; the engine reports it as not-yet-covered.

### 2. Run the engine (never invent scores)

```bash
python {skill_dir}/scripts/score.py --json '{...the product json...}'
```

Add `--pregnant` if the user is pregnant or nursing. The script prints JSON with
`formula`, `quality`, `safety`, `overall`, `flags`, `unknown`, `coverage`,
`rationale`, and `disclaimer`. To compare products, run it once per product.

### 3. Present the result

- Lead with the overall and the three sub-scores.
- Explain *why* using the `rationale` and `flags`, in the user's language,
  concisely.
- If `unknown` is non-empty, say plainly that those ingredients aren't covered
  and the score only reflects `coverage` of the formula.
- End with the `disclaimer`.

## Rules

- **Never fabricate or hand-calculate a score** — always run the script.
- **Brand-neutral**: score by the data, regardless of brand.
- **Compliance**: structure-function language only ("supports", "helps
  maintain"); never disease claims ("treats", "cures", "prevents [disease]").
  Don't advise starting/stopping medication; refer symptoms to a professional.
- **Honesty**: the score is a transparent methodology, not objective truth;
  reference values are an international baseline that varies by country.

For the full scoring logic, the honesty framing, and detailed compliance
guidance, read `references/methodology.md`. The tunable weights and the
ingredient reference table are in `references/ingredients.json`.
