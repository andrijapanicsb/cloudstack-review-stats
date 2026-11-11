# Who reviews, tests and merges Apache CloudStack pull requests

## In short

This repository counts, for one year of merged pull requests in
[apache/cloudstack](https://github.com/apache/cloudstack), who approved each
one and who merged it, and whether those people worked for the same company
as the author. Every number comes with a table of the pull requests behind
it, each with a link, so anyone can check it.

It is about process, not about people. The people named here do a very large
share of the work in the project, and the data shows that too.

## Why it matters

An Apache project is meant to be independent of any single company. One
practical test of that is review: when a change is written, approved, tested
and merged by colleagues who share an employer and a deadline, a mistake has
fewer chances to be caught. A contributor from outside meets the other side
of the same situation: they need someone from that company to approve, test
and merge their work.

The numbers below show how often that happens. They do not say that any
single review was careless.

## Results

Period: pull requests merged from 11 November 2025 to 11 November 2026, all
branches, 738 pull requests opened by people (bots left out). "Inside" means
the person was a ShapeBlue employee on that day. "Outside" means everyone
else.

| Question | Inside authors (443 PRs) | Outside authors (295 PRs) |
|---|---|---|
| Approved only by inside people | 373 (84.2%) | 176 (59.7%) |
| At least one approval from outside | 66 (14.9%) | 114 (38.6%) |
| Merged by an inside person | 429 (96.8%) | 242 (82.0%) |
| Merged by the author | 89 (20.1%) | 13 (4.4%) |
| Fewer than two approvals | 31 (7.0%) | 27 (9.2%) |
| No approval at all | 4 (0.9%) | 5 (1.7%) |

Across all 738 pull requests:

- 671 (90.9%) were merged by an inside person.
- 1,513 of 1,748 approvals (86.6%) were given by inside people.

Large changes by inside authors (500 or more changed lines, 50 PRs):

- 45 (90%) had no sign-off from outside: no outside approval and an inside
  merger.
- 9 (18%) were merged with fewer than two approvals.

What the data also shows, in fairness:

- Inside people review outside work. Most outside pull requests were approved
  and merged by them.
- Outside pull requests were merged with fewer than two approvals slightly
  more often than inside ones.

### Smoke tests

The project's smoke tests run on infrastructure owned by ShapeBlue, through a
bot called blueorangutan. Anyone can ask the bot to build packages. Only
people on the bot's own list can start a test run; the bot prints that list
in its help text
([example, 14 August 2026](https://github.com/apache/cloudstack/pull/13807#issuecomment-5292305992)).
All 19 people on that list were ShapeBlue employees.

In the first 100 comments of each pull request in the period:

| Who gave the `test` command | Commands | Bot started a run |
|---|---|---|
| Inside people | 988 | 945 |
| Outside people | 9 | 4 |

The 4 runs started for an outside person were all for one former employee,
in the ten days after leaving the company. The hardware belongs to ShapeBlue
and it is ShapeBlue's right to decide who uses it; nobody else has offered
the project comparable infrastructure. The effect is that an outside
contributor cannot get a smoke-test result without asking an inside person.

## Where the evidence is

Everything is in the `evidence` folder. Each row links to the pull request,
review or comment it rests on.

| File | What it lists |
|---|---|
| `SUMMARY.md` | All figures, plus a linked table of the 50 large inside PRs |
| `all_prs.csv` | Every pull request: author, approvers (inside and outside), merger, size |
| `approvals.csv` | Every approval, with a link to the review |
| `inside_prs_approved_only_inside.csv` | The 373 inside PRs approved only by inside people |
| `large_inside_prs.csv` | The 50 large inside PRs, largest first |
| `fewer_than_two_approvals.csv` | The 58 PRs merged with fewer than two approvals |
| `self_merged.csv` | The 102 PRs merged by their own author |
| `smoke_test_commands.csv` | Every `test` command, who gave it, and whether the bot started a run |

## Details

### How it is counted

- **Approval**: a GitHub review in state "Approved" by someone other than the
  author. If a person reviewed several times, their last approve, request
  changes or dismissed review decides.
- **Inside or outside**: `affiliations.csv` lists the people counted as
  ShapeBlue employees, and the leaving date for those who left. Authors are
  judged on the day the PR was opened, approvers on the day of the review,
  mergers on the day of the merge.
- **Large**: 500 or more lines added plus removed.
- **Bots**: pull requests opened by bots and reviews by bots are left out.

### How to run it again

You need Python 3 and the GitHub command line tool, logged in.

```bash
python pull.py
```

```bash
python count.py
```

`pull.py` downloads the pull requests into `data/prs.json` (about five
minutes). `count.py` reads that file and `affiliations.csv` and rewrites the
`evidence` folder. To count a different period, pass two dates to `pull.py`.
To correct who is counted as inside, edit `affiliations.csv` and run
`count.py` again.

### What is not covered

- A plain "LGTM" comment is not counted as an approval. Some pull requests in
  `fewer_than_two_approvals.csv` may have had a second sign-off in a comment.
- Whether an approver is a committer is not checked.
- The affiliation list was put together from public profiles and from the
  repository owner's own knowledge as a former ShapeBlue employee. Two
  leaving dates are approximate and are marked so in the file. Corrections
  are welcome.
- Bot commands are read from the first 100 comments of each pull request. Six
  pull requests have more comments than that. Whether the bot started a run
  is judged from its next replies, which can be wrong when several commands
  follow each other closely.
- One pull request has more than 100 reviews; only its first 100 are read.
- The data is a snapshot taken on 11 November 2026. Running `pull.py` later
  can give slightly different numbers.
- The numbers measure who signed off. They do not measure the quality of any
  review or test.
