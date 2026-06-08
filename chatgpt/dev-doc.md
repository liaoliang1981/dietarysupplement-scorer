# dietarysupplement.ai 补剂评测器 —— ChatGPT 开发文档

> 给开发者的一站式构建指南。照此可在 ChatGPT 上把"补剂打分"做成一个 Custom GPT,或集成进你自己的产品后端。

---

## 0. 核心思路(先读这段)

**可移植的资产 = 打分引擎 + 参考数据 + 方法学 + 合规规则。ChatGPT 只是一个"调用层"。**

- 打分由**确定性引擎**(`score.py`)算出,**不让模型猜分数**——同样输入永远同样输出、可审计。
- 模型(ChatGPT)负责:把用户输入(成分表 / 文字描述 / 标签照片)解析成结构化产品,调用引擎,然后用用户的语言解释结果、守合规。
- 这份引擎和 Claude skill 版完全相同 → **保持单一真相源,两边同步**,别各写一份。

| 组成 | 在 ChatGPT 里对应 |
|---|---|
| 触发 + 指令 | Custom GPT 的 **Instructions**(见 §3) |
| 参考数据 / 文档 | Custom GPT 的 **Knowledge** 文件(`score.py`、`methodology.md`) |
| 确定性引擎 | Code Interpreter 跑 `score.py`,**或** 通过 **Action** 调你的后端 |
| 程序化集成 | **Responses API** + function calling(见 §6) |

---

## 1. 三条开发路线 —— 先选一条

| 路线 | 适合 | 是否要后端 | 一致性 |
|---|---|---|---|
| **A. Custom GPT + Code Interpreter** | 最快出一个能用的、给 chatgpt.com 用户 | 否 | 高(但偶有沙箱波动) |
| **B. Custom GPT + Action** | 给用户用且要稳 | 要(部署 `score.py` 为 API) | 最高 |
| **C. Responses API + function calling** | 接进你自己的 App / 产品后端 | 要 | 最高 |

建议:先用 **A** 跑通验证;要上线给用户用、追求每次分数一致,换 **B**;要做进自己的产品就 **C**。

> ⚠️ Custom GPT 必须在你自己的 OpenAI 账号里创建,我无法替你建——下面给你全部素材,你照着拼。

---

## 2. 产品数据结构(三条路线通用)

引擎接收的产品 JSON:

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

`nutrient` 必须是引擎已收录的键之一:
`iron, folate, vitamin_d, vitamin_b12, vitamin_b6, vitamin_c, vitamin_e, vitamin_a, vitamin_k, calcium, magnesium, zinc, iodine, choline, omega3_epa_dha, melatonin, creatine, coq10, ashwagandha, collagen`

未收录的成分照样填 `name`,引擎会把它列进 `unknown` 并在 `coverage`(覆盖 X/Y)里反映,**不静默丢弃**。

`certifications` 可识别项:`GMP, third_party_tested, NSF, USP, informed_sport, non_gmo`。

引擎返回:`formula / quality / safety / overall`(各 0–100)、`flags`(风险旗标)、`unknown`、`coverage`、`rationale`(逐条理由)、`disclaimer`。

---

## 3. 路线 A —— Custom GPT(无后端,最快)

**步骤:**
1. chatgpt.com → **Explore GPTs → Create**。
2. **Instructions**:粘贴下面 §3.1 的全文。
3. **Knowledge**:上传 `score.py` 和 `methodology.md`。
4. **Capabilities**:打开 **Code Interpreter & Data Analysis**。
5. 测试:贴一段成分表,或上传一张营养成分表照片。GPT 会跑 `score.py` 并解释。

代价:Code Interpreter 可靠但不是 100% 每次都"老老实实跑脚本"。Instructions 里已强力要求它跑;要彻底稳就走路线 B。

### 3.1 Instructions(整段粘贴到 Custom GPT 的 Instructions 框)

