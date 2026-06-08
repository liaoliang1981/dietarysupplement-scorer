# Scoring methodology and compliance

Read this when you need the full logic behind the numbers, or to explain *why*
a product scored the way it did. The engine lives in `scripts/score.py`; the
tunable values (weights, certification points, the reference table) live in
`references/ingredients.json` so facts and editorial weights stay separate from
the algorithm.

## The three dimensions (each 0-100)

- **Formula** — for each recognised active: is the dose in an evidence-backed
  efficacious range, and is the form bioavailable? Doses below half the
  efficacious low are flagged as "fairy dusting". Averaged across recognised
  actives.
- **Quality** — starts at a base, adds points for certifications (third-party
  testing weighted highest, then NSF/USP/GMP, etc.) and for bioavailable forms.
  No certifications = quality is unverifiable.
- **Safety** — starts at 100, subtracts for any dose above its tolerable upper
  limit (UL), with an optional pregnancy-caution adjustment.
- **Overall** = weighted blend (default 0.45 formula + 0.25 quality + 0.30
  safety). The weights are an editorial choice, set in `config.weights`.

## Coverage and unknown ingredients

Ingredients whose `nutrient` key is not in the reference table are listed under
`unknown` and excluded from scoring; `coverage` reports recognised/total. ALWAYS
surface this when explaining: a high formula score on `coverage: 1/3` only
describes the one ingredient that was scored. Never imply full coverage you
don't have.

## Honest framing (state these when relevant)

- The score is a **transparent, reproducible methodology**, not objective truth.
  "Best supplement" depends on the person, goal, and contested evidence.
- Reference values are a **v0 international baseline**; RDA/UL and what's even
  sold or permitted **vary by country**. If the user names a market, caveat
  accordingly and default to the most conservative reading.
- These figures need expert review and per-market sourcing before any
  production/consumer use.
- "Gaming" the score by making genuinely better-dosed, better-tested, more
  bioavailable products is fine — that's the metric working.

## Compliance (apply to every response)

- Use structure-function language ("supports", "helps maintain"). NEVER disease
  claims ("treats", "cures", "prevents [disease]", "diagnoses").
- Do not tell anyone to start, stop, or change a prescription medication. For
  symptoms or pregnancy complications, recommend a qualified professional.
- Append the disclaimer returned by the script (`disclaimer` field).
- Claim rules differ by jurisdiction (US FTC/FDA, EU EFSA, China 保健食品,
  Thailand อย., etc.). When unsure, stay conservative and say rules vary by market.
