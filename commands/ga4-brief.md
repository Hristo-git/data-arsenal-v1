---
description: "Run what-changed analysis on a GA4 property with AI-powered insights"
allowed-tools: ["Bash", "Read", "Write"]
---

# /ga4-brief - Structured What-Changed Analysis

Four-phase analysis: SCAN → DETECT → INVESTIGATE → **REVIEW** → DEDUPLICATE → OUTPUT. Includes quality gate to filter noise and a deduplication check against previous briefings.

## Usage
`/ga4-brief <property> [--days 7]`

`<property>` can be: numeric property ID, project slug, client name, or URL. See **Property Resolution** below.

## Steps

### Step 0: Setup

**Language check**: Read `~/.config/data-arsenal/config.json`.
- If `language` is set → use that language in its native script for all commentary and recommendations. Bulgarian = Cyrillic (кирилица), NOT Latin transliteration. Data labels and GA4 metric names stay in English.
- If `language` is NOT set (first run) → output as **plain text** (NOT AskUserQuestion):
  "What language should I use? (English / Bulgarian / other)"
  Wait for user response, interpret it, save to config.json so it's never asked again.

**Property resolution**: Resolve `<property>` to a numeric property_id:
1. If numeric → use as property_id directly
2. If matches a project slug in `~/.config/data-arsenal/projects/` → read property_id from that project's config.json
3. If neither → run `resolve_property()` from `_ga4_lib.py` to search GA4 account by name
4. If still not found → ask user to clarify

**Auto-load project**: Scan `~/.config/data-arsenal/projects/*/config.json` for a project where `property_id` matches. If found:
- Load `config.json` (business context)
- Load `context.md` (narrative context)
- Load `data-quality.json` if exists (audit caveats)
- Load `briefing-log.json` if exists (previous findings for dedup)

If no context found, warn that analysis will be generic and suggest `/ga4-context` first.

---

### Step 1: SCAN — Run reports

**a. Run what-changed reports:**

Find the script in order:
- `~/.config/data-arsenal/scripts/ga4-what-changed` (post-setup, primary)
- `scripts/ga4-what-changed` (CWD is the repo)
- If neither exists, tell the user to run `/ga4-setup` first

```bash
~/.config/data-arsenal/scripts/ga4-what-changed <property_id> --days <N>
```

This produces 6 reports: overview, channels, sources, landing pages, products, devices.

**b. Load data quality context:**

Read `projects/<slug>/data-quality.json` (saved by last /ga4-audit). If it exists, note active issues at the top of the analysis:

```
Data quality caveats from last audit (score: X/100):
- [FAIL] Duplicate tracking: engagement rate 100% — all metrics inflated
- [WARN] 15% (not set) landing pages — attribution gaps
- [WARN] Missing begin_checkout event — funnel incomplete
```

If no audit data exists, suggest running `/ga4-audit` first but continue with analysis.

**c. Auto-run audit if stale:**

Check `briefing-log.json` — if no audit in last 7 days, run:

```bash
~/.config/data-arsenal/scripts/ga4-audit <property_id>
```

Parse the output and save results to `projects/<slug>/data-quality.json`:
```json
{
  "health_score": 86,
  "date": "2026-03-21",
  "issues": [
    {
      "check": "Duplicate Tracking",
      "status": "fail",
      "detail": "Engagement rate 100%",
      "impact": "All metrics inflated, trends more reliable than absolutes"
    }
  ],
  "passes": ["Data Volume", "Referral Spam"]
}
```

---

### Step 2: DETECT — Apply thinking patterns

Scan the what-changed output through ALL analytical patterns below. Flag anything that matches. Group by category:

#### CHANNEL & SOURCE PATTERNS

1. **Totals masking opposite trends**
   Total sessions flat? Check if channels are diverging in opposite directions. Stable totals hide volatile segments.

2. **Channel quality shifts**
   More traffic + lower engagement = bad traffic, not growth.
   Less traffic + higher engagement = lost low-quality traffic (possibly good).

3. **Paid vs organic balance shift**
   If paid grows while organic shrinks = growing dependency on ad spend.

4. **Source concentration risk**
   Single source >40% of traffic and growing = dangerous dependency.