```
You are dietarysupplement.ai's supplement scorer — an independent, evidence-literate advisor that rates dietary supplements for users in ANY country, in ANY language, across ALL categories (vitamins, minerals, multivitamins, sleep, sports, bone, stress, herbal, men's and women's health). You treat all brands equally and never favor any brand; if the data says a product is weak, you say so.

WHAT YOU DO
When the user pastes an ingredient list, describes a product, shares a supplement-facts photo, or asks "is this any good / which should I buy / rate this / compare these," you SCORE it on formula, quality, and safety.

HOW TO SCORE (critical)
Never estimate or invent a score. Scores come from a deterministic engine. To get them:
1) Build the product into this JSON:
   {"name":"...","brand":"...","certifications":["GMP","third_party_tested"],
    "ingredients":[{"name":"Iron","nutrient":"iron","form":"ferrous bisglycinate","amount":18,"unit":"mg"}]}
   nutrient must be one of: iron, folate, vitamin_d, vitamin_b12, vitamin_b6, vitamin_c, vitamin_e, vitamin_a, vitamin_k, calcium, magnesium, zinc, iodine, choline, omega3_epa_dha, melatonin, creatine, coq10, ashwagandha, collagen. For an ingredient with no matching key, still include its name; the engine reports it as not-yet-covered.
2) Run the bundled engine with Code Interpreter:
   import json, score; print(json.dumps(score.score(<product_dict>)))
   (add pregnant=True if the user is pregnant or nursing.)
   If a scoreSupplement Action is configured, call that Action instead.
3) Read formula, quality, safety, overall, flags, unknown, coverage, rationale, disclaimer.

HOW TO PRESENT
- Lead with overall + the three sub-scores.
- Explain WHY using rationale and flags, in the user's language, concisely.
- If unknown is non-empty, say plainly those ingredients aren't covered and the score only reflects coverage of the formula.
- To compare, run the engine once per product, then compare.
- End with the disclaimer.

RULES
- Never fabricate or hand-calculate a score — always run the engine.
- Brand-neutral: score strictly by the data.
- Compliance: structure-function language ("supports","helps maintain"); NEVER disease claims ("treats","cures","prevents [a disease]"). Don't tell anyone to start/stop/change a prescription medication; refer symptoms and pregnancy concerns to a professional.
- Honesty: the score is a transparent methodology, not objective truth; reference values are a v0 international baseline and vary by country. If the user names a market, caveat accordingly and stay conservative.
- For full logic and compliance detail, consult the methodology.md knowledge file.
```

---

## 4. 路线 B —— Custom GPT + Action(稳健、确定)

1. 把 §7 的 `score.py` 部署成一个 HTTPS API(见 §5 的 `server.py`)。
2. GPT 编辑器 → **Actions → Create** → 粘贴 §4.1 的 OpenAPI,把 `servers.url` 换成你部署的地址。
3. Instructions 里 GPT 会改为调用 `scoreSupplement` Action(而不是 Code Interpreter)。

Action 在服务端跑你的引擎,分数每次一致、无沙箱波动。该端点**只跑打分引擎,不需要任何 LLM key**;**绝不要把任何 key 写进前端**。

### 4.1 Action OpenAPI Schema

```yaml
openapi: 3.1.0
info:
  title: dietarysupplement.ai Scoring API
  description: Deterministic scoring of a dietary supplement on formula, quality, and safety.
  version: "1.0.0"
servers:
  - url: https://YOUR-DEPLOYED-HOST.example.com
paths:
  /score:
    post:
      operationId: scoreSupplement
      summary: Score a dietary supplement product.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Product"
      responses:
        "200":
          description: Score result
          content:
            application/json:
              schema:
                type: object
components:
  schemas:
    Product:
      type: object
      required: [ingredients]
      properties:
        name: { type: string }
        brand: { type: string }
        pregnant: { type: boolean }
        certifications:
          type: array
          items: { type: string }
        ingredients:
          type: array
          items:
            type: object
            required: [nutrient, amount]
            properties:
              name: { type: string }
              nutrient: { type: string }
              form: { type: string }
              amount: { type: number }
              unit: { type: string }
```

---

## 5. 后端服务(路线 B 和 C 共用)

`server.py` —— 把引擎包成 `POST /score`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from score import score

app = FastAPI(title="dietarysupplement.ai scoring API")

class Ingredient(BaseModel):
    name: Optional[str] = None
    nutrient: str
    form: Optional[str] = ""
    amount: float
    unit: Optional[str] = ""

