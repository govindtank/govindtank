#!/usr/bin/env python3
"""Refresh README 'Recent activity' + 'Last updated' markers. Run by GitHub Action."""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ["GITHUB_TOKEN"]
API = "https://api.github.com/users/govindtank/events/public"
ME = "govindtank/govindtank"
SKIP_MSGS = ("chore: refresh", "chore(readme)")


def fetch():
    req = urllib.request.Request(API, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fmt(ev):
    repo = ev["repo"]["name"]
    if repo == ME:
        return None
    t = ev["type"]
    if t == "PushEvent":
        msgs = [c.get("message", "") for c in ev.get("payload", {}).get("commits", [])]
        msgs = [m for m in msgs if m]
        if not msgs:
            return None
        msg = msgs[-1].split("\n")[0]
        if any(msg.startswith(s) for s in SKIP_MSGS):
            return None
        return f"- pushed to `{repo}` — {msg}"
    if t == "ReleaseEvent":
        rel = ev.get("payload", {}).get("release", {})
        tag = rel.get("tag_name", "release")
        return f"- released `{tag}` in `{repo}`"
    if t == "CreateEvent" and ev.get("payload", {}).get("ref_type") == "repository":
        return f"- created new repo `{repo}`"
    return None


def main():
    seen = set()
    lines = []
    for ev in fetch():
        f = fmt(ev)
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
