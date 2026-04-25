# Porter Five Forces Framework

Reference guide for conducting the three-perspective Porter Five Forces analysis in Phase 3.

---

## The Five Forces

### 1. Supplier Power (供应商议价能力)
**High power (score 4-5) when:**
- Few suppliers dominate the market (concentration)
- Switching costs to alternative suppliers are high
- Suppliers' products are highly differentiated or unique
- Suppliers can credibly threaten forward integration
- The company's purchases represent a small fraction of supplier volume

**Low power (score 1-2) when:**
- Many competing suppliers available
- Low switching costs; commoditized inputs
- Company is a major customer representing large % of supplier revenue
- Company has backward integration capability

**Key questions to answer:**
- Who are the key suppliers? (raw materials, components, labor, technology)
- Is there a single-source dependency risk?
- Are input costs rising due to supplier concentration?

---

### 2. Buyer Power (买方议价能力)
**High power (score 4-5) when:**
- Buyers are concentrated (few large customers = high % of revenue)
- Products are undifferentiated / easy to compare
- Low switching costs for buyers
- Buyers have credible backward integration threat
- Buyers are price-sensitive and well-informed

**Low power (score 1-2) when:**
- Fragmented customer base (no single customer is >5-10% of revenue)
- High switching costs (contracts, data lock-in, training investment)
- Brand loyalty or differentiation makes substitution unlikely
- Product is mission-critical to buyer's operations

**Key questions to answer:**
- What is the customer concentration? (largest customer % of revenue)
- What are the switching costs?
- How price-elastic is demand?

---

### 3. Threat of New Entrants (新进入者威胁)
**High threat (score 4-5) when:**
- Low capital requirements to enter
- Minimal regulatory barriers
- Easy access to distribution channels
- Little brand loyalty or established customer relationships
- Technology is accessible (no patents, trade secrets)

**Low threat (score 1-2) when:**
- High capital intensity (manufacturing plants, infrastructure)
- Significant regulatory approval requirements (FDA, FCC, banking licenses)
- Strong network effects favor incumbents
- Proprietary technology or patents
- Established brand loyalty and customer switching costs

**Key questions to answer:**
- What is the minimum efficient scale?
- Are there regulatory moats?
- Can new entrants replicate distribution/logistics networks?

---

### 4. Threat of Substitutes (替代品威胁)
**High threat (score 4-5) when:**
- Alternative products/services deliver similar value
- Low switching costs to substitutes
- Substitute offers better price-performance ratio
- Buyers are willing to trade off quality for price

**Low threat (score 1-2) when:**
- No functionally equivalent substitute exists
- Substitutes offer significantly inferior performance
- High switching costs to alternatives
- Regulatory or safety requirements mandate the specific product

**Key questions to answer:**
- What could replace this product/service (directly or indirectly)?
- Is the substitute trend accelerating due to technology?
- What is the relative price-performance of substitutes?

---

### 5. Competitive Rivalry (行业竞争强度)
**High rivalry (score 4-5) when:**
- Many competitors of similar size (no dominant player)
- Slow industry growth (companies fight for market share)
- High fixed costs force companies to fill capacity at any price
- Undifferentiated products → price competition
- High exit barriers keep weak competitors in the market

**Low rivalry (score 1-2) when:**
- One or few dominant players (oligopoly or monopoly)
- Fast-growing market (companies grow without taking share)
- Highly differentiated products (compete on value, not price)
- Low fixed costs, low exit barriers

**Key questions to answer:**
- Who are the top 3-5 competitors by market share?
- Is pricing power declining (margin compression)?
- Are competitors engaging in capacity expansion that will oversupply?

---

## Scoring Guidelines

Use these anchor descriptions when assigning 1-5 scores for the radar chart:

| Score | Label | Meaning | Visual |
|-------|-------|---------|--------|
| 1 | Very Low | Force poses negligible threat / company has dominant advantage | Green |
| 2 | Low | Force is present but manageable; company has structural advantages | Green |
| 3 | Moderate | Mixed signals; depends on specific circumstances | Amber |
| 4 | High | Force creates meaningful challenges; requires strategic response | Red |
| 5 | Very High | Force severely constrains profitability or growth | Red |

