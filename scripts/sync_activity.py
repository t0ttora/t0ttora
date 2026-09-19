"""Publish only public, owner-authored commits; never fabricate activity."""
import html
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

OWNER = "t0ttora"
START, END = "<!-- activity:start -->", "<!-- activity:end -->"


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-workbench"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urlopen(Request("https://api.github.com/" + path, headers=headers), timeout=30) as response:
        return json.load(response)


def render(entries):
    rows = []
    for date, repo, sha, message in sorted(entries, reverse=True)[:3]:
        url = f"https://github.com/{OWNER}/{quote(repo)}/commit/{quote(sha)}"
        label = html.escape(message.splitlines()[0][:110])
        rows.append(f'<li><code>{date[:10]}</code> · <a href="{url}">{html.escape(repo)} — {label}</a></li>')
    return "<ul>\n" + "\n".join(rows) + "\n</ul>" if rows else "No public commits to display yet."


def replace_activity(source, body):
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError("README must contain exactly one activity section")
    before, rest = source.split(START)
    old, after = rest.split(END)
    return before + START + "\n" + body + "\n" + END + after


def main():
    entries = []
    page = 1
    while True:
        repos = api(f"users/{OWNER}/repos?type=owner&per_page=100&page={page}")
        for repo in repos:
            if repo["private"] or repo["fork"] or repo["archived"] or repo["name"] == OWNER:
                continue
            try:
                commits = api(f"repos/{OWNER}/{quote(repo['name'])}/commits?author={OWNER}&per_page=1")
            except HTTPError as error:
                if error.code == 409:
                    continue  # Empty repository.
                raise
            for commit in commits:
                detail = commit["commit"]
                entries.append((detail["committer"]["date"], repo["name"], commit["sha"], detail["message"]))
        if len(repos) < 100:
            break
        page += 1
    path = Path(__file__).resolve().parents[1] / "README.md"
    source = path.read_text()
    result = replace_activity(source, render(entries))
    if result != source:
        path.write_text(result)
        print("Updated public activity.")
    else:
        print("No changes.")


def self_test():
    source = "intro\n" + START + "\nold\n" + END + "\noutro"
    entries = [(f"2026-09-{day:02}T12:00:00Z", "demo", "abc", '<script>& test\nbody') for day in range(1, 5)]
    body = render(entries)
    assert body.count("<li>") == 3 and "2026-09-01" not in body
    assert "&lt;script&gt;&amp;" in body and "\nbody" not in body
    updated = replace_activity(source, body)
    assert updated.startswith("intro\n") and updated.endswith("\noutro")
    assert replace_activity(updated, body) == updated
    assert render([]) == "No public commits to display yet."
    try:
        replace_activity("missing markers", body)
    except ValueError:
        pass
    else:
        raise AssertionError("Missing markers must fail without modifying README")
    print("Self-check passed.")


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else main()
