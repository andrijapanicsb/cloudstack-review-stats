# Who reviews, tests and merges Apache CloudStack pull requests

## In short

This repository counts, for one year of merged pull requests in
[apache/cloudstack](https://github.com/apache/cloudstack), who approved each
one and who merged it, and whether those people worked for the same
organisation as the author. Every organisation is counted in the same way.
Every number comes with a table of the pull requests behind it, each with a
link, so anyone can check it.

It is about one thing only: whether the project has a written, consistent
review and testing procedure that applies to every change in the same way.
It is not about any person, and it is not a case against any organisation.

## How organisations are shown

This page does not name organisations, because the point is the pattern and
not who it is. They are numbered in order of activity (pull requests written
plus approvals given plus merges done): Organisation 1 is the most active,
Organisation 2 the next, and so on. Which number stands for which
organisation is in `evidence/organisation_key.csv`, and the files in the
`evidence` folder use the names.

People whose employer could not be found in public sources, and people who
state that they have none, are counted together as "Individuals or not
known".

## Credit where it is due

The same data that raises the question also shows who carries the project.
In this one year, the people employed by Organisation 1:

- wrote 443 of the 738 merged pull requests (60%),
- gave 1,534 of the 1,772 approvals (87%),
- did 671 of the 738 merges (91%), including 242 of the 295 pull requests
  written by others,
- ran the only smoke-test infrastructure the project has, on their own
  hardware, and started 945 test runs on it.

Without that work there would be far fewer releases, and contributions from
everyone else would wait much longer. Nothing here should be read as saying
that this work is unwelcome or done badly. The concentration described below
is at least as much a sign that too few others review, test and provide
infrastructure as it is a sign of anything one organisation does.

## Why it matters

An Apache project is meant to be able to stand without any single
organisation. One practical test of that is review: when a change is
written, approved, tested and merged by colleagues who share an employer and
a deadline, a mistake has fewer chances to be caught. This is true of any
organisation, large or small. A contributor from elsewhere meets the other
side of the same situation: they depend on one team to approve, test and
merge their work.

The numbers show how often this happens. They do not say that any single
review was careless.

## Results

Period: pull requests merged from 11 November 2025 to 11 November 2026, all
branches, 738 pull requests opened by people (bots left out). A person
belongs to an organisation if they were employed there on that day. An
approval is either the GitHub "Approve" button or a written "LGTM".
Percentages are left out where an organisation has fewer than 20 pull
requests.

<!-- organisations:start -->
#### Who does how much

| Organisation | PRs written | Approvals given | of those, on others' PRs | Merges done | of those, of others' PRs |
|---|---|---|---|---|---|
| Organisation 1 | 443 (60%) | 1534 (87%) | 524 | 671 | 242 |
| Organisation 2 | 107 (14%) | 179 (10%) | 71 | 57 | 24 |
| Organisation 3 | 10 (1%) | 12 (1%) | 12 | 4 | 1 |
| Organisation 4 | 9 (1%) | 9 (1%) | 2 | 0 | 0 |
| Organisation 5 | 6 (1%) | 9 (1%) | 9 | 1 | 1 |
| Organisation 6 | 2 (0%) | 10 (1%) | 10 | 0 | 0 |
| Organisations 7 to 13 together | 18 (2%) | 3 (0%) | 3 | 0 | 0 |
| Individuals or not known | 143 (19%) | 16 (1%) | 16 | 5 | 3 |

#### How each organisation's own PRs were reviewed

"Own" means the same organisation as the author; "another" means anyone else.

| Organisation | PRs | Approved only by own people | At least one approval from another | Merged by own people | No sign-off from another | Merged by the author | Fewer than two approvals | No approval at all |
|---|---|---|---|---|---|---|---|---|
| Organisation 1 | 443 | 374 of 443 (84%) | 66 of 443 (15%) | 429 of 443 (97%) | 374 of 443 (84%) | 89 of 443 (20%) | 30 of 443 (7%) | 3 of 443 (1%) |
| Organisation 2 | 107 | 21 of 107 (20%) | 86 of 107 (80%) | 33 of 107 (31%) | 14 of 107 (13%) | 8 of 107 (7%) | 5 of 107 (5%) | 0 of 107 (0%) |
| Organisation 3 | 10 | 0 of 10 | 10 of 10 | 3 of 10 | 0 of 10 | 3 of 10 | 1 of 10 | 0 of 10 |
| Organisation 4 | 9 | 0 of 9 | 9 of 9 | 0 of 9 | 0 of 9 | 0 of 9 | 0 of 9 | 0 of 9 |
| Organisation 5 | 6 | 0 of 6 | 6 of 6 | 0 of 6 | 0 of 6 | 0 of 6 | 1 of 6 | 0 of 6 |
| Organisation 6 | 2 | 0 of 2 | 2 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 0 of 2 |
| Organisations 7 to 13 together | 18 | 0 of 18 | 18 of 18 | 0 of 18 | 0 of 18 | 0 of 18 | 1 of 18 | 0 of 18 |
| Individuals or not known | 143 | does not apply | 139 of 143 (97%) | does not apply | does not apply | 2 of 143 (1%) | 16 of 143 (11%) | 4 of 143 (3%) |

#### Large PRs (500 or more changed lines)

| Organisation | Large PRs | At least one approval from another | No sign-off from another | Fewer than two approvals |
|---|---|---|---|---|
| Organisation 1 | 50 | 5 of 50 (10%) | 45 of 50 (90%) | 8 of 50 (16%) |
| Organisation 2 | 18 | 10 of 18 | 5 of 18 | 1 of 18 |
| Organisation 3 | 4 | 4 of 4 | 0 of 4 | 1 of 4 |
| Organisation 4 | 3 | 3 of 3 | 0 of 3 | 0 of 3 |
| Organisation 6 | 1 | 1 of 1 | 0 of 1 | 0 of 1 |
| Organisations 7 to 13 together | 1 | 1 of 1 | 0 of 1 | 0 of 1 |
| Individuals or not known | 10 | 9 of 10 | does not apply | 1 of 10 |

#### Who approves whose PRs

Rows: who wrote the PR. Columns: who approved it. Each cell is a number of approvals.

| Written by \ approved by | Organisation 1 | Organisation 2 | Organisation 3 | Organisation 4 | Organisation 5 | Organisation 6 | Organisations 7 to 13 together | Individuals or not known |
|---|---|---|---|---|---|---|---|---|
| Organisation 1 | 1010 | 45 | 6 | 2 | 6 | 5 | 0 | 8 |
| Organisation 2 | 163 | 108 | 0 | 0 | 1 | 1 | 0 | 3 |
| Organisation 3 | 20 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Organisation 4 | 16 | 3 | 0 | 7 | 0 | 0 | 0 | 0 |
| Organisation 5 | 11 | 1 | 0 | 0 | 0 | 2 | 0 | 1 |
| Organisation 6 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Organisations 7 to 13 together | 34 | 5 | 0 | 0 | 0 | 1 | 0 | 0 |
| Individuals or not known | 277 | 16 | 6 | 0 | 2 | 1 | 3 | 4 |
<!-- organisations:end -->

How to read this:

- Review is concentrated. One organisation gives 87% of all approvals and
  does 91% of all merges. Organisations 3 to 13 together give 43 of the
  1,772 approvals (2%).
- Organisation 1 has 84% of its own PRs approved only by its own people;
  Organisation 2 has 20%. Part of that difference is arithmetic. When one
  organisation gives 87% of all approvals, nearly every PR written by anyone
  else gets one of them, while its own PRs can only get an approval from the
  remaining 13%. The figure measures how few reviewers there are elsewhere
  as much as it measures anyone's habits.
- A fairer comparison is where each organisation's approvals go.
  Organisation 2 gives 60% of its approvals to its own PRs, which are 14% of
  all PRs. Organisation 1 gives 66% to its own, which are 60% of all PRs.
  Relative to size, the smaller one stays closer to home. Reviewing mostly
  the work of one's own colleagues is what both of the two most active
  organisations do.
- Organisations 3 to 13 are small, and none of their PRs was approved only
  by their own people. With so few PRs each, that says little either way.
- Large changes get the least review from elsewhere. For the two
  organisations with the most large PRs, 45 of 50 and 5 of 18 were approved
  and merged without a sign-off from anyone in another organisation.
- The project's "two approvals" practice is followed in about 9 out of 10
  cases, whoever wrote the PR.
- Everyone outside Organisation 1 gave 238 approvals. Only 72 of them (30%)
  went to its PRs, which are 60% of the work.

### Smoke tests

The project's smoke tests run on infrastructure owned by one organisation,
through a bot called blueorangutan. Anyone can ask the bot to build
packages. Only people on the bot's own list can start a test run; the bot
prints that list in its help text
([example, 14 August 2026](https://github.com/apache/cloudstack/pull/13807#issuecomment-5292305992)).
All 19 people on that list were employed by Organisation 1.

In the first 100 comments of each pull request in the period:

<!-- smoke:start -->
| Who gave the `test` command | Commands | Bot started a run |
|---|---|---|
| Organisation 1 | 988 | 945 |
| Organisation 4 | 3 | 0 |
| Organisations 7 to 13 together | 1 | 0 |
| Individuals or not known | 5 | 4 |
<!-- smoke:end -->

The 4 runs started for someone outside Organisation 1 were all for one
former employee, in the ten days after leaving.

The hardware belongs to that organisation, and it is reasonable that its
owner decides who may use it. Nobody else has offered the project comparable
infrastructure. The effect is still that a contributor from anywhere else
cannot get a smoke-test result without asking someone from Organisation 1.
The durable answer is test capacity donated by several organisations and run
as a shared network, not a request that one organisation opens its lab to
everyone.

## Where the evidence is

Everything is in the `evidence` folder. Each row links to the pull request,
review or comment it rests on. These files use the organisations' names.

| File | What it lists |
|---|---|
| `SUMMARY.md` | All tables on this page with the organisations named, and a linked table of every large PR |
| `organisation_key.csv` | Which number on this page stands for which organisation |
| `by_organisation.csv` | The raw counts behind the tables |
| `all_prs.csv` | Every pull request with the organisation of its author, of each approver and of the merger |
| `approvals.csv` | Every approval, button or written LGTM, with the organisation of the author and of the approver, and a link |
| `approved_only_by_own_organisation.csv` | For every organisation, its PRs approved only by its own people |
| `large_prs.csv` | Every large PR, by organisation, largest first |
| `fewer_than_two_approvals.csv` | The PRs merged with fewer than two approvals |
| `self_merged.csv` | The PRs merged by their own author |
| `smoke_test_commands.csv` | Every `test` command, who gave it, their organisation, and whether the bot started a run |

## Details

### How it is counted

- **Approval**: a sign-off by someone other than the author, either a GitHub
  review in state "Approved" or a comment or review text that says "LGTM" or
  "looks good to me". The project treats both as approvals. If a person
  later pressed "Request changes" and never approved again, their earlier
  sign-off is not counted. Of the 1,772 approvals, 1,750 were given with
  the button and 22 as a written LGTM; `approvals.csv` says which is which.
- **Organisation**: `organisations.csv` lists each person, their
  organisation, the dates where they are known, and the public source.
  Authors are judged on the day the PR was opened, approvers on the day of
  the sign-off, mergers on the day of the merge.
- **Own and another**: "own" means the same organisation as the author of
  the PR; "another" means anyone else. "Individuals or not known" has no own
  organisation, so every approval a person in that group gets from someone
  else counts as coming from another.
- **No sign-off from another**: no approval from another organisation, and
  merged by someone from the author's own organisation.
- **Large**: 500 or more lines added plus removed.
- **Bots**: pull requests opened by bots and reviews by bots are left out.
- **Small organisations**: those with fewer than 10 actions in the year
  share one table row. They are listed one by one in the key.

### How to run it again

You need Python 3 and the GitHub command line tool, logged in.

```bash
python pull.py
```

```bash
python count.py
```

`pull.py` downloads the pull requests into `data/prs.json` (about five
minutes). `count.py` reads that file and `organisations.csv`, rewrites the
`evidence` folder, and rewrites the tables on this page. To count a
different period, pass two dates to `pull.py`. To correct where someone is
counted, edit `organisations.csv` and run `count.py` again. The same scripts
work for any repository: change the list and the repository name.

### What is not covered

- A written LGTM is found by searching for the words. A sentence such as
  "LGTM once the test is fixed" is counted as an approval, so the written
  count is slightly generous.
- Whether an approver is a committer is not checked.
- `organisations.csv` places 61 people, each with its source: the company
  on the person's own GitHub profile, the address on their commits or list
  mails, the company fork their pull requests come from, or, for one
  organisation, the repository owner's own knowledge as a former employee
  there together with the smoke-test bot's public list. A company fork shows
  where someone worked at that time; it is not a statement by the person.
  Everyone else, mostly people with one or two pull requests, is counted as
  "Individuals or not known". Three dates in the file are approximate and
  are marked so. Corrections are welcome.
- Comments are read from the first 100 of each pull request. Six pull
  requests have more than that. Whether the bot started a test run is judged
  from its next replies, which can be wrong when several commands follow
  each other closely.
- The data is a snapshot taken on 11 November 2026. Running `pull.py` later
  can give slightly different numbers.
- The numbers measure who signed off. They do not measure the quality of any
  review or test, and they do not measure how much code each party wrote.
