#!/usr/bin/env python3
"""Check the archive's evidence index: every README number resolves to a committed file.

data/claims.json lists what the README states, with a status for each claim
(established, qualified, open or retired) and, for each, the committed file
that holds its number. This script checks that index against the files:

  * every quoted README passage occurs exactly once in README.md;
  * every digit in README prose lies inside an indexed passage, and every
    number in it inside exactly one, so a new number cannot enter the README
    without entering the index;
  * every evidence file is tracked by git (a fresh clone has it);
  * every needle (a verbatim excerpt) occurs in its evidence file;
  * every quoted number occurs inside one of its claim's needles;
  * no hypothesis is marked established or qualified, no retired claim still
    quotes the README, and no current claim or line of llms.txt uses
    promotional verbs such as "proves" or "memory is established";
  * every number in llms.txt (HELIOS-BRIDGE/public/llms.txt, which the site
    serves at its root) is a number the index holds, matched by value.

Matching rule, stated once here and in the index: normalize(text) turns
every run of whitespace into one space and deletes every '*' and '`'. A
needle matches when its normalized text is a substring of the normalized
file, and a needle that begins or ends with a digit must not cut a longer
number. A number is found when its value (thousands commas and a trailing %
removed) is a number token inside a matching needle; dates (YYYY-MM-DD) and
fractions (1/20) must appear literally. A version such as 7.0.0 is one number.

Usage:
  python3 tools/archive/claims_index.py --check        exit 1 and list every failure
  python3 tools/archive/claims_index.py --report       print the measured coverage as JSON
  python3 tools/archive/claims_index.py --copy FILE    check a piece of copy against the index

--copy reads any text (a product page, a post, a caption) and lists every number
it gives in digits beside the indexed claims that hold that value, marks the
numbers the index does not hold, flags promotional verbs, and names the open
claims when the text mentions memory or the hypothesis. It matches numbers by
value only: a held number still has to mean what its claim says, so read the
claims it prints. It exits 1 when a number is not held or a verb is flagged.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only
"""

import argparse
import bisect
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

INDEX = "data/claims.json"
README = "README.md"
LLMS = "HELIOS-BRIDGE/public/llms.txt"   # served at the site root by the Vite build
SCHEMA = "nrm-archive-claims/1"
STATUSES = ("established", "qualified", "open", "retired")
KINDS = ("measurement", "instrument", "software", "procedure",
         "historical-count", "hypothesis", "label")
MIN_NEEDLE = 15

# Regions of Markdown a reader does not see as prose. Each is blanked to spaces
# of equal length, so offsets in the masked text are offsets in the README.
MASKS = (
    re.compile(r"```.*?```", re.S),         # fenced code
    re.compile(r"<!--.*?-->", re.S),        # HTML comments
    re.compile(r"`[^`\n]*`"),               # inline code
    re.compile(r"</?[A-Za-z][^<>\n]*>"),    # HTML tags and their attributes
    re.compile(r"(?<=\])\([^)\s]*\)"),      # link and image targets
    re.compile(r"https?://[^\s)>\]]+"),     # bare URLs
)
LIST_MARKER = re.compile(r"^(\s*(?:\*\*)?)(\d+)\.(?=\s)")
LIST_ITEM = re.compile(r"^\s*(?:(?:\*\*)?\d+\.|[-*+])\s")
TOKEN = re.compile(r"(?<![\w.,/-])(\d{4}-\d{2}-\d{2}|\d+/\d+|\d{1,3}(?:,\d{3})+(?:\.\d+)?%?"
                   r"|\d+(?:\.\d+)*%?)(?![\w/])")
NUMBER = re.compile(r"(?<![\d.])\d[\d,]*(?:\.\d+)*")
SUBJECT = r"(?:NRM|nested resonance memory|memory|the hypothesis)"
PROMOTIONAL = re.compile(
    r"\bprov(?:e|es|ed|en|ing)\b|\bproof\b"
    r"|\b(?:confirm|validat|establish|demonstrat|verif)\w*\s+(?:that\s+)?(?:the\s+)?" + SUBJECT + r"\b"
    r"|\b" + SUBJECT + r"\s+(?:is|was|are|were|has been|have been)\s+(?:now\s+)?"
    r"(?:confirm|validat|establish|demonstrat|prov|verif)\w*",
    re.I)


