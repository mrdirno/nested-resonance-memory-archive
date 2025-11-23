#!/usr/bin/env python3
"""
Experimental Data Survey for Regime Classification

Systematically surveys all experimental result files to identify which
contain the statistics needed for regime classification (mean, std, CV).

Builds inventory of classifiable data and identifies data gaps.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
Cycle: 871
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def survey_json_file(file_path: Path) -> Dict:
    """
    Survey a single JSON file for regime classification data.

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary with file metadata and data availability
    """
    try:
        with open(file_path) as f:
            data = json.load(f)
    except Exception as e:
        return {
            "file": file_path.name,
            "status": "error",
            "error": str(e),
            "has_regime_data": False
        }

    # Handle both dict and list structures
    if isinstance(data, list):
        # List of experiments directly
        experiments = data
        metadata = {}
    elif isinstance(data, dict):
        # Dictionary with metadata and experiments
        metadata = data.get("metadata", {})
        experiments = data.get("experiments", [])
    else:
        return {
            "file": file_path.name,
            "status": "unknown_format",
            "has_regime_data": False
        }

    if not experiments:
        return {
            "file": file_path.name,
            "status": "no_experiments",
            "has_regime_data": False
        }

    # Check first experiment for required fields
    first_exp = experiments[0]
    has_mean = "mean_population" in first_exp
    has_std = "std_population" in first_exp
    has_cv = "cv_population" in first_exp
    has_basin = "basin" in first_exp
    has_condition = "condition" in first_exp
    has_frequency = "frequency" in first_exp or "frequency" in metadata

    has_regime_data = has_mean and has_std and has_cv

    return {
        "file": file_path.name,
        "status": "ok",
        "cycle": metadata.get("cycle", "unknown"),
        "scenario": metadata.get("scenario", "unknown"),
        "num_experiments": len(experiments),
        "has_mean": has_mean,
        "has_std": has_std,
        "has_cv": has_cv,
        "has_basin": has_basin,
        "has_condition": has_condition,
        "has_frequency": has_frequency,
        "has_regime_data": has_regime_data,
    }


def survey_all_files(results_dir: Path, exclude_dirs: Set[str]) -> List[Dict]:
    """
    Survey all JSON files in results directory.

    Args:
        results_dir: Path to experiments/results directory
        exclude_dirs: Set of directory names to exclude

    Returns:
        List of survey results
    """
    survey_results = []

    # Find all JSON files
    for json_file in results_dir.rglob("*.json"):
        # Skip excluded directories
        if any(excl in json_file.parts for excl in exclude_dirs):
            continue

        result = survey_json_file(json_file)
        result["relative_path"] = str(json_file.relative_to(results_dir))
        survey_results.append(result)

    return survey_results


def analyze_survey_results(survey_results: List[Dict]) -> Dict:
    """
    Analyze survey results and compute statistics.

    Args:
        survey_results: List of survey results

    Returns:
        Dictionary with analysis summary
    """
    total_files = len(survey_results)

    # Status counts
    ok_files = [r for r in survey_results if r["status"] == "ok"]
    error_files = [r for r in survey_results if r["status"] == "error"]
    no_exp_files = [r for r in survey_results if r["status"] == "no_experiments"]

    # Regime data availability
    classifiable_files = [r for r in ok_files if r.get("has_regime_data", False)]

    # Field availability
    has_mean = len([r for r in ok_files if r.get("has_mean", False)])
    has_std = len([r for r in ok_files if r.get("has_std", False)])
    has_cv = len([r for r in ok_files if r.get("has_cv", False)])
    has_basin = len([r for r in ok_files if r.get("has_basin", False)])
    has_condition = len([r for r in ok_files if r.get("has_condition", False)])
    has_frequency = len([r for r in ok_files if r.get("has_frequency", False)])

    # Experiment counts
    total_experiments = sum(r.get("num_experiments", 0) for r in classifiable_files)

    return {
        "total_files": total_files,
        "ok_files": len(ok_files),
        "error_files": len(error_files),
        "no_exp_files": len(no_exp_files),
        "classifiable_files": len(classifiable_files),
        "total_classifiable_experiments": total_experiments,
        "field_availability": {
            "mean_population": has_mean,
            "std_population": has_std,
            "cv_population": has_cv,
            "basin": has_basin,
            "condition": has_condition,
            "frequency": has_frequency,
        },
        "classifiable_files_list": [r["file"] for r in classifiable_files],
        "all_classifiable": classifiable_files,
    }


def main():
    """Main survey routine."""
    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    exclude_dirs = {"long_term", "ultra_long_term", "checkpoints"}

    print("=" * 80)
    print("EXPERIMENTAL DATA SURVEY FOR REGIME CLASSIFICATION")
    print("=" * 80)
    print(f"\nSurvey directory: {results_dir}")
    print(f"Excluding: {', '.join(exclude_dirs)}\n")

    # Perform survey
    print("Scanning files...")
    survey_results = survey_all_files(results_dir, exclude_dirs)

    print(f"Found {len(survey_results)} JSON files\n")
    print("Analyzing data availability...")

    # Analyze results
    analysis = analyze_survey_results(survey_results)

    # Display summary
    print("\n" + "=" * 80)
    print("SURVEY RESULTS")
    print("=" * 80)

    print(f"\nTotal files scanned: {analysis['total_files']}")
    print(f"  ✓ Successfully parsed: {analysis['ok_files']}")
    print(f"  ✗ Parse errors: {analysis['error_files']}")
    print(f"  ⚠ No experiments: {analysis['no_exp_files']}")

    print(f"\nREGIME CLASSIFICATION DATA AVAILABILITY:")
    print(f"  Files with complete data (mean+std+CV): {analysis['classifiable_files']} "
          f"({analysis['classifiable_files']/analysis['total_files']*100:.1f}%)")
    print(f"  Total classifiable experiments: {analysis['total_classifiable_experiments']}")

    print(f"\nFIELD AVAILABILITY (in successfully parsed files):")
    for field, count in analysis['field_availability'].items():
        pct = (count / analysis['ok_files']) * 100 if analysis['ok_files'] > 0 else 0
        print(f"  {field:20s}: {count:3d}/{analysis['ok_files']:3d} ({pct:5.1f}%)")

    if analysis['classifiable_files'] > 0:
        print(f"\nCLASSIFIABLE FILES ({analysis['classifiable_files']}):")
        print("-" * 80)
        for i, file_info in enumerate(analysis['all_classifiable'], 1):
            cycle = file_info.get('cycle', 'N/A')
            scenario = file_info.get('scenario', 'N/A')
            num_exp = file_info.get('num_experiments', 0)
            print(f"  {i:2d}. {file_info['file']:50s} "
                  f"C{cycle:>3s} | {num_exp:3d} exp | {scenario[:30]}")

    # Save detailed results
    output_path = results_dir / "data_survey_results.json"
    with open(output_path, 'w') as f:
        json.dump({
            "analysis": analysis,
            "full_survey": survey_results
        }, f, indent=2)

    print(f"\n\n✓ Detailed results saved to: {output_path}")
    print("\n" + "=" * 80)
    print("SURVEY COMPLETE")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
