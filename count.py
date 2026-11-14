"""Count who approves, tests and merges whose pull requests, per organisation.

Input : data/prs.json (written by pull.py) and organisations.csv
Output: everything in evidence/ - a summary and one table per claim, each
        row with a link to the pull request, review or comment it rests on -
        and the tables in README.md, between the marker lines.

Every organisation is counted in the same way:
- PRs opened by bots are left out.
- An approval is a sign-off by someone other than the PR author, given in
  one of two ways: a GitHub review in state APPROVED, or a comment or review
  text that says "LGTM" / "looks good to me". If a person later asked for
  changes with the review button and never approved again, their earlier
  sign-off is not counted. Both ways count the same, as they do in the
  project.
- organisations.csv lists, per person, the organisation and (where known)
  from and until dates, with the public source of each entry. Authors are
  judged on the day the PR was opened, approvers on the day of their
  sign-off, mergers on the day of the merge.
- "Own" means the same organisation as the PR author; "another" means anyone
  else. A person who is not in the file, or who states no employer, is
  counted as "Individuals or not known". That group has no "own
  organisation": every approval a person in it gets from someone else counts
  as coming from another party.
- A large PR has 500 or more changed lines (added plus removed).

README.md does not name organisations. It calls them Organisation 1, 2, ...
in order of activity (PRs written plus approvals given plus merges done).
evidence/organisation_key.csv says which number is which organisation.
"""
import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "evidence")
LARGE = 500
BOT = "blueorangutan"
BOTS = {
    "dependabot", "asf-gitbox-commits", BOT, "codecov", "github-actions",
    "copilot-pull-request-reviewer", "Copilot", "ghost", None,
}
NONE = "Individuals or not known"
SOLO = {"Independent"}          # stated: no employer
MIN_ROW = 10                    # organisations below this many actions share one row


def login(node):
    return (node or {}).get("login")


