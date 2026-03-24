# Data Arsenal v1 — AI-Powered GA4 Analyst

Open-source Claude Code plugin that turns Claude into a senior GA4 analyst. 6 what-changed reports, 20 health checks, 25 thinking patterns. Context engineering for analysis that actually explains WHY.

**Your GA4 totals are lying to you.** Revenue looks flat — but Product A is down 67%, Product B down 85%, and Product C up 88% compensating. Same story across devices, regions, campaigns. This is the KPI Surface Trap. Checking every breakdown every day is impossible manually. This tool does it for you.

## The Problem

| Reality | Impact |
|---------|--------|
| **~65% of traffic is invisible** | Consent mode (~55% loss), ad blockers (~33%), grey bots (~10%) — your absolute numbers are always wrong |
| **Totals mask opposite trends** | Flat sessions can hide channels diverging in opposite directions |
| **Manual analysis doesn't scale** | Checking 6 dimensions x 5 metrics x 7 days = hundreds of comparisons per client |
| **Dashboards show numbers, not answers** | They tell you WHAT changed, never WHY |
| **AI is terrible at math** | LLMs hallucinate statistics — they need tools to get real numbers |

Most analytics workflows sit at Level 2 (dashboards) or Level 3 (alerts). Data Arsenal is **Level 4: Autonomous** — an AI agent that investigates, reasons, and explains. No magic. Just system and strategy.

## Quick Start

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Plan or Max). Paste this into Claude Code and it handles the rest:

```
git clone https://github.com/ivanovzlatan2/data-arsenal-v1.git && cd data-arsenal-v1 && claude plugin install . && echo "Plugin installed. Run /ga4-setup to connect your GA4 account."
```

Then inside Claude Code:

```
/ga4-setup
```

This installs dependencies, opens your browser for Google sign-in, and verifies access. Everything is handled automatically.

> **Note:** Google will show an "unverified app" warning because the OAuth client is bundled with the open-source code (not published as a verified web app). Click **Advanced** → **Go to Data Arsenal (unsafe)** to proceed. The only permission requested is read-only access to Analytics — the app cannot modify your data. You can review the OAuth scope (`analytics.readonly`) and the full source code in this repo.

Once setup is complete:

```
/ga4-audit my-store          # Health check by property name
/ga4-audit 123456789         # Or by property ID
/ga4-brief my-store          # What-changed analysis (AI-powered insights)
```

You can use the **property name** (or part of it) instead of the numeric ID. Use `list` to see all properties:

```
~/.config/data-arsenal/scripts/ga4-audit list
```

## Commands

| Command | What it does |
|---------|-------------|
| `/ga4-setup` | One-time setup: install deps, authenticate, verify access |
| `/ga4-audit <property>` | 20 built-in health checks with health score |
| `/ga4-brief <property>` | What-changed analysis with business context |
| `/ga4-context <client>` | Create/update business context file (interactive) |
| `/ga4-report <property>` | Custom GA4 report with any metrics/dimensions |

`<property>` can be a numeric ID (e.g., `123456789`) or a name search (e.g., `my-store`).

### Options

```
/ga4-brief my-store --days 14              # Compare last 14 days vs previous 14
/ga4-brief my-store --context my-store     # Use business context file
/ga4-report my-store --metrics sessions,activeUsers --dimensions date --days 30
```

## The 3-Layer Model (How It Works)

Most AI analytics tools do one thing: feed data to an LLM and hope for the best. Data Arsenal uses three distinct layers, each solving a different problem.

### Layer 1: Tools & Data

Python scripts crunch real GA4 data via the Data API. Dual date ranges in a single API call. Changes scored by impact formula: `absolute_change * min(percentage_change, 200%) / 100`. This surfaces changes that are both large AND significant.

AI is terrible at math — it needs tools to get real numbers. Layer 1 provides the precise, calculated foundation. No hallucinated statistics.

### Layer 2: Direction & Context

Raw numbers without business context lead to wrong conclusions. Layer 2 provides per-project context files: goals, funnel stages, competitors, seasonality, recent changes. Auto-enriched from the client's website via `/ga4-context`.

Without this, you optimize for the wrong thing. With it, the analysis knows that a traffic drop during your off-season is normal, or that a conversion spike coincides with a campaign launch.

### Layer 3: Reasoning & Patterns

25 thinking patterns + hypothesis-driven investigation. When the data shows a drop, Layer 3 doesn't just report it — it checks if channels are diverging, if a device-specific bug appeared, if a landing page disappeared, if the product mix shifted.

The layer nobody provides. The biggest difference maker.

## What You Get

### What-Changed Reports (6 reports)

- **Overview** — Key metrics comparison (sessions, users, conversions, revenue, engagement)
- **Channels** — Which channels grew or declined, ranked by impact
- **Sources** — Source/medium level changes
- **Landing Pages** — Pages gaining or losing traffic
- **Products** — Product performance changes (e-commerce only, auto-detected)
- **Devices** — Device-specific anomalies

Each change is impact-scored and ranked. The biggest movers surface first.

### Health Checks (20 checks)

30 hours of manual auditing compressed into 2 minutes:

1. Data Volume
2. Duplicate Tracking
3. Enhanced Measurement
4. Conversion Events
5. E-commerce Completeness
6. Referral Spam
7. Self-Referral
8. (not set) Landing Pages
9. High Bounce Pages
10. Event Variety
11. Event Naming
12. Recommended Events
13. Payment Gateway Referral
14. Channel Diversification
15. Hostname Pollution
16. PII in URLs
17. Bot Traffic
18. Event Quality
19. Direct Traffic
20. Engagement Rate Anomalies