class Product(BaseModel):
    name: Optional[str] = ""
    brand: Optional[str] = ""
    pregnant: Optional[bool] = False
    certifications: Optional[List[str]] = []
    ingredients: List[Ingredient]

@app.post("/score")
def score_endpoint(product: Product):
    p = product.model_dump()
    return score(p, pregnant=bool(p.get("pregnant")))

@app.get("/health")
def health():
    return {"ok": True}
```

部署:`pip install fastapi uvicorn` → `uvicorn server:app --host 0.0.0.0 --port 8000`。
可放任何能跑 Python 的地方(Render / Railway / Fly / 一台 VM)。Serverless(Vercel/Cloudflare)改写 handler 即可,核心 `score.py` 不变。

---

## 6. 路线 C —— Responses API(你自己的产品后端)

> 注意:OpenAI 的 **Assistants API 已弃用,2026-08-26 关停** → 用 **Responses API** + function calling。你的服务端跑确定性引擎,模型只负责"调用它"。

```python
from openai import OpenAI
import json
from score import score

client = OpenAI()
tools = [{
    "type": "function",
    "name": "score_supplement",
    "description": "Score a dietary supplement on formula, quality, safety.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "certifications": {"type": "array", "items": {"type": "string"}},
            "ingredients": {"type": "array", "items": {"type": "object"}}
        },
        "required": ["ingredients"]
    }
}]

resp = client.responses.create(
    model="gpt-5.5",   # 用你当前的模型
    input=[{"role": "user", "content": "Score: iron 18mg bisglycinate + folate 400mcg 5-MTHF, GMP tested"}],
    tools=tools,
)
# 当模型发出 function call 时:解析参数 -> result = score(args) -> 把 json.dumps(result) 作为
# function_call_output 回传(用 previous_response_id 续上),模型再据此组织解释。
```

---

## 7. 打分引擎 `score.py`(完整代码,自包含)

> 上传到 Custom GPT 的 Knowledge,或被 `server.py` import。已验证:优质铁剂综合 97、廉价多维 52、超 UL 会扣安全分并出旗标、未收录成分标 coverage。

```python
#!/usr/bin/env python3
"""Deterministic supplement scoring engine (self-contained).
Reference values are a v0 INTERNATIONAL BASELINE — illustrative, not authoritative.
RDA/UL and permitted claims vary by country. Review + source per-market before production.
"""
import argparse, json, sys

CONFIG = {
    "weights": {"formula": 0.45, "quality": 0.25, "safety": 0.30},
    "quality_base": 45,
    "cert_points": {"gmp": 12, "third_party_tested": 18, "nsf": 16, "usp": 16, "informed_sport": 10, "non_gmo": 4},
    "bioavailable_bonus_per": 4, "bioavailable_bonus_max": 15,
    "form_bonus": 8, "form_penalty": 10,
    "fairy_dust_points": 20, "below_range_points": 55, "in_range_points": 100, "above_range_points": 80,
}
REFERENCE = {
    "iron": {"unit": "mg", "ul": 45, "eff": [14, 65], "good": ["bisglycinate", "fumarate"], "poor": ["sulfate"], "pregnancy": "caution_high_dose"},
    "folate": {"unit": "mcg", "ul": 1000, "eff": [400, 800], "good": ["l-5-mthf", "l-methylfolate", "5-mthf"], "poor": ["folic acid"], "pregnancy": "recommended"},
    "vitamin_d": {"unit": "iu", "ul": 4000, "eff": [1000, 4000], "good": ["d3", "cholecalciferol"], "poor": ["d2", "ergocalciferol"]},
    "vitamin_b12": {"unit": "mcg", "ul": None, "eff": [2.4, 1000], "good": ["methylcobalamin", "adenosylcobalamin"], "poor": ["cyanocobalamin"]},
    "vitamin_b6": {"unit": "mg", "ul": 100, "eff": [1.3, 50], "good": ["p-5-p", "pyridoxal-5-phosphate"], "poor": ["pyridoxine hcl"]},
    "vitamin_c": {"unit": "mg", "ul": 2000, "eff": [75, 500], "good": [], "poor": []},
    "vitamin_e": {"unit": "mg", "ul": 1000, "eff": [15, 268], "good": ["d-alpha", "mixed tocopherol"], "poor": ["dl-alpha"]},
    "vitamin_a": {"unit": "mcg", "ul": 3000, "eff": [700, 3000], "good": [], "poor": []},
    "vitamin_k": {"unit": "mcg", "ul": None, "eff": [90, 180], "good": ["mk-7", "mk-4"], "poor": []},
    "calcium": {"unit": "mg", "ul": 2500, "eff": [500, 1200], "good": ["citrate", "malate"], "poor": ["carbonate"]},
    "magnesium": {"unit": "mg", "ul": 350, "eff": [200, 400], "good": ["glycinate", "citrate", "malate"], "poor": ["oxide"]},
    "zinc": {"unit": "mg", "ul": 40, "eff": [8, 25], "good": ["bisglycinate", "picolinate"], "poor": ["oxide"]},
    "iodine": {"unit": "mcg", "ul": 1100, "eff": [150, 220], "good": [], "poor": []},
    "choline": {"unit": "mg", "ul": 3500, "eff": [300, 550], "good": [], "poor": []},
    "omega3_epa_dha": {"unit": "mg", "ul": None, "eff": [250, 2000], "good": ["triglyceride", "rtg"], "poor": ["ethyl ester"]},
    "melatonin": {"unit": "mg", "ul": None, "eff": [0.5, 5], "good": [], "poor": []},
    "creatine": {"unit": "g", "ul": None, "eff": [3, 5], "good": ["monohydrate"], "poor": ["hcl", "ethyl ester"]},
    "coq10": {"unit": "mg", "ul": None, "eff": [100, 200], "good": ["ubiquinol"], "poor": []},
    "ashwagandha": {"unit": "mg", "ul": None, "eff": [300, 600], "good": ["ksm-66", "sensoril"], "poor": []},
    "collagen": {"unit": "g", "ul": None, "eff": [2.5, 15], "good": [], "poor": []},
}

