#!/usr/bin/env python3
"""Preview root-file archival; apply only explicitly selected, reviewed files.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only
"""

import argparse
from dataclasses import dataclass
import fnmatch
import os
from pathlib import Path
import sys

MOVES = {
    "archive/artifacts": ["agent_artifact_*.py"],
    "archive/reports": ["FINAL_REPORT_V*.md", "FINAL_REPORT.md"],
    "archive/context": ["walkthrough.md", "task.md", "implementation_plan.md", "MESSAGE_TO_FUTURE_AI.md"],
    "backups": ["*.zip", "*.tar.gz"],
    "data/temp": ["temp_*", "*.log"],
}


@dataclass(frozen=True)
class Move:
    source: Path
    target: Path


def plan_moves(root):
    root = root.resolve()
    moves = []
    for source in sorted(root.iterdir()):
        if source.is_symlink() or not source.is_file():
            continue
        for destination, patterns in MOVES.items():
            if any(fnmatch.fnmatchcase(source.name, pattern) for pattern in patterns):
                target = root / destination / source.name
                if not target.resolve().is_relative_to(root):
                    raise ValueError(f"Archive destination escapes repository: {destination}")
                # lexists catches dangling symlinks as collisions too.
                if os.path.lexists(target):
                    print(f"SKIP {source.name}: destination already exists", file=sys.stderr)
                else:
                    moves.append(Move(source, target))
                break
    return moves


def apply_move(move):
    """Hard-link then unlink on the same volume; never overwrite a destination."""
    if move.source.is_symlink() or not move.source.is_file():
        raise ValueError(f"Source is no longer a regular file: {move.source.name}")
    move.target.parent.mkdir(parents=True, exist_ok=True)
    os.link(move.source, move.target, follow_symlinks=False)
    move.source.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="Apply reviewed names passed with --only")
    parser.add_argument("--only", nargs="+", metavar="ROOT_FILENAME", help="Exact root filenames reviewed for archival")
    args = parser.parse_args(argv)
    if args.apply and not args.only:
        parser.error("--apply requires --only with exact filenames after manual review")
    if args.only and any(Path(p).name != p or p in {".", ".."} for p in args.only):
        parser.error("--only accepts root filenames, not paths")
    root = args.root.resolve()
    try:
        if not (root / "README.md").is_file() or not (root / "docs/protocols/MAINTENANCE_PROTOCOL.md").is_file():
            raise ValueError("Root must contain README.md and the maintenance protocol")
        moves = plan_moves(root)
        if args.only:
            missing = set(args.only) - {move.source.name for move in moves}
            if missing:
                raise ValueError("Not eligible (missing, collision, symlink or no rule): " + ", ".join(sorted(missing)))
            moves = [move for move in moves if move.source.name in args.only]
        for move in moves:
            if args.apply:
                apply_move(move)
            print(f"{'MOVED' if args.apply else 'PREVIEW'} {move.source.name} -> {move.target.relative_to(root)}")
        print(f"{len(moves)} {'files moved' if args.apply else 'candidates; no files changed'}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Cleanup stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
