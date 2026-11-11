"""Count who approves, tests and merges whose pull requests.

Input : data/prs.json (written by pull.py) and affiliations.csv
Output: everything in evidence/ - a summary and one table per claim, each
        row with a link to the pull request, review or comment it rests on.

Rules:
- PRs opened by bots are left out.
- An approval is a GitHub review in state APPROVED by someone other than the
  PR author. If the same person reviewed more than once, their last
  approve / request-changes / dismissed review decides. A plain "LGTM"
  comment is not counted.
- affiliations.csv lists the people counted as employees of the company and,
  where they left, until when. Authors are judged on the day the PR was
  opened, approvers on the day of their review, mergers on the day of merge.
- A large PR has 500 or more changed lines (added plus removed).
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "evidence")
COMPANY = "ShapeBlue"
LARGE = 500
BOT = "blueorangutan"
BOTS = {
    "dependabot", "asf-gitbox-commits", BOT, "codecov", "github-actions",
    "copilot-pull-request-reviewer", "Copilot", "ghost", None,
}


def login(node):
    return (node or {}).get("login")


def load_affiliations():
    until = {}
    with open(os.path.join(HERE, "affiliations.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            until[row["login"]] = row["until"] or "9999-12-31"
    return until


UNTIL = load_affiliations()


def inside(user, when):
    return user in UNTIL and when[:10] <= UNTIL[user]


def approvals_of(pr, author):
    """Last decisive review per reviewer; return those that are approvals."""
    last = {}
    for r in sorted(pr["reviews"]["nodes"], key=lambda r: r["submittedAt"] or ""):
        who = login(r["author"])
        if who in BOTS or who == author:
            continue
        if r["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            last[who] = r
    return {w: r for w, r in last.items() if r["state"] == "APPROVED"}


def write_csv(name, rows, fields):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def pct(part, whole):
    return f"{part} of {whole} ({part / whole:.1%})" if whole else "0 of 0"


def main():
    with open(os.path.join(HERE, "data", "prs.json"), encoding="utf-8") as f:
        data = json.load(f)
    os.makedirs(OUT, exist_ok=True)

    prs, approvals, tests = [], [], []
    for p in data["prs"]:
        author = login(p["author"])
        if author in BOTS:
            continue
        merger = login(p["mergedBy"])
        appr = approvals_of(p, author)
        a_in = sorted(w for w, r in appr.items() if inside(w, r["submittedAt"]))
        a_out = sorted(w for w in appr if w not in a_in)
        row = {
            "pr": p["number"], "url": p["url"], "opened": p["createdAt"][:10],
            "merged": p["mergedAt"][:10], "branch": p["baseRefName"],
            "lines_changed": p["additions"] + p["deletions"],
            "files_changed": p["changedFiles"],
            "author": author, "author_inside": inside(author, p["createdAt"]),
            "merged_by": merger, "merger_inside": inside(merger, p["mergedAt"]),
            "self_merged": merger == author,
            "approvals": len(appr),
            "approvers_inside": " ".join(a_in), "approvers_outside": " ".join(a_out),
            "n_in": len(a_in), "n_out": len(a_out),
            "review_status_at_merge": p["reviewDecision"] or "",
            "title": p["title"],
        }
        row["outside_signoff"] = bool(a_out) or not row["merger_inside"]
        prs.append(row)
        for who, r in sorted(appr.items()):
            approvals.append({
                "pr": p["number"], "pr_author": author,
                "author_inside": row["author_inside"], "approver": who,
                "approver_inside": who in a_in, "date": r["submittedAt"][:10],
                "review_url": r["url"],
            })
        # smoke-test commands and whether the bot started the run
        seq = p["botComments"]
        for i, c in enumerate(seq):
            words = c["body"].strip().lower().split()
            if c["author"] == BOT or len(words) < 2 or not words[1].startswith("test"):
                continue
            started = any(
                d["author"] == BOT and d["body"].startswith("@" + c["author"])
                and "kicked" in d["body"] for d in seq[i + 1:i + 3])
            tests.append({
                "pr": p["number"], "date": c["createdAt"][:10], "user": c["author"],
                "user_inside": inside(c["author"], c["createdAt"]),
                "command": " ".join(c["body"].split())[:80],
                "bot_started_run": started, "comment_url": c["url"],
            })

    pr_fields = ["pr", "url", "opened", "merged", "branch", "lines_changed",
                 "files_changed", "author", "author_inside", "merged_by",
                 "merger_inside", "self_merged", "approvals", "approvers_inside",
                 "approvers_outside", "outside_signoff", "review_status_at_merge",
                 "title"]
    ins = [r for r in prs if r["author_inside"]]
    outs = [r for r in prs if not r["author_inside"]]
    large_in = [r for r in ins if r["lines_changed"] >= LARGE]
    few = [r for r in prs if r["approvals"] < 2]
    only_inside = [r for r in ins if r["n_in"] > 0 and r["n_out"] == 0]

    write_csv("all_prs.csv", prs, pr_fields)
    write_csv("approvals.csv", approvals, list(approvals[0].keys()))
    write_csv("inside_prs_approved_only_inside.csv", only_inside, pr_fields)
    write_csv("large_inside_prs.csv",
              sorted(large_in, key=lambda r: -r["lines_changed"]), pr_fields)
    write_csv("fewer_than_two_approvals.csv",
              sorted(few, key=lambda r: (r["approvals"], r["pr"])), pr_fields)
    write_csv("self_merged.csv", [r for r in prs if r["self_merged"]], pr_fields)
    write_csv("smoke_test_commands.csv", tests, list(tests[0].keys()))
    total = len(prs)
    n_appr = len(approvals)
    L = []
    L.append(f"# Summary\n")
    L.append(f"Repository: {data['repo']}. PRs merged {data['start']} to {data['end']}, "
             f"downloaded {data['downloaded']}. \"Inside\" means employed by {COMPANY} "
             f"on that day (see `affiliations.csv`).\n")
    L.append("## All merged PRs\n")
    L.append("| Measure | Result |\n|---|---|")
    L.append(f"| Merged PRs opened by people | {total} |")
    L.append(f"| Opened by inside authors | {pct(len(ins), total)} |")
    L.append(f"| Merged by an inside person | {pct(sum(r['merger_inside'] for r in prs), total)} |")
    L.append(f"| Approvals given by inside people | {pct(sum(a['approver_inside'] for a in approvals), n_appr)} |")
    L.append("\n## By who wrote the PR\n")
    groups = [("Inside authors", ins), ("Outside authors", outs),
              (f"Inside authors, {LARGE}+ changed lines", large_in)]
    L.append("| Measure | " + " | ".join(g[0] for g in groups) + " |")
    L.append("|---|" + "---|" * len(groups))
    measures = [
        ("PRs", lambda g: str(len(g))),
        ("Approved only by inside people", lambda g: pct(sum(r["n_in"] > 0 and r["n_out"] == 0 for r in g), len(g))),
        ("At least one outside approval", lambda g: pct(sum(r["n_out"] > 0 for r in g), len(g))),
        ("Merged by an inside person", lambda g: pct(sum(r["merger_inside"] for r in g), len(g))),
        ("No outside sign-off (no outside approval, inside merger)", lambda g: pct(sum(not r["outside_signoff"] for r in g), len(g))),
        ("Merged by the author", lambda g: pct(sum(r["self_merged"] for r in g), len(g))),
        ("Fewer than two approvals", lambda g: pct(sum(r["approvals"] < 2 for r in g), len(g))),
        ("No approval at all", lambda g: pct(sum(r["approvals"] == 0 for r in g), len(g))),
    ]
    for name, fn in measures:
        L.append(f"| {name} | " + " | ".join(fn(g[1]) for g in groups) + " |")
    L.append("\n## Smoke-test commands (`@blueorangutan test`)\n")
    L.append("Read from the first 100 comments of each PR.\n")
    L.append("| Who gave the command | Commands | Bot started a run |\n|---|---|---|")
    for label, sel in (("Inside people", True), ("Outside people", False)):
        g = [t for t in tests if t["user_inside"] == sel]
        L.append(f"| {label} | {len(g)} | {sum(t['bot_started_run'] for t in g)} |")
    L.append(f"\n## Large PRs by inside authors ({LARGE}+ changed lines)\n")
    L.append("| PR | Lines | Author | Inside approvers | Outside approvers | Merged by | Outside sign-off |\n|---|---|---|---|---|---|---|")
    for r in sorted(large_in, key=lambda r: -r["lines_changed"]):
        L.append(f"| [#{r['pr']}]({r['url']}) | {r['lines_changed']} | {r['author']} | "
                 f"{r['approvers_inside'] or '-'} | {r['approvers_outside'] or '-'} | "
                 f"{r['merged_by']} | {'yes' if r['outside_signoff'] else 'no'} |")
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text[: text.index("## Large PRs")])


if __name__ == "__main__":
    main()