def normalize(text):
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", ""))


def mask(text):
    """Blank the parts of Markdown that are not prose, keeping every offset."""
    chars = list(text)

    def blank(start, end):
        for i in range(start, end):
            if chars[i] != "\n":
                chars[i] = " "

    for pattern in MASKS:
        for match in pattern.finditer("".join(chars)):
            blank(*match.span())
    # A line-start "N." is a list marker only after a blank line or another
    # list item; inside a wrapped paragraph it is prose and is counted.
    offset, previous = 0, ""
    for line in "".join(chars).split("\n"):
        match = LIST_MARKER.match(line)
        if match and (not previous.strip() or LIST_ITEM.match(previous)):
            blank(offset + match.start(2), offset + match.end(2))
        offset, previous = offset + len(line) + 1, line
    return "".join(chars)


def prose_tokens(text):
    """[(offset, token)] for every digit token a reader sees in the prose."""
    return [(m.start(1), m.group(1)) for m in TOKEN.finditer(mask(text))]


def number_found(token, needle):
    text = normalize(needle)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}|\d+/\d+", token):
        return re.search(r"(?<![\d/])" + re.escape(token) + r"(?![\d/])", text) is not None
    value = token.replace(",", "").rstrip("%")
    return any(m.group(0).replace(",", "") == value for m in NUMBER.finditer(text))


def occurs_whole(needle, text):
    """True when the normalized needle occurs in text without cutting a longer number."""
    start = text.find(needle)
    while start != -1:
        end = start + len(needle)
        cut_left = needle[:1].isdigit() and (
            text[start - 1:start].isdigit() or
            (start >= 2 and text[start - 1] in ".," and text[start - 2].isdigit()))
        cut_right = needle[-1:].isdigit() and (
            text[end:end + 1].isdigit() or
            (text[end:end + 1] in (".", ",") and text[end + 1:end + 2].isdigit()))
        if not (cut_left or cut_right):
            return True
        start = text.find(needle, start + 1)
    return False


def tracked_files(root):
    """Tracked paths, or None when the tree is not a git checkout (a plain download)."""
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return set(out.decode("utf-8").split("\0")) - {""}


def safe_relative(path):
    pure = PurePosixPath(path)
    return bool(path) and not pure.is_absolute() and ".." not in pure.parts


def line_of(starts, offset):
    return bisect.bisect_right(starts, offset)


