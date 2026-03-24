---
description: "Run a custom GA4 report with specified metrics and dimensions"
allowed-tools: ["Bash"]
---

# /ga4-report - Custom Report Runner

Runs a custom GA4 report with user-specified metrics and dimensions.

## Usage
`/ga4-report <property_id> [--metrics sessions,activeUsers] [--dimensions date] [--days 30] [--limit 100]`

## Steps

0. **Language preference**: Read `~/.config/data-arsenal/config.json`. If `language` is set to anything other than English, write ALL commentary, explanations, and recommendations in that language. Data labels and GA4 metric names stay in English.

1. **Parse the request**: If the user gives a natural language request instead of exact parameters, translate to GA4 metrics and dimensions:
   - "show me traffic by channel" -> `--metrics sessions,activeUsers --dimensions sessionDefaultChannelGroup`
   - "daily sessions this month" -> `--metrics sessions --dimensions date --days 30`
   - "top landing pages" -> `--metrics sessions,bounceRate --dimensions landingPage`
   - "revenue by source" -> `--metrics totalRevenue,ecommercePurchases --dimensions sessionSourceMedium`

2. **Run the report**. Find the script in order:
   - `~/.config/data-arsenal/scripts/ga4-report` (post-setup, primary)
   - `scripts/ga4-report` (CWD is the repo)
   - If neither exists, tell the user to run `/ga4-setup` first

```bash
if [ -x ~/.config/data-arsenal/scripts/ga4-report ]; then
  ~/.config/data-arsenal/scripts/ga4-report <property_id> --metrics <metrics> --dimensions <dims> --days <N> --limit <L>
elif [ -f scripts/ga4-report ]; then
  scripts/ga4-report <property_id> --metrics <metrics> --dimensions <dims> --days <N> --limit <L>
else
  echo "ERROR: Script not found. Run /ga4-setup first."
fi
```

3. **Present results** with brief interpretation if the data warrants it.

## Common Metrics
- Traffic: sessions, activeUsers, newUsers, totalUsers
- Engagement: engagementRate, bounceRate, averageSessionDuration, screenPageViews
- Conversions: conversions, eventCount
- E-commerce: totalRevenue, ecommercePurchases, purchaseRevenue

## Common Dimensions
- Time: date, hour, dayOfWeek
- Source: sessionSourceMedium, sessionDefaultChannelGroup, sessionSource
- Content: landingPage, pagePath, pageTitle
- User: deviceCategory, country, city, userAgeBracket
- Events: eventName
