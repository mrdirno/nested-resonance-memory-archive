#!/usr/bin/env python3
"""Read-only source inclusion audit of the Pages deployment's Wish surfaces.

Author: Aldrin Payopay · GPL-3.0-only
This reads source; it does not build, open browsers, or submit feedback.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


class AuditError(Exception):
    pass


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.inline = []
        self.in_script = False
        self.script_src = None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
            self.script_src = dict(attrs).get("src")
            if self.script_src:
                self.scripts.append(self.script_src)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
            self.script_src = None

    def handle_data(self, data):
        if self.in_script and not self.script_src:
            self.inline.append(data)


def read(root, relative):
    path = root / relative
    if not path.is_file():
        raise AuditError(f"Missing expected source file: {relative}")
    return path.read_text(encoding="utf-8")


def unique_match(pattern, text, label):
    matches = re.findall(pattern, text, re.MULTILINE)
    if len(matches) != 1:
        raise AuditError(f"Deployment mapping unknown: expected one {label}; found {len(matches)}")
    return matches[0]


def deployment(root):
    relative = ".github/workflows/deploy_bridge.yml"
    workflow = read(root, relative)
    trades_raw = unique_match(r'^\s*TRADES="([a-z -]+)"\s*$', workflow, "TRADES assignment")
    trades = trades_raw.split()
    if not trades or len(trades) != len(set(trades)):
        raise AuditError("Deployment TRADES list is empty or contains duplicates")
    for trade in trades:
        if not re.fullmatch(r"[a-z]+(?:-[a-z]+)*", trade):
            raise AuditError(f"Unsafe trade slug: {trade}")
        read(root, f"{trade}/trade.js")
    disk_trades = {path.parent.name for path in root.glob("*/trade.js")}
    if disk_trades != set(trades):
        raise AuditError(f"Deployment/disk trade mismatch: unstaged={sorted(disk_trades-set(trades))}, missing={sorted(set(trades)-disk_trades)}")
    required_staging = {
        "trade pages": 'cp -R "$t/." "HELIOS-BRIDGE/dist/$t/"',
        "Commons": "cp -R commons/. HELIOS-BRIDGE/dist/commons/",
        "current Collage": "cp -R tools/collage-studio/dist/. HELIOS-BRIDGE/dist/collage/",
        "archive": "cp -R HELIOS-BRIDGE-ARCHIVE/. HELIOS-BRIDGE/dist/archive/",
        "Collage Beta": "cp -R collage-beta/. HELIOS-BRIDGE/dist/collage-beta/",
        "classic bridge": "mv HELIOS-BRIDGE/dist/index.html HELIOS-BRIDGE/dist/assets HELIOS-BRIDGE/dist/archive/classic/",
    }
    for label, statement in required_staging.items():
        if statement not in workflow:
            raise AuditError(f"Deployment mapping unknown for {label}: staging statement changed; review this adapter")
    halo = unique_match(r'^\s*cp (HELIOS-BRIDGE-ARCHIVE/[^\s]+\.html) HELIOS-BRIDGE/dist/index\.html\s*$', workflow, "active HALO root mapping")
    read(root, halo)
    return trades, halo, {
        "workflow": relative,
        "sha256": hashlib.sha256(workflow.encode()).hexdigest(),
        "mapping_policy": "TRADES and HALO root source are parsed from deployment; other known staging statements are asserted. Changed mappings fail closed for review.",
        "trade_slugs": trades,
        "active_root_source": halo,
        "limitations": [
            "This adapter understands the current deployment structure; it is not a general YAML or shell interpreter.",
            "Generated app routes/assets and public files copied by Vite are not inferred from a build that has not been run.",
        ],
    }


def page(root, source, deployed, lifecycle):
    text = read(root, source)
    parsed = Document()
    parsed.feed(text)
    direct = [src for src in parsed.scripts if re.search(r"(?:^|/)shared/(?:toolkit|feedback)\.js(?:[?#]|$)", src)]
    inline = "\n".join(parsed.inline)
    # Recognize a script.src assignment (current Collage loader), not a filename
    # mentioned by an HTML comment. This still proves source inclusion only.
    dynamic = re.findall(r"\b[\w$]+\.src\s*=\s*['\"]([^'\"]*(?:^|/)shared/(?:toolkit|feedback)\.js)['\"]", inline)
    kinds = sorted({"toolkit" if "toolkit.js" in src else "feedback" for src in direct + dynamic})
    return {
        "source_path": source,
        "deployed_paths": deployed,
        "lifecycle": lifecycle,
        "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_inclusion": {
            "status": "recognized" if kinds else "not_recognized",
            "runtimes": kinds,
            "direct_script_srcs": direct,
            "dynamic_script_src_assignments": dynamic,
            "custom_trigger_requested": bool(re.search(r"\btrigger\s*:\s*false\b", inline)),
            "meaning": "A source tag or loader assignment exists; successful loading, visibility and click behavior remain unmeasured.",
        },
        "behavior_facets": {
            "runtime_loaded": "not_tested",
            "visible_reachable_named_wish_trigger": "not_tested",
            "opens_correct_modal": "not_tested",
            "draft_survives_close_reopen": "not_tested",
            "draft_survives_reload": "not_tested",
            "submission_accepted": "not_tested",
        },
    }


def inventory(root):
    trades, halo, mapping = deployment(root)
    maintained = []
    for folder in trades + ["commons"]:
        paths = sorted((root / folder).rglob("*.html"))
        if not paths:
            raise AuditError(f"No HTML pages found for maintained deployment folder: {folder}")
        if not (root / folder / "index.html").is_file():
            raise AuditError(f"Missing maintained hub: {folder}/index.html")
        for path in paths:
            relative = path.relative_to(root).as_posix()
            maintained.append(page(root, relative, ["/" + relative], "maintained"))
    maintained.append(page(root, halo, ["/index.html", "/archive/" + Path(halo).name], "maintained"))
    maintained.append(page(root, "tools/collage-studio/index.html", ["/collage/index.html"], "maintained"))
    legacy = []
    for folder, prefix in [("HELIOS-BRIDGE-ARCHIVE", "/archive/"), ("collage-beta", "/collage-beta/")]:
        paths = sorted((root / folder).rglob("*.html"))
        if not paths:
            raise AuditError(f"Expected published legacy collection is absent: {folder}")
        for path in paths:
            relative = path.relative_to(root).as_posix()
            if relative == halo:
                continue
            target = prefix + path.relative_to(root / folder).as_posix()
            legacy.append(page(root, relative, [target], "legacy_or_archived"))
    legacy.append(page(root, "HELIOS-BRIDGE/index.html", ["/archive/classic/index.html"], "legacy_or_archived"))
    return mapping, maintained, legacy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/Volumes/dual/nested-resonance-memory-archive"))
    parser.add_argument("--page", action="append", default=[], help="Exact source path or deployed path, e.g. av/consumables.html or /collage/index.html; unknown pages fail")
    parser.add_argument("--output", type=Path, help="Write the report to this explicit path; otherwise print JSON")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        mapping, maintained, legacy = inventory(root)
        all_pages = maintained + legacy
        selected = []
        for requested in args.page:
            found = [p for p in all_pages if requested == p["source_path"] or requested in p["deployed_paths"]]
            if len(found) != 1:
                raise AuditError(f"Unknown or ambiguous page '{requested}'. Use an exact source path or deployed HTML path from the full inventory.")
            if found[0] not in selected:
                selected.append(found[0])
        git = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
        output = {
            "schema": "wish-source-inventory/v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_root": str(root),
            "git_head": git.stdout.strip() if git.returncode == 0 else None,
            "deployment": mapping,
            "scope": "Source inclusion only. Browser behavior and persistence require separate evidence; legacy omissions are debt, not maintained-surface failures.",
            "summary": {
                "maintained_source_pages": len(maintained),
                "maintained_deployed_html_paths": sum(len(p["deployed_paths"]) for p in maintained),
                "maintained_recognized_inclusions": sum(p["source_inclusion"]["status"] == "recognized" for p in maintained),
                "maintained_missing_inclusions": [p["source_path"] for p in maintained if p["source_inclusion"]["status"] != "recognized"],
                "legacy_source_pages": len(legacy),
                "legacy_recognized_inclusions": sum(p["source_inclusion"]["status"] == "recognized" for p in legacy),
                "runtime_pages_tested_by_this_script": 0,
            },
            "pages": selected if args.page else all_pages,
        }
        rendered = json.dumps(output, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
            print(json.dumps({"output": str(args.output), **output["summary"]}, indent=2))
        else:
            print(rendered, end="")
        return 1 if output["summary"]["maintained_missing_inclusions"] else 0
    except (AuditError, OSError, UnicodeError) as error:
        print(f"wish-source-audit: ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