def check(root, index_path=INDEX, readme_path=README, llms_path=LLMS):
    """Return (errors, report). An empty error list means the index holds."""
    root = Path(root)
    errors = []
    failing = set()   # claim ids with at least one failure

    def fail(message, claim_id=None):
        errors.append(message)
        if claim_id is not None:
            failing.add(claim_id)

    try:
        index = json.loads((root / index_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"{index_path}: cannot load ({exc})"], {}
    if index.get("schema") != SCHEMA:
        fail(f"{index_path}: schema is {index.get('schema')!r}, expected {SCHEMA!r}")
    readme = (root / readme_path).read_text(encoding="utf-8")
    starts = [0] + [m.end() for m in re.finditer("\n", readme)]
    tokens = prose_tokens(readme)
    tracked = tracked_files(root)
    cache = {}

    def evidence_text(path):
        if path not in cache:
            cache[path] = normalize((root / path).read_text(encoding="utf-8", errors="replace"))
        return cache[path]

    claims = index.get("claims", [])
    non_claims = index.get("non_claims", [])
    ids = [c.get("id") for c in claims]
    for dup in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        fail(f"claim id {dup!r} is used more than once", dup)

    if non_claims:
        fail(f"{index_path}: non_claims are not accepted; every README number needs a claim "
             f"with a status and evidence ({len(non_claims)} found)")
    entries = [(c, f"claim {c.get('id')!r}", c.get("id")) for c in claims]
    spans = []   # (start, end, owner, claim id)
    for entry, owner, claim_id in entries:
        quote = entry.get("quote")
        if quote is None:
            continue
        if claim_id is None and not entry.get("reason"):
            fail(f"{owner}: a non-claim needs a reason")
        count = readme.count(quote) if quote else 0
        if count != 1:
            fail(f"{owner}: quote occurs {count} times in {readme_path} (must be exactly once)", claim_id)
            continue
        start = readme.index(quote)
        inside = [t for o, t in tokens if start <= o < start + len(quote)]
        if sorted(entry.get("numbers", [])) != sorted(inside):
            fail(f"{owner}: numbers {entry.get('numbers', [])} do not match the digits in its quote {inside}", claim_id)
        spans.append((start, start + len(quote), owner, claim_id))

    counted = {o + k for o, t in tokens for k in range(len(t))}
    masked = mask(readme)
    for match in re.finditer(r"\w+", masked):
        stray = [i for i in range(match.start(), match.end())
                 if masked[i].isnumeric() and i not in counted
                 and not any(s <= i < e for s, e, _, _ in spans)]
        if stray:
            fail(f"{readme_path}:{line_of(starts, stray[0])}: {match.group(0)!r} gives a number in a form "
                 f"the checker does not count, outside every indexed passage")
    for offset, token in tokens:
        owners = [(o, i) for s, e, o, i in spans if s <= offset < e]
        if len(owners) != 1:
            where = f"{readme_path}:{line_of(starts, offset)}"
            state = ("is in no indexed quote" if not owners else
                     f"is in {len(owners)} quotes ({', '.join(o for o, _ in owners)})")
            fail(f"{where}: the number {token!r} {state}")
            for _, claim_id in owners:
                if claim_id is not None:
                    failing.add(claim_id)

    for claim in claims:
        cid = claim.get("id")
        name = f"claim {cid!r}"
        status, kind = claim.get("status"), claim.get("kind")
        if status not in STATUSES:
            fail(f"{name}: status {status!r} is not one of {', '.join(STATUSES)}", cid)
        if kind not in KINDS:
            fail(f"{name}: kind {kind!r} is not one of {', '.join(KINDS)}", cid)
        if kind == "hypothesis" and status != "open":
            fail(f"{name}: a hypothesis can only be open, not {status!r}", cid)
        if status == "retired" and claim.get("quote") is not None:
            fail(f"{name}: a retired claim cannot quote the README (the README still states it)", cid)
        if status == "qualified" and not claim.get("scope"):
            fail(f"{name}: a qualified claim must state its scope", cid)
        if not claim.get("claim"):
            fail(f"{name}: states no claim", cid)
        for field in (("scope",) if status == "retired" else ("claim", "scope")):
            found = PROMOTIONAL.search(claim.get(field) or "")
            if found:
                fail(f"{name}: {field} uses a promotional verb ({found.group(0)!r})", cid)
        evidence = claim.get("evidence") or []
        if not evidence:
            fail(f"{name}: no evidence file", cid)
        needles = []
        for item in evidence:
            path = item.get("file", "")
            if not safe_relative(path):
                fail(f"{name}: evidence path {path!r} must be relative to the repository", cid)
                continue
            if not (root / path).is_file():
                fail(f"{name}: evidence file {path} is missing", cid)
                continue
            if tracked is not None and path not in tracked:
                fail(f"{name}: evidence file {path} is not tracked by git, so a clone will not have it", cid)
                continue
            if not item.get("needles"):
                fail(f"{name}: {path} has no needle", cid)
            for needle in item.get("needles", []):
                if len(normalize(needle).strip()) < MIN_NEEDLE:
                    fail(f"{name}: needle {needle!r} is shorter than {MIN_NEEDLE} characters", cid)
                elif not occurs_whole(normalize(needle), evidence_text(path)):
                    fail(f"{name}: needle {needle[:60]!r} is absent from {path}", cid)
                else:
                    needles.append(needle)
        for token in claim.get("numbers", []):
            if not any(number_found(token, n) for n in needles):
                fail(f"{name}: the number {token!r} is in no matching needle of its evidence", cid)

    llms = root / llms_path
    held = {t.replace(",", "").rstrip("%") for c in claims for t in c.get("numbers", [])}
    llms_tokens = 0
    if not llms.is_file():
        fail(f"{llms_path} is missing")
    else:
        text = llms.read_text(encoding="utf-8")
        if not text.startswith("# "):
            fail(f"{llms_path}: must open with a '# ' title line")
        if "claims.json" not in text:
            fail(f"{llms_path}: must link the evidence index (claims.json)")
        for line_no, line in enumerate(text.splitlines(), 1):
            found = PROMOTIONAL.search(line)
            if found:
                fail(f"{llms_path}:{line_no}: promotional verb {found.group(0)!r}")
        for _, token in prose_tokens(text):
            llms_tokens += 1
            if token.replace(",", "").rstrip("%") not in held:
                fail(f"{llms_path}: the number {token!r} is not a number the index holds")

    readme_ids = [c.get("id") for c in claims if c.get("quote") is not None]
    resolved = sum(1 for i in readme_ids if i not in failing)
    report = {
        "readme_claims": len(readme_ids),
        "readme_claims_resolving": resolved,
        "fraction_resolving": round(resolved / len(readme_ids), 4) if readme_ids else 0.0,
        "readme_digit_tokens": len(tokens),
        "readme_digit_tokens_covered": sum(1 for o, _ in tokens
                                           if sum(1 for s, e, _, _ in spans if s <= o < e) == 1),
        "claims_by_status": {s: sum(1 for c in claims if c.get("status") == s) for s in STATUSES},
        "evidence_files": len({i.get("file") for c in claims for i in c.get("evidence") or []}),
        "llms_digit_tokens": llms_tokens,
        "errors": len(errors),
    }
    return errors, report


MEMORY_WORDS = re.compile(r"\bmemory\b|\bNRM\b|nested resonance", re.I)


def check_copy(root, text, index_path=INDEX):
    """Return (problems, lines) for a piece of copy checked against the index."""
    index = json.loads((Path(root) / index_path).read_text(encoding="utf-8"))
    claims = index.get("claims", [])
    by_value = {}
    for claim in claims:
        for token in claim.get("numbers", []):
            key = token.replace(",", "").rstrip("%")
            if claim not in by_value.setdefault(key, []):
                by_value[key].append(claim)
    problems, lines, seen = 0, [], set()
    for _, token in prose_tokens(text):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", token) or token in seen:
            continue
        seen.add(token)
        held = by_value.get(token.replace(",", "").rstrip("%"), [])
        if held:
            names = "; ".join(f"{c['id']} ({c['status']})" for c in held[:4])
            more = f"; and {len(held) - 4} more" if len(held) > 4 else ""
            lines.append(f"HELD {token}: {names}{more}")
        else:
            problems += 1
            lines.append(f"NOT IN INDEX {token}: no indexed claim gives this number")
    for found in PROMOTIONAL.finditer(text):
        problems += 1
        lines.append(f"PROMOTIONAL {found.group(0)!r}: the index never uses this verb for a claim")
    if MEMORY_WORDS.search(text):
        open_ids = [c["id"] for c in claims if c.get("kind") == "hypothesis" and c.get("status") == "open"]
        lines.append("NOTE the text mentions memory or the hypothesis; the index holds these as open, "
                     "not established: " + (", ".join(open_ids) or "(none listed)"))
    return problems, lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", action="store_true", help="exit 1 when any check fails")
    parser.add_argument("--report", action="store_true", help="print the measured coverage as JSON")
    parser.add_argument("--copy", type=Path, metavar="FILE", help="check a piece of copy against the index")
    args = parser.parse_args(argv)
    if args.copy:
        try:
            copy_text = args.copy.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"cannot read {args.copy}: {exc.strerror or exc}")
            return 2
        problems, lines = check_copy(args.root, copy_text)
        print("\n".join(lines) if lines else "no numbers, no flagged verbs")
        return 1 if problems else 0
    errors, report = check(args.root)
    for error in errors:
        print(f"FAIL {error}")
    if args.report or not args.check:
        print(json.dumps(report, indent=2))
    if args.check:
        print(f"{report.get('readme_claims_resolving', 0)} of {report.get('readme_claims', 0)} README claims "
              f"resolve; {len(errors)} failure(s)")
    return 1 if (args.check and errors) else 0


if __name__ == "__main__":
    sys.exit(main())