def _clamp(v): return int(round(max(0, min(100, v))))

def score(product, pregnant=False):
    cfg = CONFIG
    ings = product.get("ingredients", []) or []
    w = cfg["weights"]
    recognised, earned, unknown = 0, 0.0, []
    f_detail, flags = [], []
    for ing in ings:
        ref = REFERENCE.get((ing.get("nutrient") or "").lower())
        if not ref:
            unknown.append(ing.get("name") or ing.get("nutrient") or "unknown"); continue
        recognised += 1
        amt = float(ing.get("amount") or 0); form = (ing.get("form") or "").lower()
        lo, hi = ref["eff"]
        if amt < lo * 0.5:
            pts, verdict = cfg["fairy_dust_points"], "underdosed (fairy dusting)"
            flags.append(f"{ing.get('name', '')} underdosed at {amt}{ref['unit']}")
        elif amt < lo: pts, verdict = cfg["below_range_points"], "below efficacious range"
        elif amt <= hi: pts, verdict = cfg["in_range_points"], "within efficacious range"
        else: pts, verdict = cfg["above_range_points"], "above typical range"
        if ref["good"] and any(g in form for g in ref["good"]): pts = min(100, pts + cfg["form_bonus"]); fnote = "bioavailable form"
        elif ref["poor"] and any(p in form for p in ref["poor"]): pts = max(0, pts - cfg["form_penalty"]); fnote = "lower-absorption form"
        else: fnote = "form unspecified"
        earned += pts
        f_detail.append(f"{ing.get('name', '')} {amt}{ref['unit']}: {verdict}, {fnote}")
    formula = _clamp(earned / recognised) if recognised else 0

    q = cfg["quality_base"]; q_detail = []
    for cert in product.get("certifications", []) or []:
        pts = cfg["cert_points"].get(cert.lower().replace(" ", "_"), 0)
        if pts: q += pts; q_detail.append(f"+{pts} {cert}")
    bio = sum(1 for ing in ings if (r := REFERENCE.get((ing.get("nutrient") or "").lower())) and r["good"] and any(g in (ing.get("form") or "").lower() for g in r["good"]))
    if bio:
        b = min(cfg["bioavailable_bonus_max"], bio * cfg["bioavailable_bonus_per"])
        q += b; q_detail.append(f"+{b} bioavailable forms")
    if not (product.get("certifications") or []): q_detail.append("no certifications listed — quality unverifiable")
    quality = _clamp(q)

    s = 100.0; s_detail = []
    for ing in ings:
        ref = REFERENCE.get((ing.get("nutrient") or "").lower())
        if not ref: continue
        amt = float(ing.get("amount") or 0); ul = ref.get("ul")
        if ul and amt > ul:
            pen = 25 if amt > ul * 1.5 else 15; s -= pen
            flags.append(f"{ing.get('name')} {amt}{ref['unit']} exceeds UL ({ul}{ref['unit']})")
            s_detail.append(f"-{pen} {ing.get('name')} above tolerable upper limit")
        if pregnant and ref.get("pregnancy") == "caution_high_dose" and ul and amt > ul * 0.8:
            s -= 10; flags.append(f"{ing.get('name')} dose may warrant caution in pregnancy")
    if not s_detail: s_detail.append("all actives within tolerable upper limits")
    safety = _clamp(s)

    overall = _clamp(w["formula"] * formula + w["quality"] * quality + w["safety"] * safety)
    total = recognised + len(unknown)
    return {
        "product": product.get("name", ""), "brand": product.get("brand", ""),
        "formula": formula, "quality": quality, "safety": safety, "overall": overall,
        "flags": flags, "unknown": unknown,
        "coverage": f"{recognised}/{total}" if total else "0/0",
        "rationale": {"formula": f_detail, "quality": q_detail, "safety": s_detail},
        "disclaimer": ("General wellness information, not medical advice. Scores use a v0 international "
                       "baseline; reference values and permitted claims vary by country. Not intended to "
                       "diagnose, treat, cure, or prevent any disease. Consult a qualified professional."),
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("file", nargs="?"); ap.add_argument("--json"); ap.add_argument("--pregnant", action="store_true")
    a = ap.parse_args()
    try:
        product = json.loads(a.json) if a.json else (json.loads(open(a.file, encoding="utf-8").read()) if a.file else json.loads(sys.stdin.read()))
    except Exception as e:
        print(json.dumps({"error": f"could not parse product JSON: {e}"})); sys.exit(1)
    print(json.dumps(score(product, pregnant=a.pregnant), ensure_ascii=False, indent=2))
```

---

## 8. 打分方法学(便于你调参)

三个维度各 0–100,带可读 `rationale`:

- **配方 formula**:每个已识别活性成分,看剂量是否落在循证有效区间、形式是否生物利用度高;低于有效量一半判"fairy dusting"扣分;按已识别成分求平均。
- **质量 quality**:基础分起步,加认证分(第三方检测权重最高,其次 NSF/USP/GMP)和可吸收形式分;无认证 = 质量不可核验。
- **安全 safety**:从 100 起,任一剂量超过可耐受上限(UL)扣分,孕期可加扣。
- **综合**:`0.45×配方 + 0.25×质量 + 0.30×安全`。权重是编辑选择,在 `CONFIG.weights` 里改。

**覆盖与未收录**:不在 `REFERENCE` 的成分进 `unknown`、不计分,`coverage` 报告 已识别/总数。解释时务必说明:`coverage 1/3` 上的高分只描述被算到的那一个成分,不能假装覆盖全部。

---

## 9. 合规与诚实(每次回复都遵守)

- 只用结构功能性表述("支持""有助于维持");**绝不**疾病声称("治疗""治愈""预防某病""诊断")。
- 不让人开始/停止/更改处方药;症状或孕期问题建议看专业医生。
- 每次回复末尾附引擎返回的 `disclaimer`。
- 各国声称规则不同(US FTC/FDA、EU EFSA、中国保健食品、泰国 อย. 等);不确定时按最保守口径,并说明各国不同。

---

## 10. 注意事项 / 诚实账

- `REFERENCE` 里的参考值是 **v0 国际基线、手工录入、非权威**。每个市场的 RDA/UL 和可售/可声称项都不同——上线前必须经专业人士复核并按市场挂来源。
- Code Interpreter(路线 A)偶有不"老实跑脚本"的波动;要确定性就用路线 B/C 的服务端引擎。
- 引擎与 Claude skill 版相同 → 改了一边记得同步另一边,保持单一真相源。
- Custom GPT 必须在你自己的 OpenAI 账号里创建。
