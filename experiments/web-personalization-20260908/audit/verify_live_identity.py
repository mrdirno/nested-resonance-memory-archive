#!/usr/bin/env python3
"""Read-only byte identity checks for the two sampled legacy HTML pages.
Author: Aldrin Payopay · GPL-3.0-only
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, default=Path("/Volumes/dual/nested-resonance-memory-archive"))
parser.add_argument("--output", type=Path, default=Path(__file__).with_name("live-identity.json"))
args = parser.parse_args()
base = "https://mrdirno.github.io/nested-resonance-memory-archive/"
results = []
for source_path, suffix in [
    ("collage-beta/index.html", "collage-beta/"),
    ("HELIOS-BRIDGE-ARCHIVE/HELIOS-V045-amethyst-interference.html", "archive/HELIOS-V045-amethyst-interference.html"),
]:
    source = (args.root / source_path).read_bytes()
    with urlopen(base + suffix, timeout=10) as response:
        live = response.read()
        results.append({
            "source_path": source_path,
            "requested_url": base + suffix,
            "response_url": response.url,
            "http_status": response.status,
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "response_sha256": hashlib.sha256(live).hexdigest(),
            "source_bytes": len(source),
            "response_bytes": len(live),
            "byte_identical": source == live,
        })
report = {"schema": "wish-live-html-identity/v1", "observed_at": datetime.now(timezone.utc).isoformat(), "scope": "Two HTML response bodies only; dependency assets and other pages were not byte-matched.", "results": results}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
raise SystemExit(0 if all(r["byte_identical"] and r["http_status"] == 200 for r in results) else 1)