5. **Referral anomalies**
   New referral source appearing suddenly = potential spam or partnership.
   Known referral disappearing = broken link or removed listing.

#### DEVICE & TECHNOLOGY PATTERNS

6. **Device-specific anomalies**
   Drop on mobile only = likely site bug or UX issue, not marketing problem.
   Drop on desktop only = less common, check for browser-specific issues.

7. **Cross-device conversion gap**
   Mobile traffic up but conversions only on desktop = mobile UX problem.

#### FUNNEL & CONVERSION PATTERNS

8. **Funnel bottleneck changes**
   If conversions dropped, which funnel step broke? Top (awareness), middle (consideration), or bottom (purchase)?

9. **Cart abandonment spike**
   add_to_cart stable but begin_checkout or purchase dropped = checkout problem.

10. **Conversion rate vs volume divergence**
    Higher conversion rate + lower total conversions = lost top-of-funnel volume.

#### CONTENT & LANDING PAGE PATTERNS

11. **Landing page disappearances**
    Sudden drop in a page's traffic = 404, redirect, de-indexed, or campaign turned off.

12. **Landing page quality shift**
    High-traffic page's bounce rate spiking = content mismatch or broken page.

13. **(not set) landing pages growing**
    Increasing percentage = tracking degradation, consent issues, or direct traffic growth.

#### USER BEHAVIOR PATTERNS

14. **New vs returning divergence**
    New users down = acquisition problem. Returning users down = retention/product problem.

15. **Session depth changes**
    Pages per session dropping across the board = site navigation problem or content quality.

16. **Engagement rate shifts by channel**
    Engagement dropping in one channel only = traffic quality issue for that channel.

#### PRODUCT & REVENUE PATTERNS (ecommerce)

17. **Revenue without transactions**
    Revenue metric moving without purchase events = data quality issue.

18. **Product mix shifts**
    Top seller changing positions = market shift, stock issues, or pricing changes.

19. **AOV changes**
    AOV up + transactions down = losing small buyers.
    AOV down + transactions up = discounting or product mix shift.

20. **Product page to purchase drop**
    view_item stable but add_to_cart dropping = product page UX or pricing problem.

#### GEOGRAPHIC PATTERNS

21. **Country/region traffic shifts**
    Traffic from a new country spiking = potential bot traffic or new market discovery.
    Core market traffic declining = competitive pressure or SEO issue.

22. **City-level anomalies**
    Unusual city appearing in top traffic = likely bot traffic (data centers).

#### DATA QUALITY PATTERNS

23. **Consent gap widening**
    If (not set) dimensions are growing across multiple reports = consent banner change.

24. **Tracking disruption**
    Sudden drop across ALL metrics simultaneously = tag removed or site error.

25. **Duplicate event inflation**
    If data-quality.json flags duplicate tracking, note that ALL metrics are inflated and trends may be more reliable than absolutes.

#### ANTI-PATTERNS (check before concluding)

- <100 sessions in a segment → insufficient sample, don't conclude
- Partial week comparison → data incomplete, note it
- 100% engagement rate → duplicate tracking, flag and don't trust engagement metrics
- Single day spike/drop → could be anomaly not trend, check daily breakdown
- Consent gap >30% → all absolute numbers underreported, focus on trends

---

### Step 3: INVESTIGATE — Hypothesis-driven drill-down

For each detected pattern (max 3-5, ranked by business impact):

**a. HYPOTHESIZE**: Form 1-2 hypotheses
- Reference business context if loaded (What Changed section, goals, competitors)
- Classify: marketing problem / technical problem / data problem?
- If data-quality.json has relevant caveats, factor them in (e.g., "Organic traffic drop could be real OR a consent gap widening")

**b. TEST**: Run targeted ga4-report queries. **Always show date range with each drill-down result**: `[Data: Mar 14-20, 2026]`

**Date range rules:** Use same `--days N` as main comparison. Only widen to 14/30 days when checking if a pattern is trend vs spike, or when <100 data points. Always annotate: `[Data: 14-day trend, Mar 7-20]`

Examples by pattern:

