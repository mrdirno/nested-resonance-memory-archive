#!/usr/bin/env python3
"""
ARBITER: Artifact-Based Reproducibility and Integrity Testing for Experimental Research

Hash-based validation system ensuring experimental determinism and research integrity.
Computes cryptographic hashes of output artifacts and validates against reference manifests.

Target: Phase 1 Gate 1.3 (ARBITER CI Integration)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Date: 2025-10-31 (Cycle 816)
"""

import hashlib
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ArtifactHash:
    """Hash metadata for a single artifact."""
    path: str  # Relative path from repository root
    sha256: str  # SHA-256 hash
    size_bytes: int  # File size
    modified: str  # ISO 8601 timestamp


@dataclass
class HashManifest:
    """Collection of artifact hashes with metadata."""
    version: str  # ARBITER version
    created: str  # ISO 8601 timestamp
    description: str  # Manifest purpose
    artifacts: List[ArtifactHash]  # Hash records


class ARBITER:
    """
    Artifact-Based Reproducibility and Integrity Testing for Experimental Research.

    Ensures experimental determinism through cryptographic hash validation.
    """

    VERSION = "1.0.0"
    CHUNK_SIZE = 8192  # Read files in 8KB chunks

    def __init__(self, repo_root: Path):
        """
        Initialize ARBITER system.

        Args:
            repo_root: Path to repository root directory
        """
        self.repo_root = repo_root
        self.arbiter_dir = repo_root / "code" / "arbiter"
        self.manifest_path = self.arbiter_dir / "arbiter_manifest.json"

    def compute_sha256(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal SHA-256 hash
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while chunk := f.read(self.CHUNK_SIZE):
                sha256.update(chunk)

        return sha256.hexdigest()

    def hash_artifact(self, artifact_path: Path) -> ArtifactHash:
        """
        Compute hash and metadata for a single artifact.

        Args:
            artifact_path: Absolute path to artifact

        Returns:
            ArtifactHash record
        """
        # Compute relative path from repo root
        rel_path = str(artifact_path.relative_to(self.repo_root))

        # Compute hash
        sha256_hash = self.compute_sha256(artifact_path)

        # Get file metadata
        stat = artifact_path.stat()
        size_bytes = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

        return ArtifactHash(
            path=rel_path,
            sha256=sha256_hash,
            size_bytes=size_bytes,
            modified=modified
        )

    def create_manifest(
        self,
        artifact_patterns: List[str],
        description: str,
        output_path: Optional[Path] = None
    ) -> HashManifest:
        """
        Create hash manifest from artifact patterns.

        Args:
            artifact_patterns: List of glob patterns (e.g., "data/results/*.json")
            description: Manifest description
            output_path: Optional output path (default: arbiter_manifest.json)

        Returns:
            HashManifest object
        """
        if output_path is None:
            output_path = self.manifest_path

        # Collect all matching artifacts
        artifacts = []
        for pattern in artifact_patterns:
            for artifact_path in self.repo_root.glob(pattern):
                if artifact_path.is_file():
                    artifact_hash = self.hash_artifact(artifact_path)
                    artifacts.append(artifact_hash)

        # Sort by path for deterministic ordering
        artifacts.sort(key=lambda x: x.path)

        # Create manifest
        manifest = HashManifest(
            version=self.VERSION,
            created=datetime.now().isoformat(),
            description=description,
            artifacts=artifacts
        )

        # Save to JSON
        self.save_manifest(manifest, output_path)

        return manifest

    def save_manifest(self, manifest: HashManifest, output_path: Path):
        """
        Save manifest to JSON file.

        Args:
            manifest: HashManifest object
            output_path: Path to save JSON file
        """
        manifest_dict = {
            'version': manifest.version,
            'created': manifest.created,
            'description': manifest.description,
            'artifacts': [asdict(a) for a in manifest.artifacts]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(manifest_dict, f, indent=2)

        print(f"Manifest saved: {output_path}")
        print(f"Artifacts: {len(manifest.artifacts)}")

    def load_manifest(self, manifest_path: Optional[Path] = None) -> HashManifest:
        """
        Load manifest from JSON file.

        Args:
            manifest_path: Path to manifest file (default: arbiter_manifest.json)

        Returns:
            HashManifest object
        """
        if manifest_path is None:
            manifest_path = self.manifest_path

        with open(manifest_path, 'r') as f:
            data = json.load(f)

        artifacts = [
            ArtifactHash(
                path=a['path'],
                sha256=a['sha256'],
                size_bytes=a['size_bytes'],
                modified=a['modified']
            )
            for a in data['artifacts']
        ]

        return HashManifest(
            version=data['version'],
            created=data['created'],
            description=data['description'],
            artifacts=artifacts
        )

    def validate_manifest(
        self,
        manifest_path: Optional[Path] = None,
        strict: bool = True
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate artifacts against reference manifest.

        Args:
            manifest_path: Path to reference manifest (default: arbiter_manifest.json)
            strict: If True, fail on any hash mismatch or missing file

        Returns:
            Tuple of (validation_passed, errors, warnings)
        """
        manifest = self.load_manifest(manifest_path)

        errors = []
        warnings = []

        print("="*80)
        print("ARBITER VALIDATION")
        print("="*80)
        print()
        print(f"Manifest: {manifest_path or self.manifest_path}")
        print(f"Description: {manifest.description}")
        print(f"Created: {manifest.created}")
        print(f"Artifacts: {len(manifest.artifacts)}")
        print()

        for i, artifact in enumerate(manifest.artifacts, 1):
            artifact_path = self.repo_root / artifact.path

            # Check file exists
            if not artifact_path.exists():
                error_msg = f"✗ [{i}/{len(manifest.artifacts)}] {artifact.path}: FILE NOT FOUND"
                errors.append(error_msg)
                print(error_msg)
                continue

            # Compute current hash
            try:
                current_hash = self.compute_sha256(artifact_path)
            except Exception as e:
                error_msg = f"✗ [{i}/{len(manifest.artifacts)}] {artifact.path}: HASH ERROR ({e})"
                errors.append(error_msg)
                print(error_msg)
                continue

            # Compare hashes
            if current_hash == artifact.sha256:
                print(f"✓ [{i}/{len(manifest.artifacts)}] {artifact.path}")
            else:
                error_msg = f"✗ [{i}/{len(manifest.artifacts)}] {artifact.path}: HASH MISMATCH"
                error_detail = f"  Expected: {artifact.sha256}"
                error_detail2 = f"  Got:      {current_hash}"
                errors.append(error_msg)
                print(error_msg)
                print(error_detail)
                print(error_detail2)

            # Check file size (warning only)
            current_size = artifact_path.stat().st_size
            if current_size != artifact.size_bytes:
                warning_msg = f"⚠ [{i}/{len(manifest.artifacts)}] {artifact.path}: SIZE CHANGED ({artifact.size_bytes} → {current_size} bytes)"
                warnings.append(warning_msg)
                print(warning_msg)

        print()
        print("="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        print()
        print(f"Total artifacts: {len(manifest.artifacts)}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print()

        if errors:
            print("ERRORS:")
            for error in errors:
                print(f"  {error}")
            print()

        if warnings:
            print("WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
            print()

        validation_passed = (len(errors) == 0) if strict else True

        if validation_passed:
            print("✓ VALIDATION PASSED")
        else:
            print("✗ VALIDATION FAILED")

        print()
        print("="*80)

        return validation_passed, errors, warnings

    def update_manifest(
        self,
        artifact_patterns: List[str],
        manifest_path: Optional[Path] = None,
        dry_run: bool = False
    ) -> Tuple[int, int, int]:
        """
        Update manifest with new/changed artifacts.

        Args:
            artifact_patterns: List of glob patterns
            manifest_path: Path to manifest file
            dry_run: If True, show changes without saving

        Returns:
            Tuple of (added, modified, unchanged) counts
        """
        if manifest_path is None:
            manifest_path = self.manifest_path

        # Load existing manifest
        if manifest_path.exists():
            manifest = self.load_manifest(manifest_path)
            existing_hashes = {a.path: a.sha256 for a in manifest.artifacts}
        else:
            manifest = HashManifest(
                version=self.VERSION,
                created=datetime.now().isoformat(),
                description="ARBITER reference hashes for experimental artifacts",
                artifacts=[]
            )
            existing_hashes = {}

        # Collect current artifacts
        current_artifacts = {}
        for pattern in artifact_patterns:
            for artifact_path in self.repo_root.glob(pattern):
                if artifact_path.is_file():
                    artifact_hash = self.hash_artifact(artifact_path)
                    current_artifacts[artifact_hash.path] = artifact_hash

        # Classify changes
        added = []
        modified = []
        unchanged = []

        for path, artifact in current_artifacts.items():
            if path not in existing_hashes:
                added.append(artifact)
                print(f"+ ADD: {path}")
            elif existing_hashes[path] != artifact.sha256:
                modified.append(artifact)
                print(f"~ MOD: {path}")
                print(f"    Old: {existing_hashes[path]}")
                print(f"    New: {artifact.sha256}")
            else:
                unchanged.append(artifact)

        # Update manifest
        if not dry_run:
            manifest.artifacts = list(current_artifacts.values())
            manifest.artifacts.sort(key=lambda x: x.path)
            self.save_manifest(manifest, manifest_path)

        print()
        print(f"Added: {len(added)}")
        print(f"Modified: {len(modified)}")
        print(f"Unchanged: {len(unchanged)}")
        print()

        return len(added), len(modified), len(unchanged)


def main():
    """Command-line interface for ARBITER."""
    parser = argparse.ArgumentParser(
        description="ARBITER: Hash-based validation for experimental artifacts"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create manifest
    create_parser = subparsers.add_parser('create', help='Create new hash manifest')
    create_parser.add_argument(
        '--patterns',
        nargs='+',
        required=True,
        help='Glob patterns for artifacts (e.g., "data/results/*.json")'
    )
    create_parser.add_argument(
        '--description',
        default='ARBITER reference hashes for experimental artifacts',
        help='Manifest description'
    )
    create_parser.add_argument(
        '--output',
        type=Path,
        help='Output path (default: code/arbiter/arbiter_manifest.json)'
    )

    # Validate manifest
    validate_parser = subparsers.add_parser('validate', help='Validate artifacts against manifest')
    validate_parser.add_argument(
        '--manifest',
        type=Path,
        help='Manifest path (default: code/arbiter/arbiter_manifest.json)'
    )
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        default=True,
        help='Fail on any hash mismatch (default: True)'
    )

    # Update manifest
    update_parser = subparsers.add_parser('update', help='Update manifest with new artifacts')
    update_parser.add_argument(
        '--patterns',
        nargs='+',
        required=True,
        help='Glob patterns for artifacts'
    )
    update_parser.add_argument(
        '--manifest',
        type=Path,
        help='Manifest path'
    )
    update_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show changes without saving'
    )

    args = parser.parse_args()

    # Get repository root (assume running from repo root or code/arbiter/)
    repo_root = Path.cwd()
    if repo_root.name == 'arbiter':
        repo_root = repo_root.parent.parent

    arbiter = ARBITER(repo_root)

    if args.command == 'create':
        arbiter.create_manifest(
            artifact_patterns=args.patterns,
            description=args.description,
            output_path=args.output
        )

    elif args.command == 'validate':
        passed, errors, warnings = arbiter.validate_manifest(
            manifest_path=args.manifest,
            strict=args.strict
        )
        exit(0 if passed else 1)

    elif args.command == 'update':
        arbiter.update_manifest(
            artifact_patterns=args.patterns,
            manifest_path=args.manifest,
            dry_run=args.dry_run
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
