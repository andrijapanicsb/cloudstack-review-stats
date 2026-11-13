"""The same counts as count.py, for every organisation.

Input : data/prs.json (written by pull.py) and organisations.csv
Output: evidence/ORGANISATIONS.md and evidence/by_organisation.csv

organisations.csv lists, per person, the organisation and (optionally) from
and until dates, with the public source of each entry. A person who is not in
the file, or who states no employer, is counted as "Individuals or not known".
For that group there is no "own organisation", so every approval a person in
it gets from someone else counts as coming from another party.

Approvals are counted as in count.py: the GitHub Approve button or a written
LGTM, by someone other than the author.
"""
import csv
import json
import os
from collections import Counter, defaultdict

from count import BOTS, HERE, LARGE, OUT, login, signoffs

NONE = "Individuals or not known"
SOLO = {"Independent"}          # stated: no employer
MIN_ROW = 10                    # organisations below this many actions share one row


def load():
    spans = defaultdict(list)
    with open(os.path.join(HERE, "organisations.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            spans[r["login"]].append(
                (r["from"] or "0000-00-00", r["until"] or "9999-12-31", r["organisation"]))
    return spans


SPANS = load()


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


def main():
    with open(os.path.join(HERE, "data", "prs.json"), encoding="utf-8") as f:
        data = json.load(f)

    S = defaultdict(Counter)      # per author organisation
    G = defaultdict(Counter)      # per acting organisation (approvals, merges)
    matrix = defaultdict(Counter)  # author organisation -> approver organisation
    for p in data["prs"]:
        author = login(p["author"])
        if author in BOTS:
            continue
        a_org = org(author, p["createdAt"])
        merger = login(p["mergedBy"])
        m_org = org(merger, p["mergedAt"])
        so = signoffs(p, author)
        large = p["additions"] + p["deletions"] >= LARGE
        own = other = 0
        for who, (_kind, when, _url) in so.items():
            w_org = org(who, when)
            is_own = same(a_org, author, w_org, who)
            own += is_own
            other += not is_own
            G[w_org]["approvals"] += 1
            G[w_org]["approvals_own" if is_own else "approvals_other"] += 1
            matrix[a_org][w_org] += 1
        own_merge = same(a_org, author, m_org, merger)
        G[m_org]["merges"] += 1
        G[m_org]["merges_own" if own_merge else "merges_other"] += 1
        s = S[a_org]
        s["prs"] += 1
        s["only_own"] += own > 0 and other == 0
        s["some_other"] += other > 0
        s["own_merger"] += own_merge
        s["no_other_signoff"] += other == 0 and own_merge
        s["self_merged"] += merger == author
        s["lt2"] += len(so) < 2
        s["none"] += len(so) == 0
        if large:
            s["large"] += 1
            s["large_some_other"] += other > 0
            s["large_no_other_signoff"] += other == 0 and own_merge

    names = set(S) | set(G)
    weight = {n: S[n]["prs"] + G[n]["approvals"] + G[n]["merges"] for n in names}
    shown = sorted((n for n in names if n != NONE and weight[n] >= MIN_ROW),
                   key=lambda n: -weight[n])
    small = sorted(n for n in names if n != NONE and weight[n] < MIN_ROW)
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

    def share(part, whole):
        return f"{part} ({part / whole:.0%})" if whole else "0"

    def of(part, whole):
        if not whole:
            return "-"
        return f"{part} of {whole}" + (f" ({part / whole:.0%})" if whole >= 20 else "")

    people = Counter()
    seen = set()
    for p in data["prs"]:
        for user, when in [(login(p["author"]), p["createdAt"]), (login(p["mergedBy"]), p["mergedAt"])]:
            if user and user not in BOTS and user not in seen:
                seen.add(user)
                o = org(user, when)
                people[o if o in order else SMALL] += 1

    L = ["# The same counts for every organisation\n"]
    L.append(f"Repository: {data['repo']}. PRs merged {data['start']} to {data['end']}. "
             "Who belongs where is in `organisations.csv`, with the public source of "
             "each entry. Percentages are left out where a group has fewer than 20 PRs.\n")
    L.append("## Who does how much\n")
    L.append("| Organisation | PRs written | Approvals given | of those, on others' PRs | Merges done | of those, of others' PRs |")
    L.append("|---|---|---|---|---|---|")
    for n in order:
        s, g = S[n], G[n]
        L.append(f"| {n} | {share(s['prs'], total_prs)} | {share(g['approvals'], total_app)} | "
                 f"{g['approvals_other']} | {g['merges']} | {g['merges_other']} |")
    L.append("\n## How each organisation's own PRs were reviewed\n")
    L.append("\"Own\" means the same organisation as the author; \"another\" means anyone else.\n")
    L.append("| Organisation | PRs | Approved only by own people | At least one approval from another | Merged by own people | No sign-off from another | Merged by the author | Fewer than two approvals |")
    L.append("|---|---|---|---|---|---|---|---|")
    for n in order:
        s = S[n]
        w = s["prs"]
        if n == NONE:
            L.append(f"| {n} | {w} | does not apply | {of(s['some_other'], w)} | does not apply | "
                     f"does not apply | {of(s['self_merged'], w)} | {of(s['lt2'], w)} |")
        else:
            L.append(f"| {n} | {w} | {of(s['only_own'], w)} | {of(s['some_other'], w)} | "
                     f"{of(s['own_merger'], w)} | {of(s['no_other_signoff'], w)} | "
                     f"{of(s['self_merged'], w)} | {of(s['lt2'], w)} |")
    L.append(f"\n## Large PRs ({LARGE}+ changed lines)\n")
    L.append("| Organisation | Large PRs | At least one approval from another | No sign-off from another |")
    L.append("|---|---|---|---|")
    for n in order:
        s = S[n]
        if s["large"]:
            last = "does not apply" if n == NONE else of(s["large_no_other_signoff"], s["large"])
            L.append(f"| {n} | {s['large']} | {of(s['large_some_other'], s['large'])} | {last} |")
    L.append("\n## Who approves whose PRs\n")
    L.append("Rows: who wrote the PR. Columns: who approved it. Each cell is a number of approvals.\n")
    L.append("| Written by \\ approved by | " + " | ".join(order) + " |")
    L.append("|---|" + "---|" * len(order))
    for a in order:
        L.append(f"| {a} | " + " | ".join(str(matrix[a][b]) for b in order) + " |")
    if small:
        L.append(f"\nThe {len(small)} smaller organisations are: " + ", ".join(small) + ".")
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "ORGANISATIONS.md"), "w", encoding="utf-8") as f:
        f.write(text)

    fields = ["organisation", "prs", "approvals", "approvals_own", "approvals_other",
              "merges", "merges_own", "merges_other", "only_own", "some_other",
              "own_merger", "no_other_signoff", "self_merged", "lt2", "none",
              "large", "large_some_other", "large_no_other_signoff"]
    with open(os.path.join(OUT, "by_organisation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for n in order:
            w.writerow({"organisation": n, **{k: (S[n][k] if k in S[n] else G[n][k]) for k in fields[1:]}})
    print(text)


if __name__ == "__main__":
    main()