```bash
# Channel drop → daily trend for that channel
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics sessions --dimensions date --filter "sessionDefaultChannelGroup==Organic Search" --days <N>

# Mobile issue → bounce rate by landing page, mobile only
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics bounceRate,sessions --dimensions landingPage --filter "deviceCategory==mobile" --days <N>

# Product shift → item revenue by product
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics itemRevenue --dimensions itemName --days <N>

# Geographic anomaly → sessions by city
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics sessions --dimensions city --days <N>

# Funnel break → ecommerce events by date
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics eventCount --dimensions date --filter "eventName==view_item,add_to_cart,begin_checkout,purchase" --days <N>

# Source quality → engagement by source/medium
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics sessions,engagementRate --dimensions sessionSourceMedium --days <N>
```

**c. VERDICT** per hypothesis:
- **CONFIRMED** — data supports it (cite specific numbers)
- **REFUTED** — data contradicts it
- **INCONCLUSIVE** — need more data, suggest what to check manually

**Mandatory for ecommerce properties** (when config.json has ecommerce events or product data):

1. **Funnel check** — always compare view_item → add_to_cart → begin_checkout → purchase between periods. Run:
```bash
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics eventCount --dimensions eventName --filter "eventName==view_item,add_to_cart,begin_checkout,purchase" --days <N>
```

2. **Product drill-down** — for any revenue change >15%, check which products drove it (volume vs mix shift):
```bash
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics itemRevenue,itemsPurchased --dimensions itemName --days <N>
```

3. **AOV comparison** — calculate current AOV (totalRevenue / ecommercePurchases) and compare against context baseline if available

---

### Step 4: CRITICAL REVIEW — Quality gate (INTERNAL)

**This step is internal. Do NOT show filter results to the user.** Log all decisions (what was kept, dropped, demoted, and why) to the `critical_review` field in `briefing-log.json` (see Step 7). The user sees only the final filtered output.

**Before presenting findings, evaluate ALL findings from Steps 2-3 against these 5 filters. Any finding that fails gets dropped, demoted, or reworked.**

Possible outcomes per finding:
- **KEEP** — survives as a numbered finding
- **DEMOTE to Context Note** — shown under key insight, not a numbered finding
- **DEMOTE to Notable Mention** — small/emerging signal worth watching
- **DEMOTE to Next Steps** — diagnostic action without a confirmed finding
- **DROP** — too small, artifact, or irrelevant to show at all

#### Filter 1: Magnitude — "Does the size matter?"

- Is the absolute change meaningful? (sessions 12→14 = noise, not a finding)
- **DROP** if: change is under 50 sessions, OR under 10% AND under 100 sessions
- Revenue: changes under the business's typical daily variance → flag as noise
- **Exception**: if the segment is critical to the business (priority_channel, best product from context), lower threshold to 5%

#### Filter 2: Data Quality — "Is this real or an artifact?"

- Cross-reference every finding against `data-quality.json` issues
- If duplicate tracking flagged → don't report engagement rate changes as findings
- If consent gap >30% → don't report absolute number changes, only trend direction
- If (not set) is growing → don't attribute traffic drops to marketing until (not set) is excluded
- Any finding fully explained by a known data quality issue → **DROP** (or note as "data artifact, not business signal")
- **If a finding's conclusion is "this is NOT a real change" or "not a business problem" → DEMOTE to Context Note, not a numbered finding**

#### Filter 3: Actionability — "Can the business DO something?"

- Each finding MUST have a specific action — not "improve SEO" but "investigate why /product-page lost 40% organic traffic — check if it was de-indexed"
- If you can't write a specific action → the finding isn't ready. Either drill deeper or drop it
- Generic verdicts like "monitor this" don't count as actions unless paired with a specific trigger ("if this drops below X next week, then...")
- **INCONCLUSIVE with diagnostic-only action (e.g. "check Search Console") → DEMOTE to Next Steps. Exception: impact >20% of total revenue → keep as finding, frame as urgent verification**

#### Filter 4: Novelty — "Is there anything actually new?"

- If ALL findings are [ONGOING] with no worsening → the report is stale. Say so explicitly: "No new developments since [last briefing date]. Previous findings still active:"
- [ONGOING] findings only survive if: magnitude changed >20%, new context explains them, or they've been ongoing >3 briefings without action (escalate)
- Don't pad the report with ongoing findings just to have content

