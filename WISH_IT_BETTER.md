# The Wish It Better Loop — v1.0

A portable standard for **compounding living apps**: small utilities that get measurably
better on a loop, in public, with the improvement history as the proof.

This file is the spec. It is not specific to Vibe Cards — Vibe Cards is just the first
implementation. Copy this file into your project, implement the five stations, add the
manifest, and you are in the network.

> **The one-line version.** A wish becomes a shipped change, the change is proven by an
> eval that could have failed, and the loop itself is amended by what the change taught.

---

## 0. Why this exists

Most side projects die in one of two ways. They ship once and rot, or they accumulate
feedback nobody can act on. Both failures are the same failure: **there is no loop, only
an event.**

A loop needs five things, and skipping any one collapses it back to an event:

| Station | Question it answers | Collapse if skipped |
|---|---|---|
| **1. WISH** | What do real users actually want? | You build what you imagine. |
| **2. TRIAGE** | Which wish is worth the next hour? | You build the loudest, not the largest. |
| **3. BUILD** | What is the smallest honest change? | You rewrite instead of improve. |
| **4. PROVE** | How do we know it is actually better? | "Better" becomes a feeling. |
| **5. LOG** | What did this teach the next loop? | You relearn the same lesson forever. |

Station 5 is what makes it **compound** instead of merely repeat.

---

## 1. The five stations

### 1. WISH — collect, cheaply, without an account

A wish costs the user seconds or it does not get made. No login, no form with eleven
fields, no "please file a detailed reproduction."

**Conformance:**
- A wish can be submitted in **under 30 seconds** with **no account**.
- At minimum: a GitHub issue template. Better: an in-app control that files it for them.
- The wish queue may be **private**. Publishing raw wishes exposes your users' workflows
  and turns triage into a popularity contest. Publish *what shipped*, not *what was asked*.

**The trap — narrative vs. list.** If the answer to a task is a list, build a list. If it
is a paragraph, do not answer it with a twelve-field form. A form that turns a sentence
into typing work is worse than no tool.

### 2. TRIAGE — rank by what the wish reveals, not by who asked

Wishes are evidence about the *shape of the gap*, not a work queue to drain.

**Conformance:**
- Every wish reaches exactly one of: **claimed · shipped · declined (with a reason) · expired**.
- A wish untouched for **K cycles auto-expires**, named in the log. A backlog you cannot
  shrink is a system optimised never to be done.
- A wish from a use case you do not serve is not an error — it is the **strongest signal
  in the queue**. It is telling you the next thing to build.

**The trap — declining silently.** A declined wish with a written reason is a contribution
to the docs. A declined wish with no reason teaches the user not to wish again.

### 3. BUILD — the smallest change that removes the cause

**Conformance:**
- Fix the **cause**, not the symptom. If a fix has been applied twice to the same class,
  the third instance is not a bug — it is the wrong layer.
- **No new tooling for a behavioural problem.** If the fix is "add a script that reminds
  us," the real fix is deleting or reordering what already exists.
- Extract a shared abstraction on the **second** instance, never the first. One instance
  is over-abstraction; five is five forks.

### 4. PROVE — an eval that could have failed

This is the station everyone skips, and it is the one that makes the standard worth
adopting. See §2 for the full bar.

### 5. LOG — write what it taught, in a form the next loop reads

**Conformance:**
- Every shipped change leaves a durable note: what broke, why the obvious fix was wrong,
  what to do next time. One paragraph is enough. A commit message can carry it.
- The note goes where the next person **will already be looking** — the code comment
  beside the fix, not a wiki nobody opens.
- **Git history is the ledger.** Not a changelog you maintain by hand: the commits, the
  issue that caused them, the eval that proved them. That trail is the compounding asset,
  and it is why this standard lives in a repo instead of a doc.

---

## 2. The eval bar — isomorphic across app types

An eval is not a test suite. A test asks *does the code still do what it did?* An eval
asks *is the thing actually better for the person using it?*

These five rules generalise to any utility — a card designer, a CLI, an API, a game, a
form builder. They are written as **failure modes**, because that is the form in which
they are actually violated.

### E1. The eval must be able to fail

If you cannot describe the observation that would have proven you wrong, you have written
a demo, not an eval. Write the failing condition **before** the fix.

### E2. Verify at the artifact the user touches — not the source you edited

A green unit test, a passing type-check, and an HTTP 200 are all compatible with a
completely broken screen. Check the built artifact, the deployed page, the rendered DOM,
the actual printed card.

> Real instance: a fix was written, committed, and confirmed three separate times while
> the deployed bundle still contained the old code. The source was right every time.

### E3. Count is not coverage

"48 of 48 cells rendered" says nothing about whether they covered 18% of the frame.
"0 findings" says nothing if the scan silently skipped the file. Always report the
denominator, and always report **what was excluded**.

> Real instance: a search returned zero matches on a file that plainly contained the
> string — the file held NUL bytes, so the tool treated it as binary and reported nothing
> rather than refusing. Absence produced by a filter is not absence.

### E4. Name the silent cap

If your eval samples, truncates, retries once, or checks only the top N — say so in the
output. A silent cap reads as full coverage and is the most expensive lie a harness tells.

### E5. Adversarial pass on anything that matters

