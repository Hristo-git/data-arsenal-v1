"""
Data Arsenal v1 - Shared GA4 Library
Auth, API clients, query helpers, impact scoring
"""

import os
import sys
import json
import time
from datetime import date, timedelta

# --- Venv auto-activation ---
# If a venv exists alongside the scripts, activate it so google packages are found
# regardless of which python3 the shebang resolved to.
_config_dir = os.path.expanduser('~/.config/data-arsenal')
_venv_site = os.path.join(_config_dir, 'venv', 'lib')
_venv_site_win = os.path.join(_config_dir, 'venv', 'Lib', 'site-packages')
if os.path.isdir(_venv_site_win) and _venv_site_win not in sys.path:
    # Windows: venv/Lib/site-packages (flat)
    sys.path.insert(0, _venv_site_win)
elif os.path.isdir(_venv_site):
    # macOS/Linux: venv/lib/python3.X/site-packages
    for _d in os.listdir(_venv_site):
        _sp = os.path.join(_venv_site, _d, 'site-packages')
        if os.path.isdir(_sp) and _sp not in sys.path:
            sys.path.insert(0, _sp)
            break

# Try to import Google API packages (optional for cloud mode)
_HAS_GOOGLE = False
try:
    import google.auth
    _HAS_GOOGLE = True
except ImportError:
    pass


def _require_google():
    """Exit with helpful message if Google packages aren't installed."""
    if not _HAS_GOOGLE:
        print("ERROR: Google API packages not installed.", file=sys.stderr)
        print("Fix: Re-run setup to install dependencies:", file=sys.stderr)
        print("  python3 ~/.config/data-arsenal/scripts/ga4-setup", file=sys.stderr)
        print("  OR: pip install google-auth google-auth-oauthlib google-api-python-client", file=sys.stderr)
        sys.exit(1)

# Constants
CONFIG_DIR = os.path.expanduser('~/.config/data-arsenal')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'credentials.json')
SCRIPTS_DIR = os.path.join(CONFIG_DIR, 'scripts')
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
MIN_VOLUME = 5
MAX_ROWS = 15
RELATIVE_CAP = 200

BUNDLED_CLIENT_CONFIG = {
    "installed": {
        "client_id": "1054174457426-g5crq5rgsg9op7rle4mu1mj1plg5lbe4.apps.googleusercontent.com",
        "client_secret": "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",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}


# --- Auth ---

def authenticate():
    """Run OAuth flow, save credentials. Returns Credentials object."""
    _require_google()
    from google_auth_oauthlib.flow import InstalledAppFlow

    os.makedirs(CONFIG_DIR, exist_ok=True)

    flow = InstalledAppFlow.from_client_config(BUNDLED_CLIENT_CONFIG, SCOPES)
    try:
        creds = flow.run_local_server(port=0, prompt='consent')
    except Exception:
        # Fallback for headless environments: show URL, ask user to paste code
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, _ = flow.authorization_url(prompt='consent')
        print("\n" + "="*60)
        print("Отворете този URL в браузър и разрешете достъп:")
        print("="*60)
        print(auth_url)
        print("="*60)
        code = input("\nПоставете кода от страницата тук: ").strip()
        flow.fetch_token(code=code)
        creds = flow.credentials
    save_credentials(creds)
    return creds


def load_credentials():
    """Load credentials from JSON, auto-refresh if expired. Returns Credentials or None."""
    _require_google()
    if not os.path.exists(CREDENTIALS_FILE):
        return None

    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            data = json.load(f)

        from google.oauth2.credentials import Credentials
        creds = Credentials(
            token=data.get('token'),
            refresh_token=data.get('refresh_token'),
            token_uri=data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            scopes=data.get('scopes', SCOPES)
        )

        if creds.expired and creds.refresh_token:
            import google.auth.transport.requests
            creds.refresh(google.auth.transport.requests.Request())
            save_credentials(creds)

        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}", file=sys.stderr)
        return None


