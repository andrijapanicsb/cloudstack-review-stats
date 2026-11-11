"""Download merged pull requests of apache/cloudstack from the GitHub API.

Needs the GitHub command line tool `gh`, logged in (`gh auth login`).
Writes data/prs.json: one record per PR merged in the period, with its
author, merger, every review, and every comment that talks to or comes
from the test bot (blueorangutan).

Usage: python pull.py [START END]     dates as YYYY-MM-DD
"""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "prs.json")
REPO = "apache/cloudstack"
START = "2025-11-11"
END = "2026-11-11"

QUERY = """
query($q:String!,$after:String){
  search(query:$q,type:ISSUE,first:30,after:$after){
    issueCount
    pageInfo{hasNextPage endCursor}
    nodes{... on PullRequest{
      number title url createdAt mergedAt baseRefName additions deletions changedFiles
      author{login}
      mergedBy{login}
      reviewDecision
      reviews(first:100){totalCount nodes{author{login} state submittedAt url}}
      comments(first:100){totalCount nodes{author{login} createdAt url body}}
    }}
  }
}"""


def run(q, after):
    args = ["gh", "api", "graphql", "-f", "query=" + QUERY, "-f", "q=" + q]
    if after:
        args += ["-f", "after=" + after]
    for _ in range(5):
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            try:
                return json.loads(r.stdout)["data"]["search"]
            except (ValueError, KeyError, TypeError):
                pass
        sys.stderr.write("retrying: " + (r.stderr or "bad answer")[:200] + "\n")
    raise SystemExit("GitHub API call failed")


def windows(start, end, days=15):
    d = start
    while d <= end:
        e = min(d + datetime.timedelta(days=days - 1), end)
        yield d, e
        d = e + datetime.timedelta(days=1)


def main():
    start = datetime.date.fromisoformat(sys.argv[1] if len(sys.argv) > 2 else START)
    end = datetime.date.fromisoformat(sys.argv[2] if len(sys.argv) > 2 else END)
    prs = {}
    for a, b in windows(start, end):
        q = f"repo:{REPO} is:pr is:merged merged:{a}..{b}"
        after = None
        while True:
            s = run(q, after)
            if s["issueCount"] > 1000:
                raise SystemExit(f"more than 1000 PRs between {a} and {b}; use shorter windows")
            for n in s["nodes"]:
                if not n:
                    continue
                bot = []
                for c in n["comments"]["nodes"]:
                    who = (c["author"] or {}).get("login")
                    body = c["body"] or ""
                    if who == "blueorangutan" or body.strip().lower().startswith("@blueorangutan"):
                        bot.append({"author": who, "createdAt": c["createdAt"],
                                    "url": c["url"], "body": body[:200]})
                n["botComments"] = bot
                n["commentCount"] = n["comments"]["totalCount"]
                del n["comments"]
                prs[n["number"]] = n
            if not s["pageInfo"]["hasNextPage"]:
                break
            after = s["pageInfo"]["endCursor"]
        sys.stderr.write(f"{a}..{b}: {len(prs)} PRs so far\n")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"repo": REPO, "start": str(start), "end": str(end),
                   "downloaded": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                   "prs": sorted(prs.values(), key=lambda p: p["number"])}, f, indent=1)
    print(len(prs), "PRs written to", OUT)


if __name__ == "__main__":
    main()
