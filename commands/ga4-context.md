---
description: "Create or update a business context file for better GA4 analysis"
allowed-tools: ["Read", "Write", "Edit", "Bash", "WebFetch", "WebSearch", "AskUserQuestion"]
---

# /ga4-context - Website-First Context Builder

Creates a project with business context by auto-extracting information from the client's website first, then validating and filling gaps with minimal interaction.

## Usage
`/ga4-context [client_name] [url]`

## Project Structure

Projects are stored at `~/.config/data-arsenal/projects/<slug>/`. Each project contains:
- `config.json` — Structured business context (machine-readable)
- `context.md` — Narrative context with enrichment (human-readable)
- `data-quality.json` — Last audit results (written by /ga4-audit)
- `briefing-log.json` — History of past briefings (written by /ga4-brief)
- `reports/` — Generated PDFs

## Steps

### Step 0: Language check

Read `~/.config/data-arsenal/config.json`. Check the `language` key.

- If `language` is set → use that language for all commentary and questions. Data labels and GA4 metric names stay in English.
- If `language` is NOT set (first run) → output as **plain text** (NOT AskUserQuestion):
  "What language should I use? (English / Bulgarian / other)"
  Wait for the user to type their response naturally (e.g., "bg", "Bulgarian", "english").
  Interpret the response and save to `~/.config/data-arsenal/config.json` so it's never asked again.

**All subsequent output uses the chosen language.**

### Step 1: Initial info

If `client_name` and `url` were provided as arguments, use them. Otherwise output as **plain text** (NOT AskUserQuestion):

"Please provide:
1. Client/project name
2. Website URL"

Wait for the user to type both in one message. Parse the response naturally.

Slugify the project name (lowercase, hyphens, no special chars).

```bash
mkdir -p ~/.config/data-arsenal/projects/<slug>/reports
```

If `~/.config/data-arsenal/projects/<slug>/config.json` already exists, ask: "Project exists. Update existing context or start fresh?"

### Step 2: AUTO-EXTRACT from website

**Before asking any business questions**, WebFetch the homepage URL. Extract everything possible:

**Do NOT report on tracking tags (GTM, GA4, Meta Pixel, Facebook Pixel, LinkedIn, TikTok, etc.) or consent banners (CookieBot, OneTrust, etc.).** WebFetch returns raw HTML which misses dynamically-loaded tags, producing false negatives that mislead users. Skip any tracking/consent analysis entirely.

- **Business name** — from `<title>`, `og:site_name`, header logo alt text
- **Description** — from `<meta name="description">` or `og:description`
- **Business type** — ecommerce if cart/shop/product pages present, B2B if "solutions"/"services"/"consulting", lead-gen if contact forms prominent
- **Platform** — WordPress (wp-content), Shopify (cdn.shopify), WooCommerce (woocommerce), Magento, custom — from meta tags, URLs, scripts
- **Navigation sections** — from `<nav>` elements, main menu links → infer product/service categories
- **Value propositions** — hero text, tagline, "why choose us" callouts, USP sections
- **Services/products listed** — from nav or featured sections on homepage
- **Contact info** — email, phone if visible
- **Social media links** — infer active channels from footer/header social icons
- **Target market clues** — language, currency symbols, addresses, phone format, TLD (.co.uk, .de, .bg)

If the user mentioned specific pages (e.g., "services page", "about us"), WebFetch those too for additional context.

### Step 3: Present findings + ask ALL remaining questions in ONE block

Show what was extracted, then ask ALL business questions in a single plain text block. **Do NOT use AskUserQuestion** — output as plain text so the user can type a free-form response:

**IMPORTANT: Output ONLY the fields shown in the template below. Do NOT add tracking tags, pixels, consent banners, or any other fields.** WebFetch HTML is unreliable for detecting dynamically-loaded scripts — reporting their presence/absence misleads users.

```
Here's what I found from your website:

Business: [name] — [description]
Type: [ecommerce / B2B services / lead-gen]
Platform: [WordPress / Shopify / custom]
Services/Products: [list from nav]
Market: [UK / Bulgaria / etc. based on clues]
Value props: [list]

To complete the context, please answer what you can (skip any you don't know):
1. Main business goals? (traffic / leads / sales / brand awareness)
2. Key metric you're optimizing?
3. Priority marketing channel?
4. Main competitors? (names only)
5. Target SEO keywords?
6. Specific problem to investigate?
7. Peak/low seasons?
```

