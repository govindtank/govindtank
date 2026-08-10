#!/usr/bin/env python3
"""Refresh README 'Recent activity' + 'Last updated' markers. Run by GitHub Action.

Source: GitHub commit-search API (author:govindtank) — returns real commit
messages across all repos, which the events API omits.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ["GITHUB_TOKEN"]
SEARCH = ("https://api.github.com/search/commits"
          "?q=author:govindtank&sort=committer-date&order=desc&per_page=8")
SKIP_MSGS = ("chore: refresh", "chore(readme)", "Merge branch")


def fetch():
    req = urllib.request.Request(
        SEARCH,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github.cloak-preview+json",
            "User-Agent": "govindtank-readme/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fmt(item):
    repo = item["repository"]["full_name"]
    msg = item["commit"]["message"].split("\n")[0].strip()
    if not msg or any(msg.startswith(s) for s in SKIP_MSGS):
        return None
    date = item["commit"]["committer"]["date"][:10]
    short_repo = repo.replace("govindtank/", "")
    return f"- `{date}` **{short_repo}** — {msg[:70]}"


def main():
    data = fetch()
    seen = set()
    lines = []
    for item in data.get("items", []):
        f = fmt(item)
        if f and f not in seen:
            seen.add(f)
            lines.append(f)
        if len(lines) >= 5:
            break
    if not lines:
        lines = ["- nothing yet — check back soon"]
    body = "\n".join(lines) + "\n"

    with open("README.md") as f:
        readme = f.read()

    readme = re.sub(
        r"<!-- ACTIVITY:START -->.*?<!-- ACTIVITY:END -->",
        f"<!-- ACTIVITY:START -->\n{body}<!-- ACTIVITY:END -->",
        readme,
        flags=re.S,
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    readme = readme.replace("<!--UPDATED-->", now)

    with open("README.md", "w") as f:
        f.write(readme)
    print("refreshed:", now)


if __name__ == "__main__":
    main()
