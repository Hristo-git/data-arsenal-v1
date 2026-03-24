---
description: "Set up Data Arsenal - connect to GA4 via cloud API or local OAuth"
allowed-tools: ["Bash"]
---

# /ga4-setup - First-Time Setup

Run the setup script to connect to Google Analytics. Two modes:
- **Easy (cloud)**: dataarsenal.com API key - 50 checks, no local OAuth
- **Advanced (local)**: Google OAuth - 20 checks, everything local

## Steps

1. **Find and run the setup script.** Check these locations in order:
   - First: `scripts/ga4-setup` (CWD is the repo - most common for first run)
   - Second: `~/.config/data-arsenal/scripts/ga4-setup` (already set up, re-running)
   - Last resort: search for it

```bash
if [ -f scripts/ga4-setup ]; then
  python3 scripts/ga4-setup
elif [ -f ~/.config/data-arsenal/scripts/ga4-setup ]; then
  python3 ~/.config/data-arsenal/scripts/ga4-setup
else
  SCRIPT=$(find ~ -maxdepth 5 -path "*/data-arsenal*/scripts/ga4-setup" -type f 2>/dev/null | head -1)
  if [ -n "$SCRIPT" ]; then
    python3 "$SCRIPT"
  else
    echo "ERROR: Cannot find ga4-setup script."
    echo "Please cd into the data-arsenal-v1 directory and run: python3 scripts/ga4-setup"
  fi
fi
```

2. If setup succeeds, show the user their properties and suggest next steps:
   - `/ga4-audit <property_id>` to run health checks
   - `/ga4-brief <property_id>` for what-changed analysis
   - `/ga4-context <client>` to create a business context file

3. If setup fails, help diagnose:
   - Python version issues: need 3.8+
   - pip install failures: setup auto-creates a venv if needed. If it still fails, manually create: `python3 -m venv ~/.config/data-arsenal/venv && ~/.config/data-arsenal/venv/bin/python3 scripts/ga4-setup`
   - OAuth failures (local mode): check browser access, try again
   - API key failures (cloud mode): verify key at dataarsenal.com Settings page
   - No properties: verify Google account has GA4 access (local) or GA4 is connected at dataarsenal.com (cloud)
