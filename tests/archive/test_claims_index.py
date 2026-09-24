"""The evidence index holds: every README number resolves to a committed file.

Runs under unittest (the archive-health workflow) and pytest alike.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


claims_index = module("archive_claims_index", "tools/archive/claims_index.py")

README = "# Lab\n\nWe ran 60 runs at 4,194,304 particles. See [the file](data/result.md).\n"
RESULT = "The grid holds 60 runs at 4194304 particles each, 24 epochs per run.\n"
LLMS = "# Lab\n\n> Evidence index: [claims.json](claims.json). The grid has 60 runs.\n"


def claim(**overrides):
    base = {
        "id": "grid-runs", "status": "established", "kind": "measurement",
        "claim": "The grid has 60 runs of 4,194,304 particles.", "scope": "",
        "quote": "We ran 60 runs at 4,194,304 particles.", "numbers": ["60", "4,194,304"],
        "evidence": [{"file": "data/result.md", "needles": ["The grid holds 60 runs at 4194304 particles"]}],
    }
    base.update(overrides)
    return base


class MiniArchive:
    """A throwaway archive: README, one evidence file, an index and an llms.txt."""

    def __init__(self, claims, readme=README, result=RESULT, llms=LLMS, non_claims=()):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "data").mkdir()
        (self.root / "README.md").write_text(readme, encoding="utf-8")
        if result is not None:
            (self.root / "data/result.md").write_text(result, encoding="utf-8")
        (self.root / claims_index.LLMS).parent.mkdir(parents=True, exist_ok=True)
        (self.root / claims_index.LLMS).write_text(llms, encoding="utf-8")
        index = {"schema": claims_index.SCHEMA, "claims": list(claims), "non_claims": list(non_claims)}
        (self.root / "data/claims.json").write_text(json.dumps(index), encoding="utf-8")

    def errors(self):
        return claims_index.check(self.root)[0]

    def close(self):
        self.directory.cleanup()


class CommittedIndexTests(unittest.TestCase):
    def test_every_readme_number_resolves_to_a_committed_file(self):
        errors, report = claims_index.check(ROOT)
        self.assertEqual(errors, [], "\n".join(errors))
        self.assertGreater(report["readme_claims"], 0)
        self.assertEqual(report["readme_claims_resolving"], report["readme_claims"])
        self.assertEqual(report["readme_digit_tokens_covered"], report["readme_digit_tokens"])


class CheckerFailsWhenItShouldTests(unittest.TestCase):
    def run_case(self, claims, **kwargs):
        archive = MiniArchive(claims, **kwargs)
        try:
            return archive.errors()
        finally:
            archive.close()

    def test_a_clean_index_passes(self):
        self.assertEqual(self.run_case([claim()]), [])

    def test_a_missing_evidence_file_fails(self):
        errors = self.run_case([claim()], result=None)
        self.assertTrue(any("data/result.md is missing" in e for e in errors), errors)

    def test_a_number_absent_from_the_evidence_fails(self):
        errors = self.run_case([claim()], result="The grid holds 59 runs at 4194304 particles each.\n")
        self.assertTrue(any("absent from data/result.md" in e for e in errors), errors)
        self.assertTrue(any("'60' is in no matching needle" in e for e in errors), errors)

    def test_a_needle_that_omits_a_quoted_number_fails(self):
        evidence = [{"file": "data/result.md", "needles": ["at 4194304 particles each"]}]
        errors = self.run_case([claim(evidence=evidence)])
        self.assertTrue(any("'60' is in no matching needle" in e for e in errors), errors)

    def test_a_readme_number_outside_every_quote_fails(self):
        readme = README + "\nA later edit adds 17 new runs.\n"
        errors = self.run_case([claim()], readme=readme)
        self.assertTrue(any("'17' is in no indexed quote" in e for e in errors), errors)

    def test_a_quote_that_left_the_readme_fails(self):
        errors = self.run_case([claim(quote="We ran 61 runs at 4,194,304 particles.")])
        self.assertTrue(any("occurs 0 times" in e for e in errors), errors)

    def test_numbers_must_match_the_digits_in_the_quote(self):
        errors = self.run_case([claim(numbers=["60"])])
        self.assertTrue(any("do not match the digits" in e for e in errors), errors)

    def test_a_hypothesis_cannot_be_established(self):
        errors = self.run_case([claim(kind="hypothesis")])
        self.assertTrue(any("a hypothesis can only be open" in e for e in errors), errors)

    def test_promotional_verbs_are_refused(self):
        errors = self.run_case([claim(claim="The grid proves nested resonance memory.")])
        self.assertTrue(any("promotional verb" in e for e in errors), errors)

    def test_non_claims_are_refused(self):
        readme = README + "\nCopyright 2026.\n"
        errors = self.run_case([claim()], readme=readme,
                               non_claims=[{"quote": "Copyright 2026.", "numbers": ["2026"], "reason": "a year"}])
        self.assertTrue(any("non_claims are not accepted" in e for e in errors), errors)

    def test_a_number_in_an_uncounted_form_fails(self):
        for extra in ("It ran -3 times.", "A 10x speedup.", "Half is ½.", "Seen 2nd."):
            errors = self.run_case([claim()], readme=README + "\n" + extra + "\n")
            self.assertTrue(any("in a form the checker does not count" in e for e in errors), (extra, errors))

    def test_a_comparison_sign_does_not_hide_a_number(self):
        errors = self.run_case([claim()], readme=README + "\nWhen a < b, 17 runs pass; b > a.\n")
        self.assertTrue(any("'17' is in no indexed quote" in e for e in errors), errors)

    def test_a_needle_that_cuts_a_longer_number_fails(self):
        evidence = [{"file": "data/result.md", "needles": ["60 runs at 4194304 particles each"]}]
        errors = self.run_case([claim(evidence=evidence)],
                               result="The grid holds 160 runs at 4194304 particles each.\n")
        self.assertTrue(any("absent from data/result.md" in e for e in errors), errors)

    def test_passive_promotion_is_refused(self):
        for text in ("NRM is established by the grid.", "The grid establishes that memory holds.",
                     "Memory was confirmed in the chamber."):
            errors = self.run_case([claim(claim=text)])
            self.assertTrue(any("promotional verb" in e for e in errors), (text, errors))

    def test_a_retired_claim_cannot_quote_the_readme(self):
        errors = self.run_case([claim(status="retired")])
        self.assertTrue(any("a retired claim cannot quote the README" in e for e in errors), errors)

    def test_llms_numbers_must_be_held_by_the_index(self):
        errors = self.run_case([claim()], llms=LLMS + "It also has 99 runs.\n")
        self.assertTrue(any("'99' is not a number the index holds" in e for e in errors), errors)

    def test_an_untracked_evidence_file_fails_in_a_git_checkout(self):
        archive = MiniArchive([claim()])
        try:
            git = ["git", "-C", str(archive.root)]
            subprocess.run(git + ["init", "-q"], check=True)
            subprocess.run(git + ["add", "README.md", "data/claims.json", claims_index.LLMS], check=True)
            errors = archive.errors()
            self.assertTrue(any("not tracked by git" in e for e in errors), errors)
            subprocess.run(git + ["add", "data/result.md"], check=True)
            self.assertEqual(archive.errors(), [])
        finally:
            archive.close()


class CopyCheckTests(unittest.TestCase):
    def test_copy_numbers_are_held_or_flagged_and_promotion_is_refused(self):
        archive = MiniArchive([claim()])
        try:
            problems, lines = claims_index.check_copy(
                archive.root, "Our lab ran 60 runs and 99 people agree: this proves memory.")
        finally:
            archive.close()
        self.assertEqual(problems, 2, lines)
        self.assertTrue(any(line.startswith("HELD 60: grid-runs (established)") for line in lines), lines)
        self.assertTrue(any(line.startswith("NOT IN INDEX 99") for line in lines), lines)
        self.assertTrue(any(line.startswith("PROMOTIONAL 'proves'") for line in lines), lines)
        self.assertTrue(any(line.startswith("NOTE") for line in lines), lines)

    def test_copy_that_only_restates_held_numbers_passes(self):
        archive = MiniArchive([claim()])
        try:
            problems, _ = claims_index.check_copy(archive.root, "Sixty is 60, written on 2026-09-23.")
        finally:
            archive.close()
        self.assertEqual(problems, 0)


class MaskingTests(unittest.TestCase):
    def test_code_links_urls_tags_and_list_markers_are_not_prose(self):
        text = ("1. Run `python3 run.py --seed 42` from [cycle 7](a/cycle7.md) at https://x.io/v2 "
                "<img width=\"45%\">\n**2. HARDWARE:** 3 of 3 runs at 1/20 s on 2026-09-05.\n")
        self.assertEqual([t for _, t in claims_index.prose_tokens(text)], ["7", "3", "3", "1/20", "2026-09-05"])

    def test_html_comments_are_hidden_and_wrapped_lines_are_prose(self):
        self.assertEqual(claims_index.prose_tokens("Text <!-- 99\nhidden 98 --> end.\n"), [])
        self.assertEqual([t for _, t in claims_index.prose_tokens("A paragraph that wraps\n60. runs so far.\n")], ["60"])
        self.assertEqual([t for _, t in claims_index.prose_tokens("Steps:\n\n1. one\n2. two\n")], [])

    def test_number_values_ignore_thousands_commas_and_percent(self):
        self.assertTrue(claims_index.number_found("4,194,304", '"particles": 4194304,'))
        self.assertTrue(claims_index.number_found("95.93%", "coverage is 95.93 percent"))
        self.assertFalse(claims_index.number_found("60", "the 160 runs"))
        self.assertFalse(claims_index.number_found("0.3", "sg0.35 only"))
        self.assertTrue(claims_index.number_found("7.0.0", 'version: "7.0.0"'))
        self.assertFalse(claims_index.number_found("7.0", 'version: "7.0.0"'))
        self.assertEqual([t for _, t in claims_index.prose_tokens("Version 7.0.0 of 12.")], ["7.0.0", "12"])


if __name__ == "__main__":
    unittest.main()