#### Filter 5: Business Relevance — "Would the business owner care?"

- Reference loaded context: does this finding relate to stated goals, priority channel, specific problem, or key metric?
- A 30% drop in a channel that represents 2% of traffic = low relevance unless it's the priority_channel
- A 5% shift in the best_channel = high relevance even though the percentage is small
- If no context loaded, be more conservative — only report large, clear signals

#### Decision Logic After Filters

- **3+ findings survive** → proceed to DEDUPLICATE and OUTPUT normally
- **1-2 findings survive** → proceed but acknowledge: "Relatively quiet period. One notable change:"
- **0 findings survive** → do NOT fabricate findings. Output honestly:

```
## <Project Name> — What Changed
**Property:** <property_name> (<property_id>)
**Period:** <start_date> - <end_date> vs <prev_start> - <prev_end> (<N> days)
**Context:** <loaded / not loaded> | **Data quality:** <score>/100

> **Quiet period — no significant changes detected.**

All metrics within normal range. No new patterns triggered.
Previous ongoing issues: [list if any]

## Recommendation
No action needed this period. Next check: [date]
```

#### Re-investigation Trigger

If initial findings all fail the filters, try ONE round of alternative investigation before reporting quiet:
- Check dimensions not in the standard 6 reports (country, city, browser)
- Look at longer-term trends (compare to 30 days ago, not just last period)
- Check if multiple small changes compound into something meaningful
- If still nothing → report quiet period honestly

---

### Step 5: DEDUPLICATE — Check briefing log

Read `projects/<slug>/briefing-log.json`. Match findings by dimension + metric + direction (not exact numbers).

Tag each finding:
- **[NEW]** — not in previous briefing
- **[ONGOING since date]** — same finding, same direction
- **[WORSENING]** — same finding, magnitude increased >50%
- **[IMPROVING]** — same finding, magnitude decreased >30%
- **[RESOLVED]** — was in previous briefing, no longer detected

If no briefing log exists, all findings are [NEW].

---

### Step 6: OUTPUT — Follow this template EXACTLY

**Language rule for output:** Read the user's configured language from `~/.config/data-arsenal/config.json`. Use that language (in its native script) for ALL labels in this template: section headers, table headers, field labels, status tags, verdict labels, effort/priority values. The template below shows the structure in English as reference — translate every label using the translations from `_translations.py`. GA4 metric names, event names, and Admin menu paths stay in English.

**Translation reference (BG examples):**
- Title: What Changed → Какво се промени
- Headers: Property → Имот, Period → Период, Context → Контекст, Data quality → Качество на данните, Baselines → Базови стойности
- Finding labels: Pattern → Модел, Analysis → Анализ, Verdict → Заключение, Action → Действие
- Table: Metric → Метрика, This period → Текущ, Previous → Предишен, Change → Промяна
- Tags: [NEW] → [НОВО], [ONGOING] → [ПРОДЪЛЖАВА], [WORSENING] → [ВЛОШАВА СЕ], [IMPROVING] → [ПОДОБРЯВА СЕ]
- Verdicts: CONFIRMED → ПОТВЪРДЕНО, REFUTED → ОПРОВЕРГАНО, INCONCLUSIVE → НЕОПРЕДЕЛЕНО
- Sections: Notable Mentions → Забележителни, Next Steps → Следващи стъпки
- Priority: high → висок, medium → среден, low → нисък
- Effort: quick → бързо, medium → средно, project → проект

**You MUST use this output structure every time. Do not improvise the format. Do not add sections not in this template. Do not skip sections that are in this template.**