The user answers in one message, can skip anything. Parse their response naturally — partial answers are fine.

**For each competitor name provided:**
- WebSearch `"[competitor name] [industry/location]"` to find their URL
- WebFetch top 2-3 competitor homepages and extract:
  - Platform, pricing visibility, value propositions, key differences
- Store findings in `enrichment.competitors[]`

### Step 4: GA4 property — auto-resolve (NO question)

Do NOT ask "Which GA4 property does this use?" — instead, auto-resolve:

1. Search by business name/URL using `resolve_property()` from `_ga4_lib.py`
3. If found, show the result: "Found GA4 property: [name] ([property_id])"
4. If multiple matches, show them and let user pick
5. If not found, note it and move on — user can link later

If property found, run a quick data pull to pre-fill what we can:

```bash
# Top channels by sessions (pre-fill active_channels)
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics sessions --dimensions sessionDefaultChannelGroup --days 30

# Conversion rate and AOV if ecommerce
~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics sessions,ecommercePurchases,purchaseRevenue --days 30
```

**Always show date ranges in data output:**
```
GA4 data from last 30 days (Feb 19 - Mar 21, 2026)
```

From results:
- Pre-fill `funnel.active_channels` with channels that have >5% share
- Calculate and pre-fill `funnel.conversion_rate`
- Calculate and pre-fill `funnel.average_order_value` if purchase data exists
- If purchase events exist, confirm `business_type` as ecommerce

### Step 5: Confirm & save

Use **AskUserQuestion** (YES/NO only):
"Context ready. Save it?"

If yes, proceed to save. If no, ask what to change.

### Step 6: Save

**Write `config.json`** to `~/.config/data-arsenal/projects/<slug>/config.json`:
- Use the JSON schema from `contexts/_template.json` as the structure
- Fill in all gathered data (auto-extracted + user-provided + GA4 data)
- Initialize `what_changed` section as empty (tell user they can update it later with `/ga4-context <slug>`)
- Set `last_updated` to today's date

**Write `context.md`** to `~/.config/data-arsenal/projects/<slug>/context.md`:
- Follow the structure from `contexts/_template.md`
- Include all sections with gathered data
- Add the enrichment section with auto-detected details
- Write a brief narrative summary at the top
- Initialize "What Changed" section as empty with a note: "Update this section regularly for better analysis — run `/ga4-context <slug>` to update"

**Initialize `briefing-log.json`**:
```json
{ "briefings": [] }
```

**Legacy compatibility**: Also save context.md to `~/.config/data-arsenal/contexts/<slug>.md` so older commands can still find it.

**Suggest next steps**:
- `/ga4-audit <property>` — Run health checks (recommended first)
- `/ga4-brief <property>` — Run what-changed analysis with this context

## Property Resolution (used across all commands)

Accept property name, URL, project slug, or numeric ID:

1. If numeric → use as property_id directly
2. If matches a project slug in `~/.config/data-arsenal/projects/` → read property_id from that project's config.json
3. If neither → run `resolve_property()` from `_ga4_lib.py` to search GA4 account by name
4. If still not found → ask user to clarify

## Key Design Principles

- **Website extraction FIRST, questions SECOND** — the user validates rather than writes from scratch
- **GA4 data also pre-fills** — channels, conversion rate, AOV come from real data
- **Competitor URLs found automatically** — user provides names, we find the rest
- **Every question skippable** — partial context is infinitely better than no context
- **Max 1 AskUserQuestion call** (Step 5: confirm save) — everything else is plain text
- **No "What Changed" questions in initial setup** — initialize empty, user updates later
- **Auto-resolve GA4 property** — never ask for property_id, find it automatically
- **Always show date ranges** — whenever GA4 data is displayed, show the exact dates
- **Structured + narrative output** — config.json for machines, context.md for humans
- **No tracking/consent analysis** — WebFetch HTML misses dynamically-loaded tags; reporting presence/absence creates false confidence. Use `/ga4-audit` for tracking verification instead