def load_organisations():
    spans = defaultdict(list)
    with open(os.path.join(HERE, "organisations.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            spans[r["login"]].append(
                (r["from"] or "0000-00-00", r["until"] or "9999-12-31", r["organisation"]))
    return spans


SPANS = load_organisations()


def org(user, when):
    for start, end, name in SPANS.get(user, ()):
        if start <= when[:10] <= end:
            return NONE if name in SOLO else name
    return NONE


def same(org_a, user_a, org_b, user_b):
    """True when two people count as the same organisation."""
    if org_a == NONE or org_b == NONE:
        return user_a == user_b
    return org_a == org_b


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


def share(part, whole):
    return f"{part} ({part / whole:.0%})" if whole else "0"


def of(part, whole):
    """Counts always; a percentage only when the group has 20 or more."""
    if not whole:
        return "-"
    return f"{part} of {whole}" + (f" ({part / whole:.0%})" if whole >= 20 else "")


def inject(page, name, lines):
    """Replace what stands between the two marker lines called name."""
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if start not in page or end not in page:
        return page
    return (page[:page.index(start) + len(start)] + "\n" + "\n".join(lines) + "\n"
            + page[page.index(end):])


def main():
    with open(os.path.join(HERE, "data", "prs.json"), encoding="utf-8") as f:
        data = json.load(f)
    os.makedirs(OUT, exist_ok=True)

    S = defaultdict(Counter)       # per author organisation
    G = defaultdict(Counter)       # per acting organisation
    matrix = defaultdict(Counter)  # author organisation -> approver organisation
    prs, approvals, tests = [], [], []
    for p in data["prs"]:
        author = login(p["author"])
        if author in BOTS:
            continue
        a_org = org(author, p["createdAt"])
        merger = login(p["mergedBy"])
        m_org = org(merger, p["mergedAt"])
        own_merge = same(a_org, author, m_org, merger)
        so = signoffs(p, author)
        large = p["additions"] + p["deletions"] >= LARGE
        n = Counter()
        own_names, other_names = [], []
        for who, (kind, when, url) in sorted(so.items()):
            w_org = org(who, when)
            is_own = same(a_org, author, w_org, who)
            n["own" if is_own else "other"] += 1
            if kind == "button":
                n["b_own" if is_own else "b_other"] += 1
                G[w_org]["button_approvals"] += 1
            (own_names if is_own else other_names).append(
                who if is_own else f"{who} ({w_org})")
            G[w_org]["approvals"] += 1
            G[w_org]["approvals_own" if is_own else "approvals_other"] += 1
            matrix[a_org][w_org] += 1
            approvals.append({
                "pr": p["number"], "pr_author": author, "author_organisation": a_org,
                "approver": who, "approver_organisation": w_org,
                "same_organisation": is_own, "date": when[:10], "kind": kind, "url": url})
        G[m_org]["merges"] += 1
        G[m_org]["merges_own" if own_merge else "merges_other"] += 1
        s = S[a_org]
        s["prs"] += 1
        s["own_merger"] += own_merge
        s["self_merged"] += merger == author
        s["only_own"] += n["own"] > 0 and n["other"] == 0
        s["some_other"] += n["other"] > 0
        s["no_other_signoff"] += n["other"] == 0 and own_merge
        s["lt2"] += len(so) < 2
        s["none"] += len(so) == 0
        if large:
            s["large"] += 1
            s["large_some_other"] += n["other"] > 0
            s["large_no_other_signoff"] += n["other"] == 0 and own_merge
            s["large_lt2"] += len(so) < 2
        prs.append({
            "pr": p["number"], "url": p["url"], "opened": p["createdAt"][:10],
            "merged": p["mergedAt"][:10], "branch": p["baseRefName"],
            "lines_changed": p["additions"] + p["deletions"],
            "files_changed": p["changedFiles"],
            "author": author, "author_organisation": a_org,
            "merged_by": merger, "merger_organisation": m_org,
            "merged_by_own_organisation": own_merge, "self_merged": merger == author,
            "approvals": len(so), "button_approvals": n["b_own"] + n["b_other"],
            "approvers_own_organisation": " ".join(own_names),
            "approvers_other": "; ".join(other_names),
            "approved_only_by_own": n["own"] > 0 and n["other"] == 0,
            "signoff_from_another": n["other"] > 0 or not own_merge,
            "review_status_at_merge": p["reviewDecision"] or "",
            "title": p["title"]})
        # smoke-test commands and whether the bot started the run
        seq = p["botComments"]
        for i, c in enumerate(seq):
            words = c["body"].strip().lower().split()
            if c["author"] == BOT or len(words) < 2 or not words[1].startswith("test"):
                continue
            started = any(
                d["author"] == BOT and d["body"].startswith("@" + c["author"])
                and "kicked" in d["body"] for d in seq[i + 1:i + 3])
            u_org = org(c["author"], c["createdAt"])
            G[u_org]["test_commands"] += 1
            G[u_org]["test_runs"] += started
            tests.append({
                "pr": p["number"], "date": c["createdAt"][:10], "user": c["author"],
                "user_organisation": u_org,
                "command": " ".join(c["body"].split())[:80],
                "bot_started_run": started, "comment_url": c["url"]})

    # Order and numbering: by activity. Small organisations share one table row.
    names = set(S) | set(G)
    weight = {n: S[n]["prs"] + G[n]["approvals"] + G[n]["merges"] for n in names}
    shown = sorted((n for n in names if n != NONE and weight[n] >= MIN_ROW),
                   key=lambda n: (-weight[n], n))
    small = sorted((n for n in names if n != NONE and weight[n] < MIN_ROW),
                   key=lambda n: (-weight[n], n))
    numbered = shown + small
    number = {n: i + 1 for i, n in enumerate(numbered)}
    raw_S = {n: Counter(S[n]) for n in names}
    raw_G = {n: Counter(G[n]) for n in names}
    SMALL = f"{len(small)} smaller organisations"
    for n in small:
        S[SMALL].update(S[n])
        G[SMALL].update(G[n])
        for k, v in matrix.pop(n, {}).items():
            matrix[SMALL][k] += v
    for row in matrix.values():
        for n in small:
            if n in row:
                row[SMALL] += row.pop(n)
    order = shown + ([SMALL] if small else []) + [NONE]
    total_prs = sum(S[n]["prs"] for n in order)
    total_app = sum(G[n]["approvals"] for n in order)
    total_btn = sum(G[n]["button_approvals"] for n in order)

    def named(n):
        return n

    def anonymous(n):
        if n == NONE:
            return n
        if n == SMALL:
            return f"Organisations {len(shown) + 1} to {len(numbered)} together"
        return f"Organisation {number[n]}"

    def who_does(label):
        T = ["| Organisation | PRs written | Approvals given | of those, on others' PRs | Merges done | of those, of others' PRs |",
             "|---|---|---|---|---|---|"]
        for n in order:
            s, g = S[n], G[n]
            T.append(f"| {label(n)} | {share(s['prs'], total_prs)} | {share(g['approvals'], total_app)} | "
                     f"{g['approvals_other']} | {g['merges']} | {g['merges_other']} |")
        return T

    def own_review(label):
        T = ["| Organisation | PRs | Approved only by own people | At least one approval from another | Merged by own people | No sign-off from another | Merged by the author | Fewer than two approvals | No approval at all |",
             "|---|---|---|---|---|---|---|---|---|"]
        for n in order:
            s = S[n]
            w = s["prs"]
            na = "does not apply"
            T.append(
                f"| {label(n)} | {w} | {na if n == NONE else of(s['only_own'], w)} | "
                f"{of(s['some_other'], w)} | {na if n == NONE else of(s['own_merger'], w)} | "
                f"{na if n == NONE else of(s['no_other_signoff'], w)} | "
                f"{of(s['self_merged'], w)} | {of(s['lt2'], w)} | {of(s['none'], w)} |")
        return T

    def large_table(label):
        T = ["| Organisation | Large PRs | At least one approval from another | No sign-off from another | Fewer than two approvals |",
             "|---|---|---|---|---|"]
        for n in order:
            s = S[n]
            if s["large"]:
                last = "does not apply" if n == NONE else of(s["large_no_other_signoff"], s["large"])
                T.append(f"| {label(n)} | {s['large']} | {of(s['large_some_other'], s['large'])} | "
                         f"{last} | {of(s['large_lt2'], s['large'])} |")
        return T

    def matrix_table(label):
        T = ["| Written by \\ approved by | " + " | ".join(label(n) for n in order) + " |",
             "|---|" + "---|" * len(order)]
        for a in order:
            T.append(f"| {label(a)} | " + " | ".join(str(matrix[a][b]) for b in order) + " |")
        return T

    def smoke_table(label):
        T = ["| Who gave the `test` command | Commands | Bot started a run |", "|---|---|---|"]
        for n in order:
            if G[n]["test_commands"]:
                T.append(f"| {label(n)} | {G[n]['test_commands']} | {G[n]['test_runs']} |")
        return T

    OWN = "\"Own\" means the same organisation as the author; \"another\" means anyone else.\n"
    MATRIX = "Rows: who wrote the PR. Columns: who approved it. Each cell is a number of approvals.\n"

    # evidence/SUMMARY.md, with the organisations named
    L = ["# Summary\n"]
    L.append(f"Repository: {data['repo']}. PRs merged {data['start']} to {data['end']}, "
             f"downloaded {data['downloaded']}. {total_prs} merged PRs opened by people, "
             f"{total_app} approvals ({total_btn} with the button, {total_app - total_btn} "
             "as a written LGTM). Who belongs where is in `organisations.csv`, with the "
             "public source of each entry. Percentages are left out where a group has "
             "fewer than 20 PRs.\n")
    L.append("## Which number is which organisation\n")
    L.append("`README.md` uses numbers instead of names. The numbers follow activity: "
             "PRs written plus approvals given plus merges done. The same list is in "
             "`organisation_key.csv`.\n")
    L.append("| Number | Organisation | PRs written | Approvals given | Merges done |")
    L.append("|---|---|---|---|---|")
    for n in numbered:
        L.append(f"| Organisation {number[n]} | {n} | {raw_S[n]['prs']} | "
                 f"{raw_G[n]['approvals']} | {raw_G[n]['merges']} |")
    L += ["", "## Who does how much\n"] + who_does(named)
    L += ["", "## How each organisation's own PRs were reviewed\n", OWN]
    L += own_review(named)
    L += ["", f"## Large PRs ({LARGE}+ changed lines)\n"] + large_table(named)
    L += ["", "## Who approves whose PRs\n", MATRIX] + matrix_table(named)
    L += ["", "## Smoke-test commands (`@blueorangutan test`)\n",
          "Read from the first 100 comments of each PR.\n"] + smoke_table(named)
    if small:
        L.append(f"\nThe {len(small)} smaller organisations are: " + ", ".join(sorted(small)) + ".")
    rank = {n: i for i, n in enumerate(numbered + [NONE])}
    large_rows = sorted((r for r in prs if r["lines_changed"] >= LARGE),
                        key=lambda r: (rank[r["author_organisation"]], -r["lines_changed"]))
    L.append(f"\n## Every large PR ({LARGE}+ changed lines), by organisation of the author\n")
    L.append("| PR | Lines | Author | Organisation | Approvers from own organisation | Other approvers | Merged by | Sign-off from another |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in large_rows:
        L.append(f"| [#{r['pr']}]({r['url']}) | {r['lines_changed']} | {r['author']} | "
                 f"{r['author_organisation']} | {r['approvers_own_organisation'] or '-'} | "
                 f"{r['approvers_other'] or '-'} | {r['merged_by']} ({r['merger_organisation']}) | "
                 f"{'yes' if r['signoff_from_another'] else 'no'} |")
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write(text)

    # README.md, with numbers instead of names
    readme = os.path.join(HERE, "README.md")
    with open(readme, encoding="utf-8") as f:
        page = f.read()
    T = ["#### Who does how much\n"] + who_does(anonymous)
    T += ["", "#### How each organisation's own PRs were reviewed\n", OWN] + own_review(anonymous)
    T += ["", f"#### Large PRs ({LARGE} or more changed lines)\n"] + large_table(anonymous)
    T += ["", "#### Who approves whose PRs\n", MATRIX] + matrix_table(anonymous)
    page = inject(page, "organisations", T)
    page = inject(page, "smoke", smoke_table(anonymous))
    with open(readme, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)

    # the tables behind each claim
    write_csv("organisation_key.csv",
              [{"number": f"Organisation {number[n]}", "organisation": n,
                "prs_written": raw_S[n]["prs"], "approvals_given": raw_G[n]["approvals"],
                "merges_done": raw_G[n]["merges"]} for n in numbered],
              ["number", "organisation", "prs_written", "approvals_given", "merges_done"])
    s_fields = ["prs", "only_own", "some_other", "own_merger", "no_other_signoff",
                "self_merged", "lt2", "none", "large", "large_some_other",
                "large_no_other_signoff", "large_lt2"]
    g_fields = ["approvals", "button_approvals", "approvals_own", "approvals_other",
                "merges", "merges_own", "merges_other", "test_commands", "test_runs"]
    with open(os.path.join(OUT, "by_organisation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["organisation"] + s_fields + g_fields)
        for n in order:
            w.writerow([n] + [S[n][k] for k in s_fields] + [G[n][k] for k in g_fields])
    pr_fields = list(prs[0].keys())
    by_org = sorted(prs, key=lambda r: (rank[r["author_organisation"]], r["pr"]))
    write_csv("all_prs.csv", by_org, pr_fields)
    write_csv("approvals.csv", approvals, list(approvals[0].keys()))
    write_csv("approved_only_by_own_organisation.csv",
              [r for r in by_org if r["approved_only_by_own"]
               and r["author_organisation"] != NONE], pr_fields)
    write_csv("large_prs.csv", large_rows, pr_fields)
    write_csv("fewer_than_two_approvals.csv",
              sorted((r for r in prs if r["approvals"] < 2),
                     key=lambda r: (r["approvals"], r["pr"])), pr_fields)
    write_csv("self_merged.csv", [r for r in by_org if r["self_merged"]], pr_fields)
    write_csv("smoke_test_commands.csv", tests, list(tests[0].keys()))
    print(text[: text.index("## Every large PR")])


if __name__ == "__main__":
    main()