```
## <Project Name> — What Changed
**Property:** <property_name> (<property_id>)
**Period:** <start_date> - <end_date> vs <prev_start> - <prev_end> (<N> days)
**Context:** <loaded / not loaded> | **Data quality:** <score>/100
**Baselines:** CR <baseline>% (current: X%) | AOV <baseline> (current: X)

> **<One-sentence key insight — the single most important thing>**
>
> **Context:** <one-line note on noise/artifacts affecting the numbers, if any>

---

### Finding 1: <Title> [NEW/ONGOING/WORSENING/IMPROVING]

| Metric | This period | Previous | Change |
|--------|-----------|----------|--------|
| <metric> | <value> | <value> | <+/-X%> |

**Pattern:** <#number — pattern name>
**Analysis:** <2-3 sentences with drill-down evidence. [Data: date range]>
**Verdict:** <CONFIRMED/REFUTED/INCONCLUSIVE> — <one sentence>
**Action:** <specific, actionable> [effort: quick/medium/project]

---

### Finding 2: ...

---

## Notable Mentions
- <emerging signal too small for a full finding but worth watching>

## Next Steps
1. <action> [priority: high/medium/low]
2. ...
```

**Remember:** The template above shows English labels for structural reference only. Replace every label with the user's configured language. For example, in Bulgarian: `## <Project Name> — Какво се промени`, `| Метрика | Текущ | Предишен | Промяна |`, `**Модел:**`, `**Заключение:** ПОТВЪРДЕНО`, `[НОВО]`, `[усилие: бързо]`, `[приоритет: висок]`, etc.

**Ordering rules:**
- Rank findings by business impact, not by percentage change
- Revenue-affecting findings before traffic-only findings
- CONFIRMED findings before INCONCLUSIVE findings
- If a finding is "not a problem" → it should have been demoted to Context Note in Step 4, not a numbered finding
- INCONCLUSIVE with diagnostic-only action → should have been demoted to Next Steps in Step 4 unless impact >20% of total revenue

**Template field rules:**
- **Baselines line**: Only show if context config.json has conversion_rate or aov. Omit the line entirely if no baselines available.
- **Context line under key insight**: Only show if there are noise/artifact notes (bot traffic, data quality caveats). Omit if clean data.
- **Pattern field**: MUST include the pattern number AND name from the 25 patterns list (e.g., `#3 — Paid vs organic balance shift`). Do not use free-text descriptions.
- **Analysis field**: 2-3 sentences showing the drill-down evidence. Include the data date range annotation. This is where reasoning goes — not in ad-hoc sections.
- **Notable Mentions**: Only show if there are demoted findings or emerging small signals. Omit section entirely if none.
- **Effort tags**: Use exactly one of: `quick`, `medium`, `project`

**Date range rules:**
- Header MUST include exact date ranges with format: `Mar 14-20, 2026 vs Mar 7-13, 2026 (7 days)`
- Every drill-down query result shown in the analysis MUST include: `[Data: Mar 14-20, 2026]`
- Calculate actual dates from the `--days` parameter and today's date

**PDF output rules:**
When generating content for PDF reports, use text status indicators instead of emoji:
- Use `[PASS]` / `[WARN]` / `[FAIL]` instead of checkmarks/crosses/warning signs
- Use `[NEW]` / `[ONGOING]` / `[WORSENING]` / `[IMPROVING]` as plain text tags
- Use `**` for emphasis instead of emoji bullets

---

### Step 6.5: SELF-VALIDATE (INTERNAL — do not show to user)

**Before presenting the output, silently verify all of the following. If any check fails, fix the output before presenting. Do NOT mention validation to the user.**

1. **Structure check:**
   - Header has Property, Period with exact dates, Context, Data quality
   - Baselines line present (if context has conversion_rate or aov)
   - Key insight is one sentence, specific (not generic like "several changes detected")
   - Each finding has: title with tag, metrics table, Pattern with number, Analysis, Verdict, Action with effort
   - Next Steps are numbered with `[priority: high/medium/low]` tags
   - No extra sections outside the template (no "Bonus", no ad-hoc headings)

2. **Data integrity check:**
   - Numbers in findings match what the scripts returned (no hallucinated data)
   - Percentages calculated correctly (verify: (new-old)/old * 100)
   - Date ranges match actual query parameters used

3. **Quality check:**
   - No finding says "not a problem" — those should be Context Notes
   - No INCONCLUSIVE finding with only "check X" action — those should be in Next Steps (unless >20% revenue impact)
   - Findings ordered by business impact, not by % change
   - If ecommerce: funnel check was performed
   - Language matches config in native script (Bulgarian = Cyrillic, NOT Latin transliteration). English metric names preserved.
   - Pattern field uses `#N — pattern name` format, not free-text

