# Who reviews, tests and merges Apache CloudStack pull requests

## In short

This repository counts, for one year of merged pull requests in
[apache/cloudstack](https://github.com/apache/cloudstack), who approved each
one and who merged it, and whether those people worked for the same company
as the author. Every number comes with a table of the pull requests behind
it, each with a link, so anyone can check it.

It is about one thing only: whether the project has a written, consistent
review and testing procedure that applies to every change in the same way.
It is not about any person, and it is not a case against any company.

## Credit where it is due

The same data that raises the question also shows who carries the project.
One company employs most of the people who review, test and merge in this
project. This page does not name it, because the point is the pattern and
not the company. In this one year, the people employed there:

- wrote 443 of the 738 merged pull requests (60%),
- gave 1,532 of the 1,770 approvals (87%),
- did 671 of the 738 merges (91%), including 242 of the 295 pull requests
  written by others,
- ran the only smoke-test infrastructure the project has, on their own
  hardware, and started 945 test runs on it.

Without that work there would be far fewer releases, and outside
contributions would wait much longer. Nothing here should be read as saying
that this work is unwelcome or done badly. The concentration described below
is at least as much a sign that too few others review, test and provide
infrastructure as it is a sign of anything one company does.

## Why it matters

An Apache project is meant to be able to stand without any single company.
One practical test of that is review: when a change is written, approved,
tested and merged by colleagues who share an employer and a deadline, a
mistake has fewer chances to be caught. This would be true of any company in
that position. A contributor from outside meets the other side of the same
situation: they depend on that one team to approve, test and merge their
work.

The numbers show how often this happens. They do not say that any single
review was careless.

## Results

Period: pull requests merged from 11 November 2025 to 11 November 2026, all
branches, 738 pull requests opened by people (bots left out). "Inside" means
the person was employed by that company on that day. "Outside" means everyone
else. An approval is either the GitHub "Approve" button or a written "LGTM".

| Question | Inside authors (443 PRs) | Outside authors (295 PRs) |
|---|---|---|
| Approved only by inside people | 373 (84.2%) | 176 (59.7%) |
| At least one approval from outside | 66 (14.9%) | 115 (39.0%) |
| Merged by an inside person | 429 (96.8%) | 242 (82.0%) |
| Merged by the author | 89 (20.1%) | 13 (4.4%) |
| Fewer than two approvals | 31 (7.0%) | 25 (8.5%) |
| No approval at all | 4 (0.9%) | 4 (1.4%) |

Large changes (500 or more changed lines):

| Question | Inside authors (50 PRs) | Outside authors (37 PRs) |
|---|---|---|
| At least one approval from outside | 5 (10%) | 23 (62%) |
| No sign-off from outside: no outside approval and an inside merger | 45 (90%) | 14 (38%) |
| Fewer than two approvals | 9 (18%) | 3 (8%) |

How to read this:

- Most changes written inside one company are reviewed and merged entirely
  inside that company. For large changes it is 9 out of 10.
- The project's "two approvals" practice is followed in more than 9 out of 10
  cases for both groups. Outside pull requests fall short of it slightly more
  often than inside ones.
- Inside people review outside work: most outside pull requests were approved
  and merged by them.

### Smoke tests

The project's smoke tests run on infrastructure owned by that company, through a
bot called blueorangutan. Anyone can ask the bot to build packages. Only
people on the bot's own list can start a test run; the bot prints that list
in its help text
([example, 14 August 2026](https://github.com/apache/cloudstack/pull/13807#issuecomment-5292305992)).
All 19 people on that list were its employees.

In the first 100 comments of each pull request in the period:

| Who gave the `test` command | Commands | Bot started a run |
|---|---|---|
| Inside people | 988 | 945 |
| Outside people | 9 | 4 |

The 4 runs started for an outside person were all for one former employee,
in the ten days after leaving the company.

The hardware belongs to that company, and it is reasonable that its owner
decides who may use it. Nobody else has offered the project comparable
infrastructure. The effect is still that an outside contributor cannot get a
smoke-test result without asking an inside person. The durable answer is
test capacity donated by several organisations and run as a shared network,
not a request that one company opens its lab to everyone.

## Where the evidence is

Everything is in the `evidence` folder. Each row links to the pull request,
review or comment it rests on.

| File | What it lists |
|---|---|
| `SUMMARY.md` | All figures, with and without written LGTMs, plus a linked table of the 50 large inside PRs |
| `all_prs.csv` | Every pull request: author, approvers (inside and outside), merger, size |
| `approvals.csv` | Every approval, whether button or written LGTM, with a link |
| `inside_prs_approved_only_inside.csv` | The 373 inside PRs approved only by inside people |
| `large_inside_prs.csv` | The 50 large inside PRs, largest first |
| `fewer_than_two_approvals.csv` | The 56 PRs merged with fewer than two approvals |
| `self_merged.csv` | The 102 PRs merged by their own author |
| `smoke_test_commands.csv` | Every `test` command, who gave it, and whether the bot started a run |

## Details

### How it is counted

- **Approval**: a sign-off by someone other than the author, either a GitHub
  review in state "Approved" or a comment or review text that says "LGTM" or
  "looks good to me". The project treats both as approvals. If a person
  later pressed "Request changes" and never approved again, their earlier
  sign-off is not counted. Written LGTMs add 22 approvals to the 1,748 given
  with the button, and change no headline figure.
- **Inside or outside**: `affiliations.csv` lists the people counted as
  inside, and the leaving date for those who left. Authors are
  judged on the day the PR was opened, approvers on the day of the sign-off,
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
`count.py` again. The same scripts work for any company or any repository:
change the list and the repository name.

### What is not covered

- A written LGTM is found by searching for the words. A sentence such as
  "LGTM once the test is fixed" is counted as an approval, so the written
  count is slightly generous.
- Whether an approver is a committer is not checked.
- The affiliation list was put together from public profiles and from the
  repository owner's own knowledge as a former employee of that company. One
  leaving date is approximate and is marked so in the file. Corrections
  are welcome.
- Comments are read from the first 100 of each pull request. Six pull
  requests have more than that. Whether the bot started a test run is judged
  from its next replies, which can be wrong when several commands follow
  each other closely.
- One pull request has more than 100 reviews; only its first 100 are read.
- The data is a snapshot taken on 11 November 2026. Running `pull.py` later
  can give slightly different numbers.
- The numbers measure who signed off. They do not measure the quality of any
  review or test, and they do not measure how much code each party wrote.