def save_credentials(creds):
    """Serialize credentials to JSON file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else SCOPES
    }
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def require_credentials():
    """Load credentials or exit with helpful message."""
    creds = load_credentials()
    if not creds:
        print("Not authenticated. Run ga4-setup first.", file=sys.stderr)
        sys.exit(1)
    return creds


# --- API Clients ---

def get_data_service(creds):
    """Build GA4 Data API v1beta service."""
    from googleapiclient.discovery import build
    return build('analyticsdata', 'v1beta', credentials=creds, cache_discovery=False)


def get_admin_service(creds):
    """Build GA4 Admin API v1beta service."""
    from googleapiclient.discovery import build
    return build('analyticsadmin', 'v1beta', credentials=creds, cache_discovery=False)


def list_properties(creds):
    """List all accessible GA4 properties. Returns list of dicts."""
    admin = get_admin_service(creds)
    properties = []
    page_token = None

    while True:
        resp = admin.accountSummaries().list(pageSize=200, pageToken=page_token).execute()
        for account in resp.get('accountSummaries', []):
            account_name = account.get('displayName', 'Unknown')
            for prop in account.get('propertySummaries', []):
                prop_id = prop.get('property', '').replace('properties/', '')
                properties.append({
                    'property_id': prop_id,
                    'display_name': prop.get('displayName', 'Unknown'),
                    'account_name': account_name
                })
        page_token = resp.get('nextPageToken')
        if not page_token:
            break

    return properties


def resolve_property(creds, identifier):
    """Resolve a property ID or name to a property ID.

    Accepts:
      - Numeric ID (e.g., '407792414') - returned as-is
      - Name search (e.g., 'investclub') - fuzzy matches against property names
      - 'list' - prints all properties and exits

    Returns property_id string or exits with error.
    """
    # Pure numeric = already an ID
    if identifier.isdigit():
        return identifier

    # List all properties
    properties = list_properties(creds)

    if identifier.lower() == 'list':
        if not properties:
            print("No GA4 properties found.")
            sys.exit(1)
        print(f"\n{'Property ID':<15} {'Account':<30} {'Property Name'}")
        print(f"{'-'*15} {'-'*30} {'-'*30}")
        for p in properties:
            print(f"{p['property_id']:<15} {p['account_name'][:30]:<30} {p['display_name'][:30]}")
        sys.exit(0)

    # Search by name (case-insensitive)
    search = identifier.lower()
    matches = [p for p in properties
               if search in p['display_name'].lower()
               or search in p['account_name'].lower()]

    if not matches:
        print(f"No property matching '{identifier}'. Use 'list' to see all properties.", file=sys.stderr)
        sys.exit(1)

    if len(matches) == 1:
        p = matches[0]
        print(f"Matched: {p['display_name']} ({p['property_id']})", file=sys.stderr)
        return p['property_id']

    # Multiple matches - show them
    print(f"\nMultiple properties match '{identifier}':\n", file=sys.stderr)
    for i, p in enumerate(matches, 1):
        print(f"  {i}. {p['property_id']}  {p['display_name']} ({p['account_name']})", file=sys.stderr)
    print(f"\nUse the property ID directly, or refine your search.", file=sys.stderr)
    sys.exit(1)


# --- Query Helpers ---

def build_query(date_ranges, metrics, dimensions=None, limit=10000,
                dimension_filter=None, order_bys=None):
    """Build a GA4 Data API request body."""
    body = {
        'dateRanges': date_ranges if isinstance(date_ranges, list) else [date_ranges],
        'metrics': [{'name': m} for m in metrics],
        'limit': limit
    }
    if dimensions:
        body['dimensions'] = [{'name': d} for d in dimensions]
    if dimension_filter:
        body['dimensionFilter'] = dimension_filter
    if order_bys:
        body['orderBys'] = order_bys
    return body


def run_report(service, property_id, body, retries=2):
    """Execute GA4 report with retry logic. Returns response dict or raises."""
    from googleapiclient.errors import HttpError

    prop = property_id if property_id.startswith('properties/') else f'properties/{property_id}'
    last_error = None

    for attempt in range(retries + 1):
        try:
            return service.properties().runReport(property=prop, body=body).execute()
        except HttpError as e:
            try:
                detail = json.loads(e.content.decode())['error']['message']
            except Exception:
                detail = str(e)
            raise RuntimeError(f"GA4 API error: {detail}")
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise RuntimeError(f"GA4 API error after {retries + 1} attempts: {last_error}")


def get_property_name(creds, property_id):
    """Get display name for a property ID."""
    try:
        admin = get_admin_service(creds)
        prop = property_id if property_id.startswith('properties/') else f'properties/{property_id}'
        info = admin.properties().get(name=prop).execute()
        return info.get('displayName', property_id)
    except Exception:
        return property_id


# --- Response Parsing ---

def parse_rows(response, metrics, dimensions=None):
    """Parse GA4 response into list of dicts."""
    if not response.get('rows'):
        return []

    rows = []
    for row in response['rows']:
        d = {}
        if dimensions:
            for i, dim in enumerate(dimensions):
                try:
                    d[dim] = row['dimensionValues'][i]['value']
                except (KeyError, IndexError):
                    d[dim] = '(not set)'
        for i, metric in enumerate(metrics):
            try:
                val = row['metricValues'][i]['value']
                try:
                    d[metric] = float(val)
                except ValueError:
                    d[metric] = val
            except (KeyError, IndexError):
                d[metric] = 0.0
        rows.append(d)
    return rows


# --- Impact Scoring ---

def calculate_impact(current, previous):
    """Calculate impact score using Trackian's formula.

    impact = abs_diff * min(abs(pct_diff), RELATIVE_CAP) / 100
    """
    current = float(current)
    previous = float(previous)
    abs_diff = abs(current - previous)

    if previous == 0:
        pct_diff = 100.0 if current >= MIN_VOLUME else 0.0
    else:
        pct_diff = (current - previous) / previous * 100

    capped_pct = min(abs(pct_diff), RELATIVE_CAP)
    return abs_diff * capped_pct / 100


def format_change(current, previous, is_rate=False):
    """Format change as string with direction arrow."""
    current = float(current)
    previous = float(previous)
    diff = current - previous

    if previous == 0:
        pct = 100.0 if current > 0 else 0.0
    else:
        pct = diff / previous * 100

    if is_rate:
        sign = '+' if diff >= 0 else ''
        return f"{sign}{diff:.1f}pp", pct
    else:
        sign = '+' if diff >= 0 else ''
        return f"{sign}{diff:,.0f}", pct


def format_number(val, is_rate=False):
    """Format a number for display."""
    val = float(val)
    if is_rate:
        return f"{val:.1f}%"
    if val >= 1000000:
        return f"{val:,.0f}"
    if val >= 100:
        return f"{val:,.0f}"
    if val == int(val):
        return f"{int(val)}"
    return f"{val:.2f}"


# --- Date Helpers ---

def get_date_ranges(days=7):
    """Get current and previous date ranges for comparison.

    Returns two date range dicts for dual-range GA4 queries.
    """
    end = date.today() - timedelta(days=1)  # yesterday (today's data is incomplete)
    start = end - timedelta(days=days - 1)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    return [
        {'startDate': start.strftime('%Y-%m-%d'), 'endDate': end.strftime('%Y-%m-%d')},
        {'startDate': prev_start.strftime('%Y-%m-%d'), 'endDate': prev_end.strftime('%Y-%m-%d')}
    ], start, end, prev_start, prev_end


# --- Config ---

def load_config():
    """Load config.json, return dict."""
    config_path = os.path.join(CONFIG_DIR, 'config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save config dict to config.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_path = os.path.join(CONFIG_DIR, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


# --- Cloud Mode (dataarsenal.com API) ---

CLOUD_API_URL = 'https://audit.dataarsenal.com'


def _cloud_request(api_key, method, path, body=None):
    """Make HTTP request to dataarsenal.com API. Returns parsed JSON."""
    import urllib.request
    import urllib.error

    url = CLOUD_API_URL + path
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode('utf-8'))
            msg = err.get('error', {})
            if isinstance(msg, dict):
                msg = f"{msg.get('code', 'ERROR')}: {msg.get('message', 'Unknown error')}"
            print(f"API error: {msg}", file=sys.stderr)
        except Exception:
            print(f"API error: HTTP {e.code}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        print("Check your internet connection and try again.", file=sys.stderr)
        sys.exit(1)


def cloud_audit(api_key, property_id, ecommerce='auto', fmt='markdown'):
    """Call dataarsenal.com audit API. Returns (property_name, markdown_or_json, score, raw_data)."""
    prop = property_id if property_id.startswith('properties/') else f'properties/{property_id}'
    body = {
        'property_id': prop,
        'format': fmt,
        'has_ecommerce': ecommerce,
    }
    result = _cloud_request(api_key, 'POST', '/api/v1/audit', body)
    data = result.get('data', {})
    return (
        data.get('property_name', property_id),
        data.get('markdown', '') if fmt == 'markdown' else data,
        data.get('health_score', 0),
        data
    )


def cloud_list_properties(api_key):
    """List properties via dataarsenal.com API. Returns list of dicts."""
    result = _cloud_request(api_key, 'POST', '/api/v1/properties', {})
    data = result.get('data', {})
    props = data.get('properties', [])
    return [{'property_id': p.get('id', ''), 'display_name': p.get('display_name', '')} for p in props]


def cloud_verify(api_key):
    """Verify API key works by listing properties. Returns True/False."""
    try:
        props = cloud_list_properties(api_key)
        return len(props) >= 0  # Even empty list means auth works
    except SystemExit:
        return False