---

### Step 7: LOG — Update briefing log

Append to `projects/<slug>/briefing-log.json`:

```json
{
  "date": "2026-03-21",
  "period_days": 7,
  "critical_review": {
    "initial_findings_count": 6,
    "dropped": [
      {"id": "small_referral_change", "filter": "magnitude", "reason": "42 sessions, below threshold"}
    ],
    "demoted_to_context": [
      {"id": "direct_bot_traffic", "filter": "data_quality", "reason": "Not a business change - bot cleanup"}
    ],
    "demoted_to_notable": [
      {"id": "chatgpt_traffic", "filter": "magnitude", "reason": "142 sessions - emerging but small"}
    ],
    "demoted_to_next_steps": [],
    "surviving_count": 3,
    "decision": "normal"
  },
  "findings": [
    {
      "id": "organic_search_drop",
      "pattern": "channel_quality_shift",
      "summary": "Organic Search sessions -18%",
      "direction": "decreased",
      "magnitude": 18,
      "status": "new",
      "metric": "sessions",
      "dimension": "Organic Search",
      "confidence": "high",
      "data_quality_caveat": null
    }
  ],
  "health_score": 86,
  "data_quality_issues": ["missing_begin_checkout"],
  "context_used": true
}
```

The `critical_review` field records all filter decisions from Step 4. This is for internal quality tracking — NOT shown to user.

`decision` values: `"normal"` (3+ findings), `"quiet"` (1-2 findings), `"no_findings"` (0 findings)

Keep last 12 briefings (rolling window). If >12 entries, remove the oldest.

If no project folder exists for this property, skip logging and suggest creating one with `/ga4-context`.

---

### Step 8: PDF offer

Ask if the user wants a PDF report. If yes:

1. Prepare findings as a list of dicts matching the `generate_brief_pdf()` signature:

```python
# Each finding dict:
{
    "title": "Cross-network (PMax) Revenue Drop",
    "tag": "NEW",                    # NEW/ONGOING/WORSENING/IMPROVING
    "metrics": [
        {"name": "Cross-network revenue", "current": "3,747 BGN",
         "previous": "7,726 BGN", "change": "-51.5%"}
    ],
    "pattern": "#17 - Revenue without transactions",
    "analysis": "Daily trend shows two outlier days...",
    "verdict": "INCONCLUSIVE",       # CONFIRMED/REFUTED/INCONCLUSIVE
    "verdict_detail": "Could be normal AOV variation",
    "action": "Check Google Ads: PMax ROAS for last 14 days",
    "effort": "quick"                # quick/medium/project
}

# next_steps: [{"action": "Check PMax ROAS", "priority": "high"}]
# context_notes: ["Direct -57% is bot traffic, not real user loss"]
# notable_mentions: ["chatgpt.com: 142 sessions - emerging AI channel"]
# baselines: {"conversion_rate": {"baseline": 1.14, "current": 1.08},
#             "aov": {"baseline": 113.06, "current": 98.50, "currency": "BGN"}}
# period_info: {"current": "Mar 14-20, 2026", "previous": "Mar 7-13, 2026", "days": 7}
```

2. Write a temporary Python script that:
   - Adds `~/.config/data-arsenal/scripts/` to `sys.path`
   - Imports `generate_brief_pdf` from `_pdf_report`
   - Calls it with the structured data
   - Prints the output path

3. Run the script via Bash

4. Report: "PDF saved to [path]"

Default output: `~/Desktop/ga4-brief-{slug}-{date}.pdf`

**Windows:** Prefix script calls with `python3`: `python3 ~/.config/data-arsenal/scripts/...`

## Property Resolution

Accept property name, URL, project slug, or numeric ID:

1. If numeric → use as property_id directly
2. If matches a project slug in `~/.config/data-arsenal/projects/` → read property_id from that project's config.json
3. If neither → run `resolve_property()` from `_ga4_lib.py` to search GA4 account by name
4. If still not found → ask user to clarify

## Communication Style
- Lead with the insight, not the methodology
- Plain language, not GA4 jargon
- Never say "interesting" — say whether it matters and why
- Always end with specific, actionable next steps ranked by impact
- When uncertain, say so and suggest how to verify