**Important:** Scores represent the *threat level* for the company, not the strength of the company's position. A score of 5 on Buyer Power = buyers have very high power (bad for the company). A score of 1 = buyers have very little power (good for the company).

**P0 orientation rule:** Never invert the scale into an "attractiveness" or "company strength" score. In this skill, **5 always means the force is worst / most threatening / red**, and **1 always means the force is best / least threatening / green**. For Competitive Rivalry specifically, a brutally competitive industry with price wars should score **4-5 (red)**; a monopoly-like or barely competitive industry should score **1-2 (green)**.

---

## Three Analytical Perspectives

### Perspective 1: Company-Level
Focus on THIS specific company's position. Use:
- `financial_data.json` — revenue concentration, segment mix, margin trends
- `news_intel.json` — recent contract wins/losses, customer relationships
- Company's 10-K "Competition" and "Risk Factors" sections

Example framing: "Apple's supplier power is moderate (3/5). While it depends on TSMC for chip fabrication — a single-source concentration risk — Apple's volume represents ~25% of TSMC's revenue, giving Apple significant leverage."

### Perspective 2: Industry-Level  
Focus on the broader industry / sector dynamics. Use:
- `news_intel.json` — `industry_dynamics` object
- Web search results on sector competitive landscape
- Reference publicly known industry facts (e.g., "Cloud computing is dominated by AWS, Azure, GCP")

**Naming rule (industry tab is not an excuse for vagueness):** When you refer to **incumbents**, **leading players**, **the oligopoly**, or **existing giants** (e.g., in *Threat of new entrants* when the real dynamic is node races and capacity adds among IDMs), **name the top 3–5 firms** in the same or the immediately following sentence—unless the sector truly has no public peer set, in which case say so briefly. Do **not** leave "existing giants" undefined.

Example framing: "The cloud infrastructure industry faces moderate buyer power (3/5) at the enterprise level. Large customers increasingly adopt multi-cloud strategies..."

### Perspective 3: Forward-Looking
Describe how the five forces will evolve over the next 2-3 years. Use:
- `news_intel.json` — `forward_looking` object
- Macro trends, regulatory developments, technology disruption
- M&A activity and competitive dynamics

Example framing: "Supplier power in semiconductors is expected to increase (moving from 3 to 4) as AI chip demand outpaces capacity additions through 2027..."

---

## Writing Guidelines

- Each perspective: ~300 words covering all five forces
- Be specific — name competitors, customers, suppliers where known
- **Incumbents / rivalry / new entrants:** If the narrative says competition is among **existing giants** or **industry leaders** (including "new entrant threat is low because rivalry is really between incumbents"), **list those firms by name** (typically 3–5). Generic placeholders alone are not acceptable in any tab.
- Quantify where possible (market share %, customer concentration %)
- Avoid generic statements like "competition is intense" without substantiation
- Connect Porter analysis to financial performance where relevant (e.g., "High buyer power has compressed gross margins from 45% to 38% over 3 years")

### Phase 5 HTML (locked report template)

For **`{{PORTER_COMPANY_TEXT}}`**, **`{{PORTER_INDUSTRY_TEXT}}`**, and **`{{PORTER_FORWARD_TEXT}}`** in the generated HTML:

1. Use **one `<ul>` with exactly five `<li>` elements** per perspective. Recommended wrapper: `<ul style="margin:0;padding-left:1.25em;">` (matches Equity Research Skill house style).
2. **Fixed order** of list items: supplier power, buyer power, new entrants, substitutes, competitive rivalry — aligned with the radar chart and score list.
3. **Do not** repeat "Force name (X/5)…" at the start of each bullet; scores belong in **`PORTER_*_SCORES`** and the chart, not duplicated in the narrative list.
4. Draft JSON in `porter_analysis.json` so each of `supplier_power`, `buyer_power`, `new_entrants`, `substitutes`, `rivalry` under the relevant perspective is **analysis-only** (no redundant score lead-in), then paste or assemble into the five `<li>` blocks in Phase 5.