For a security-relevant or destructive change, the default verdict is **refuted**. Have a
second pass — a different person, a different agent, a fresh reading — try to break the
claim before you accept it. Confirm only with the exact lines that make it true.

> Real instance: an audit of this very repo claimed a local server leaked arbitrary files.
> The adversarial pass did not agree on principle — it reproduced the read against a live
> instance and returned the file body. That is the difference between a finding and an
> opinion.

### The QC checklist (copy this into your PR template)

```
[ ] E1  The eval could have failed — the failing condition is written down.
[ ] E2  Verified at the artifact a user touches, not only at the source.
[ ] E3  Denominator reported; exclusions named.
[ ] E4  Any sampling / truncation / top-N is stated in the output.
[ ] E5  Security- or data-relevant? An independent pass tried to refute it.
[ ] L   The lesson is written where the next person will already be looking.
```

---

## 3. Conformance levels

Declare yours in the manifest (§4). Do not claim a level you have not earned — the whole
value of the network is that the badge means something.

| Level | Name | Requires |
|---|---|---|
| **L0** | *Adopting* | This file present; a wish channel that works; a LICENSE. |
| **L1** | *Looping* | L0 + every shipped change carries an eval meeting §2 + wishes reach a terminal state. |
| **L2** | *Networked* | L1 + a valid `wish-it-better.json` + spinoffs declare their origin + at least one amendment contributed back (§5). |

L2 is the interesting one, because it is the level at which **your improvements improve
other people's projects**.

---

## 4. The network manifest

A project joins the network by committing `wish-it-better.json` at its root. It is
deliberately tiny — a manifest nobody can fill in is a manifest nobody fills in.

```json
{
  "spec": "wish-it-better/1.0",
  "level": "L1",
  "project": "card-studio",
  "wish_channel": "https://github.com/<owner>/<repo>/issues/new?template=wish.yml",
  "origin": null,
  "spinoffs": [],
  "evals": "docs/EVALS.md",
  "amended": []
}
```

- `origin` — if this project was forked or spun off from another, name it. **This is how
  the network is traced.** A spinoff that names its origin lets improvements flow back
  along the same edge they came from.
- `spinoffs` — projects you know were spun off from this one.
- `amended` — spec amendments this project contributed (§5). This is the compounding
  ledger: a project that has amended the standard has made every other adopter better.

Machine-readable on purpose: a crawler can walk `origin`/`spinoffs` edges and render the
network without anyone maintaining a directory.

---

## 5. Amending the standard (this is the compounding part)

A standard that cannot change is a standard that rots — and it would be self-refuting for
a *wish it better* spec not to apply to itself.

**The rule: an amendment must come from a scar, not from an opinion.**

To amend:

1. **Ship something.** Amendments come from projects that shipped, not from projects that
   have theories.
2. **Show the scar.** Name the concrete failure the current spec allowed. "E3 did not
   catch X, here is X."
3. **Write the deletion first.** Prefer removing or reordering a rule over adding one. A
   spec that only grows becomes a spec nobody reads — and an unread rule enforces nothing.
4. **Open a PR against the origin repo** touching `WISH_IT_BETTER.md` and adding your
   project to `amended` in your manifest.
5. **The version bumps on substance only.** A clarification is 1.0.x. A new or deleted
   rule is 1.x. Reordered stations are 2.0.

**Amendments in force:** none yet — v1.0 is the seed. The first real scar found by an
adopter becomes v1.1, and every project on the network inherits it.

---

## 6. Security expectations for adopters

Most of these apps are small local tools, and small local tools share one dangerous
assumption. **Binding on `127.0.0.1` is not a security boundary.**

Every other process and user on the machine can reach it; any web page the user visits can
send it requests; and DNS rebinding can make an attacker's page *same-origin* with it,
which lets them read the responses too.

If your project serves HTTP locally, you must:

- **Validate the `Host` header** against an explicit allow-list. This is what stops DNS
  rebinding, and nothing else does.
- **Validate `Origin`** when present, and require a **per-run secret** on every state-
  changing or data-returning endpoint. A port number is not a secret.
- **Never join user input into a filesystem path.** Match against a known listing instead.
  `base / user_input` silently discards `base` when the input is absolute.
- **Never interpolate user input into a directive language** — shell, IPP, SQL, template.
  Validate against the grammar and refuse, rather than trying to escape.

See `SECURITY.md` for how this project implements each of these, and for how to report a
vulnerability.

---

## 7. Adopting this in your project

```
1. cp WISH_IT_BETTER.md <your-repo>/
2. Add wish-it-better.json with your level (start at L0 — it is honest).
3. Add a wish template (.github/ISSUE_TEMPLATE/wish.yml) — copy this repo's.
4. Put the §2 QC checklist in your PR template.
5. When you ship, write the lesson next to the fix.
6. When the spec fails you, amend it (§5).
```

That is the whole standard. It is short on purpose: the parts that matter are the eval bar
and the amendment clause, and everything else is scaffolding to make those two happen.

---

*Spec version 1.0 · written by **Aldrin Payopay** (Persona 500 LLC) · seeded by
[Vibe Cards](README.md) · MIT, same as the code.*

*Copy it, fork it, amend it — that is the point. If you adopt it you owe nothing; if it
fails you, you owe the next adopter an amendment (§5).*
