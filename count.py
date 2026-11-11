"""Count who approves, tests and merges whose pull requests.

Input : data/prs.json (written by pull.py) and affiliations.csv
Output: everything in evidence/ - a summary and one table per claim, each
        row with a link to the pull request, review or comment it rests on.

Rules:
- PRs opened by bots are left out.
- An approval is a sign-off by someone other than the PR author, given in
  one of two ways: a GitHub review in state APPROVED, or a comment or review
  text that says "LGTM" / "looks good to me". If a person later asked for
  changes with the review button and never approved again, their earlier
  sign-off is not counted.
- The summary also shows the strict count, with button approvals only.
- affiliations.csv lists the people counted as employees of the company and,
  where they left, until when. Authors are judged on the day the PR was
  opened, approvers on the day of their sign-off, mergers on the day of merge.
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


def signoffs(pr, author):
    """Return {person: (kind, date, url)} for everyone who signed off.

    kind is "button" for a GitHub approval and "lgtm" for a written LGTM.
    """
    events = []  # (time, person, what, url)
    for r in pr["reviews"]["nodes"]:
        who, when = login(r["author"]), r["submittedAt"] or ""
        if r["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            events.append((when, who, r["state"], r["url"]))
        elif r.get("lgtm"):
            events.append((when, who, "LGTM", r["url"]))
    for c in pr.get("lgtmComments", []):
        events.append((c["createdAt"], c["author"], "LGTM", c["url"]))
    result = {}
    for when, who, what, url in sorted(events, key=lambda e: e[0]):
        if who in BOTS or who == author:
            continue
        if what == "APPROVED":
            result[who] = ("button", when, url)
        elif what == "LGTM":
            result.setdefault(who, ("lgtm", when, url))
        else:  # changes requested or approval dismissed
            result.pop(who, None)
    return result


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
        so = signoffs(p, author)
        a_in = sorted(w for w, s in so.items() if inside(w, s[1]))
        a_out = sorted(w for w in so if w not in a_in)
        btn = {w for w, s in so.items() if s[0] == "button"}
        row = {
            "pr": p["number"], "url": p["url"], "opened": p["createdAt"][:10],
            "merged": p["mergedAt"][:10], "branch": p["baseRefName"],
            "lines_changed": p["additions"] + p["deletions"],
            "files_changed": p["changedFiles"],
            "author": author, "author_inside": inside(author, p["createdAt"]),
            "merged_by": merger, "merger_inside": inside(merger, p["mergedAt"]),
            "self_merged": merger == author,
            "approvals": len(so), "button_approvals": len(btn),
            "approvers_inside": " ".join(a_in), "approvers_outside": " ".join(a_out),
            "n_in": len(a_in), "n_out": len(a_out),
            "b_in": len(btn & set(a_in)), "b_out": len(btn & set(a_out)),
            "review_status_at_merge": p["reviewDecision"] or "",
            "title": p["title"],
        }
        row["outside_signoff"] = bool(a_out) or not row["merger_inside"]
        prs.append(row)
        for who, (kind, when, url) in sorted(so.items()):
            approvals.append({
                "pr": p["number"], "pr_author": author,
                "author_inside": row["author_inside"], "approver": who,
                "approver_inside": who in a_in, "date": when[:10],
                "kind": kind, "url": url,
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
                 "merger_inside", "self_merged", "approvals", "button_approvals",
                 "approvers_inside", "approvers_outside", "outside_signoff",
                 "review_status_at_merge", "title"]
    ins = [r for r in prs if r["author_inside"]]
    outs = [r for r in prs if not r["author_inside"]]
    large_in = [r for r in ins if r["lines_changed"] >= LARGE]
    large_out = [r for r in outs if r["lines_changed"] >= LARGE]

    write_csv("all_prs.csv", prs, pr_fields)
    write_csv("approvals.csv", approvals, list(approvals[0].keys()))
    write_csv("inside_prs_approved_only_inside.csv",
              [r for r in ins if r["n_in"] > 0 and r["n_out"] == 0], pr_fields)
    write_csv("large_inside_prs.csv",
              sorted(large_in, key=lambda r: -r["lines_changed"]), pr_fields)
    write_csv("fewer_than_two_approvals.csv",
              sorted((r for r in prs if r["approvals"] < 2),
                     key=lambda r: (r["approvals"], r["pr"])), pr_fields)
    write_csv("self_merged.csv", [r for r in prs if r["self_merged"]], pr_fields)
    write_csv("smoke_test_commands.csv", tests, list(tests[0].keys()))

    total = len(prs)
    groups = [("Inside authors", ins), ("Outside authors", outs),
              (f"Inside authors, {LARGE}+ lines", large_in),
              (f"Outside authors, {LARGE}+ lines", large_out)]

    def table(n_in, n_out, n_all):
        rows = [
            ("PRs", lambda g: str(len(g))),
            ("Approved only by inside people", lambda g: pct(sum(r[n_in] > 0 and r[n_out] == 0 for r in g), len(g))),
            ("At least one outside approval", lambda g: pct(sum(r[n_out] > 0 for r in g), len(g))),
            ("Merged by an inside person", lambda g: pct(sum(r["merger_inside"] for r in g), len(g))),
            ("No outside sign-off (no outside approval, inside merger)", lambda g: pct(sum(r[n_out] == 0 and r["merger_inside"] for r in g), len(g))),
            ("Merged by the author", lambda g: pct(sum(r["self_merged"] for r in g), len(g))),
            ("Fewer than two approvals", lambda g: pct(sum(r[n_all] < 2 for r in g), len(g))),
            ("No approval at all", lambda g: pct(sum(r[n_all] == 0 for r in g), len(g))),
        ]
        out = ["| Measure | " + " | ".join(g[0] for g in groups) + " |",
               "|---|" + "---|" * len(groups)]
        for name, fn in rows:
            out.append(f"| {name} | " + " | ".join(fn(g[1]) for g in groups) + " |")
        return out

    L = ["# Summary\n"]
    L.append(f"Repository: {data['repo']}. PRs merged {data['start']} to {data['end']}, "
             f"downloaded {data['downloaded']}. \"Inside\" means employed by {COMPANY} "
             f"on that day (see `affiliations.csv`).\n")
    L.append("## All merged PRs\n")
    L.append("| Measure | Result |\n|---|---|")
    L.append(f"| Merged PRs opened by people | {total} |")
    L.append(f"| Opened by inside authors | {pct(len(ins), total)} |")
    L.append(f"| Merged by an inside person | {pct(sum(r['merger_inside'] for r in prs), total)} |")
    L.append(f"| Approvals given by inside people (button or LGTM) | {pct(sum(a['approver_inside'] for a in approvals), len(approvals))} |")
    b = [a for a in approvals if a["kind"] == "button"]
    L.append(f"| Approvals given by inside people (button only) | {pct(sum(a['approver_inside'] for a in b), len(b))} |")
    L.append("\n## By who wrote the PR: button approvals and written LGTMs\n")
    L += table("n_in", "n_out", "approvals")
    L.append("\n## By who wrote the PR: button approvals only\n")
    L += table("b_in", "b_out", "button_approvals")
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