### Context Engineering

The secret weapon. Create business context files that make analysis 10x better. Claude uses your goals, funnel, competitors, and recent changes to explain WHY numbers moved — not just what changed.

```
/ga4-context my-store
```

### PDF Reports

Generate client-ready PDF deliverables from any analysis. Professional formatting, multi-language support, ready to send.

## 25 Thinking Patterns

Built-in analytical patterns applied during every what-changed analysis. Grouped by category:

### Channel & Source (5)
1. **Totals masking opposite trends** — Stable totals hide volatile segments
2. **Channel quality shifts** — More traffic + lower engagement = bad traffic, not growth
3. **Paid vs organic balance shift** — Paid growing while organic shrinks = ad spend dependency
4. **Source concentration risk** — Single source >40% of traffic = dangerous dependency
5. **Referral anomalies** — New source appearing suddenly = spam or partnership

### Device & Technology (2)
6. **Device-specific anomalies** — Drop only on mobile = site bug, not marketing problem
7. **Cross-device conversion gap** — Mobile traffic up, conversions only on desktop = mobile UX problem

### Funnel & Conversion (3)
8. **Funnel bottleneck changes** — Which step broke: top, middle, or bottom?
9. **Cart abandonment spike** — add_to_cart stable but purchase dropped = checkout problem
10. **Conversion rate vs volume divergence** — Higher rate + lower total = lost top-of-funnel

### Content & Landing Page (3)
11. **Landing page disappearances** — Sudden traffic drop = 404, redirect, or de-indexed
12. **Landing page quality shift** — Bounce rate spiking = content mismatch or broken page
13. **(not set) landing pages growing** — Tracking degradation or consent issues

### User Behavior (3)
14. **New vs returning divergence** — New users down = acquisition. Returning down = retention
15. **Session depth changes** — Pages per session dropping = navigation or content problem
16. **Engagement rate shifts by channel** — One channel dropping = traffic quality issue

### Product & Revenue (4)
17. **Revenue without transactions** — Revenue moving without purchases = data quality issue
18. **Product mix shifts** — Top seller changing = market shift, stock, or pricing
19. **AOV changes** — AOV up + transactions down = losing small buyers
20. **Product page to purchase drop** — view_item stable, add_to_cart dropping = product page problem

### Geographic (2)
21. **Country/region traffic shifts** — New country spiking = potential bot traffic
22. **City-level anomalies** — Unusual city in top traffic = likely data center bots

### Data Quality (3)
23. **Consent gap widening** — (not set) growing across reports = consent banner change
24. **Tracking disruption** — All metrics dropping simultaneously = tag removed or site error
25. **Duplicate event inflation** — ALL metrics inflated, trends more reliable than absolutes

## Architecture

```
# Repository (committed to GitHub)
data-arsenal-v1/
├── CLAUDE.md              # Agent instructions + thinking patterns
├── commands/              # Slash command definitions
│   ├── ga4-audit.md
│   ├── ga4-brief.md
│   ├── ga4-context.md
│   ├── ga4-report.md
│   └── ga4-setup.md
├── contexts/              # Templates + examples
│   ├── _template.json
│   ├── _template.md
│   ├── example-ecommerce.json
│   └── example-b2b.json
├── scripts/               # Python scripts (GA4 Data API)
│   ├── ga4-audit
│   ├── ga4-what-changed
│   ├── ga4-report
│   ├── ga4-setup
│   ├── _ga4_lib.py
│   ├── _pdf_report.py
│   └── _translations.py
└── examples/              # Sample outputs
```

```
# User data (never committed)
~/.config/data-arsenal/
├── config.json            # Global config (language, auth mode)
├── credentials.json       # OAuth tokens
├── scripts/               # Installed scripts
└── projects/              # Per-client project folders
    ├── client-name/
    │   ├── config.json        # Structured business context
    │   ├── context.md         # Narrative context + enrichment
    │   ├── data-quality.json  # Last audit results
    │   ├── briefing-log.json  # Briefing history
    │   └── reports/           # Generated PDFs
    └── another-client/
```

## Standalone Usage (without Claude Code)

The Python scripts work independently:

```bash
# Setup
python3 scripts/ga4-setup

# List all properties
python3 scripts/ga4-audit list

# Health checks (by name or ID)
python3 scripts/ga4-audit my-store
python3 scripts/ga4-audit 123456789

# What-changed reports
python3 scripts/ga4-what-changed my-store
python3 scripts/ga4-what-changed my-store --days 14 --format json

# Custom reports
python3 scripts/ga4-report my-store --metrics sessions,activeUsers --dimensions date --days 30
```

## Privacy & Security

- **Local-first**: All data stays on your machine. No server, no data storage, no telemetry.
- **Read-only access**: OAuth scope is `analytics.readonly`. Cannot modify your GA4 configuration.
- **Bundled OAuth**: Google-verified OAuth client ID included. No registration required.
- **Credentials stored locally**: Tokens saved to `~/.config/data-arsenal/credentials.json`, never transmitted.

See [PRIVACY.md](PRIVACY.md) for the full privacy policy.

## Go Further

**Comprehensive GA4 Audit** — The built-in `/ga4-audit` runs 20 checks using the Data API. For a **50-check audit** including Admin API settings, GTM container analysis, consent mode verification, and more — visit [audit.dataarsenal.com](https://audit.dataarsenal.com).

**Multi-Channel AI Analytics** — Data Arsenal covers GA4. If you need the same autonomous analysis across GA4 + Google Ads + Facebook Ads + Google Search Console — with built-in anomaly detection and cross-channel insights — check out [ai.trackian.com](https://ai.trackian.com).

## License

MIT
