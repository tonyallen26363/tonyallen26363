#!/usr/bin/env python3
"""Refresh public GitHub profile metrics in README.md."""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWNER = "tonyallen26363"
README = Path("README.md")
API = "https://api.github.com"

def get_json(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-refresh",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)

def replace_between(text, start, end, replacement):
    if start not in text or end not in text:
        raise ValueError(f"README markers missing: {start} / {end}")
    before, remainder = text.split(start, 1)
    _, after = remainder.split(end, 1)
    return before + start + "\n" + replacement.rstrip() + "\n" + end + after

def main():
    profile = get_json(f"/users/{OWNER}")
    repos = get_json(f"/users/{OWNER}/repos?per_page=100&type=owner&sort=updated")
    public_repos = profile.get("public_repos", len(repos))
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    followers = profile.get("followers", 0)
    refreshed = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    metrics = (
        f"- **Public repositories:** {public_repos}\n"
        f"- **GitHub stars across listed public repositories:** {stars}\n"
        f"- **Followers:** {followers}"
    )
    readme = README.read_text(encoding="utf-8")
    readme = replace_between(
        readme, "<!-- PROFILE_METRICS:START -->",
        "<!-- PROFILE_METRICS:END -->", metrics
    )
    readme = replace_between(
        readme, "<!-- PROFILE_REFRESHED:START -->",
        "<!-- PROFILE_REFRESHED:END -->", f"Last refreshed automatically: **{refreshed}**"
    )
    README.write_text(readme, encoding="utf-8")

if __name__ == "__main__":
    main()
