r"""
Sports Cards desk one-command deploy.
Pushes the dashboard + modules to Keyvaniath/bpleone-sports-cards-desk.

Usage:  python DEPLOY.py
Token:  reads $env:GITHUB_TOKEN, falls back to ~/.pokemon_deploy_token.
"""
import base64
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not TOKEN:
    for p in (Path.home() / ".pokemon_deploy_token", Path.home() / ".bpleone_deploy_token"):
        if p.exists():
            TOKEN = p.read_text(encoding="utf-8").strip()
            break
if not TOKEN:
    print("ERR: no GITHUB_TOKEN env var and no ~/.pokemon_deploy_token file.")
    sys.exit(1)

OWNER = "Keyvaniath"
REPO = "bpleone-sports-cards-desk"

FILES = [
    ("streamlit_app.py", "feat: Sports Cards dashboard", None),
    ("cards_data.py",    "feat: 98-card watchlist seed", None),
    ("live_prices.py",   "feat: eBay sold-comp scraper + Browse API", None),
    ("quant_score.py",   "feat: momentum/value/scarcity/liquidity composite", None),
    ("tax_report.py",    "feat: Schedule D / Form 8949 helper", None),
    ("requirements.txt", "deps", None),
    ("README.md",        "docs", None),
    (".github_workflows_refresh.yml", "ci: weekly refresh", ".github/workflows/refresh.yml"),
]

HEADERS = {
    "Authorization": "Bearer " + TOKEN,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_sha(path):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def repo_exists():
    r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}", headers=HEADERS)
    return r.status_code == 200


def create_repo():
    r = requests.post(
        "https://api.github.com/user/repos",
        headers={**HEADERS, "Content-Type": "application/json"},
        data=json.dumps({
            "name": REPO,
            "description": "Brandon's Sports Cards trading desk — PSA-graded NBA/NFL/MLB with quant scoring.",
            "private": False,
            "auto_init": True,
            "has_issues": False,
            "has_wiki": False,
        }),
    )
    if r.status_code not in (200, 201):
        print(f"  ERR creating repo: HTTP {r.status_code} - {r.text[:200]}")
        return False
    print(f"  OK  created repo {OWNER}/{REPO}")
    return True


def push(filename, message, remote_path=None):
    p = Path(filename)
    if not p.exists():
        print("  X MISSING: " + filename)
        return
    target = remote_path or filename
    content_b64 = base64.b64encode(p.read_bytes()).decode()
    sha = get_sha(target)
    payload = {"message": message, "content": content_b64, "branch": "main"}
    if sha:
        payload["sha"] = sha
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{target}"
    r = requests.put(
        url,
        headers={**HEADERS, "Content-Type": "application/json"},
        data=json.dumps(payload),
    )
    if r.status_code in (200, 201):
        commit_sha = r.json().get("commit", {}).get("sha", "?")[:7]
        size_kb = len(p.read_bytes()) / 1024
        label = filename if not remote_path else f"{filename} -> {remote_path}"
        print(f"  OK  {label:50s} ({size_kb:6.1f} KB) -> {commit_sha}")
    elif r.status_code == 403 and target.startswith(".github/"):
        print(f"  SKIP {filename:25s} (needs PAT with `workflow` scope)")
    else:
        print(f"  ERR {filename}: HTTP {r.status_code} - {r.text[:200]}")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    print(f"Deploying from: {Path.cwd()}")
    print(f"Target: {OWNER}/{REPO}")
    print()

    if not repo_exists():
        print(f"  Repo not found, creating {OWNER}/{REPO}...")
        if not create_repo():
            sys.exit(1)

    for entry in FILES:
        if len(entry) == 3:
            push(entry[0], entry[1], entry[2])
        else:
            push(entry[0], entry[1])

    print()
    print("Done.")
    print("Next steps if not already configured:")
    print("  1. Streamlit Community Cloud: connect repo, app file = streamlit_app.py")
    print("  2. Custom domain: sports-cards.bpleone.com -> Streamlit CNAME")
    print("  3. Run `python live_prices.py` locally (or schedule GH Action) to populate live_prices.json")
