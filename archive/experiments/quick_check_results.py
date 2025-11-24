#!/usr/bin/env python3
"""
Quick Results Verification Tool: Paper 3 Factorial Experiments

Purpose: Rapidly check if factorial experiment results are complete and valid.
         Useful for monitoring batch execution progress (C257-C260).

Usage: python quick_check_results.py [experiment_id]
       python quick_check_results.py --all

Checks:
1. Results file exists
2. JSON structure valid
3. All 4 conditions present
4. Synergy analysis complete
5. Classification assigned
6. Population histories non-empty

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29 (Cycle 574)
License: GPL-3.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Experiment metadata
EXPERIMENTS = {
    'C255': {
        'files': [
            'cycle255_h1h2_mechanism_validation_results.json',
            'cycle255_h1h2_lightweight_results.json',
            'cycle255_h1h2_high_capacity_results.json'
        ],
        'pair': 'H1×H2',
        'names': 'Energy Pooling × Reality Sources'
    },
    'C256': {
        'files': ['cycle256_h1h4_mechanism_validation_results.json'],
        'pair': 'H1×H4',
        'names': 'Energy Pooling × Spawn Throttling'
    },
    'C257': {
        'files': ['cycle257_h1h5_mechanism_validation_results.json'],
        'pair': 'H1×H5',
        'names': 'Energy Pooling × Energy Recovery'
    },
    'C258': {
        'files': ['cycle258_h2h4_mechanism_validation_results.json'],
        'pair': 'H2×H4',
        'names': 'Reality Sources × Spawn Throttling'
    },
    'C259': {
        'files': ['cycle259_h2h5_mechanism_validation_results.json'],
        'pair': 'H2×H5',
        'names': 'Reality Sources × Energy Recovery'
    },
    'C260': {
        'files': ['cycle260_h4h5_mechanism_validation_results.json'],
        'pair': 'H4×H5',
        'names': 'Spawn Throttling × Energy Recovery'
    }
}

RESULTS_DIR = Path(__file__).parent / "results"


def check_result_file(filepath: Path) -> Tuple[bool, str, Dict]:
    """Check if a single result file is valid."""
    if not filepath.exists():
        return False, f"File not found: {filepath.name}", {}

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}", {}
    except Exception as e:
        return False, f"Error reading file: {e}", {}

    # Check required fields
    required_fields = ['metadata', 'conditions', 'synergy_analysis']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {missing}", data

    # Check conditions
    required_conditions = ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']
    conditions = data.get('conditions', {})
    if isinstance(conditions, dict):
        missing_cond = [c for c in required_conditions if c not in conditions]
    else:
        missing_cond = required_conditions

    if missing_cond:
        return False, f"Missing conditions: {missing_cond}", data

    # Check synergy analysis
    synergy = data.get('synergy_analysis', {})
    required_synergy = ['synergy', 'classification']
    missing_syn = [f for f in required_synergy if f not in synergy]
    if missing_syn:
        return False, f"Missing synergy fields: {missing_syn}", data

    # Check population histories
    for cond_name in required_conditions:
        cond_data = conditions.get(cond_name, {})
        if not cond_data.get('population_history'):
            return False, f"Empty population_history in {cond_name}", data

    return True, "Valid", data


def print_result_summary(exp_id: str, data: Dict):
    """Print a concise summary of experiment results."""
    synergy = data['synergy_analysis']
    conditions = data['conditions']

    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{exp_id}: {EXPERIMENTS[exp_id]['names']}{NC}")
    print(f"{BLUE}{'='*70}{NC}")

    # Condition results
    print(f"\n{'Condition':<15} {'Mean Pop':>12} {'Final Pop':>12} {'Max Pop':>12}")
    print(f"{'-'*55}")
    for cond_name in ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']:
        cond = conditions[cond_name]
        mean_pop = cond.get('mean_population', 'N/A')
        final_pop = cond.get('final_population', 'N/A')
        max_pop = cond.get('max_population', 'N/A')
        if isinstance(mean_pop, (int, float)):
            print(f"{cond_name:<15} {mean_pop:>12.2f} {final_pop:>12} {max_pop:>12}")
        else:
            print(f"{cond_name:<15} {str(mean_pop):>12} {str(final_pop):>12} {str(max_pop):>12}")

    # Synergy analysis
    print(f"\n{'Synergy Analysis':}")
    print(f"{'-'*55}")
    print(f"  H1 effect: {synergy.get('h1_effect', 'N/A')}")
    print(f"  H2 effect: {synergy.get('h2_effect', 'N/A')}")
    print(f"  Additive prediction: {synergy.get('additive_prediction', 'N/A')}")
    print(f"  Actual ON-ON: {synergy.get('on_on', 'N/A')}")
    print(f"  Synergy magnitude: {synergy.get('synergy', 'N/A')}")

    classification = synergy.get('classification', 'N/A')
    if classification == 'SYNERGISTIC':
        color = GREEN
    elif classification == 'ANTAGONISTIC':
        color = RED
    else:
        color = YELLOW
    print(f"  Classification: {color}{classification}{NC}")


def check_experiment(exp_id: str, verbose: bool = False):
    """Check all result files for a single experiment."""
    exp_meta = EXPERIMENTS[exp_id]
    print(f"\n{BLUE}Checking {exp_id}: {exp_meta['names']}{NC}")

    files_found = 0
    files_valid = 0
    latest_data = None

    for filename in exp_meta['files']:
        filepath = RESULTS_DIR / filename
        valid, message, data = check_result_file(filepath)

        if filepath.exists():
            files_found += 1
            status_symbol = f"{GREEN}✓{NC}" if valid else f"{RED}✗{NC}"
            status_text = f"{GREEN}VALID{NC}" if valid else f"{RED}INVALID{NC}"
        else:
            status_symbol = f"{YELLOW}⚠{NC}"
            status_text = f"{YELLOW}NOT FOUND{NC}"

        print(f"  {status_symbol} {filename:<50} {status_text}")

        if not valid and message != f"File not found: {filename}":
            print(f"      {RED}└─ {message}{NC}")

        if valid:
            files_valid += 1
            if not latest_data:
                latest_data = data

    # Overall status
    if files_valid == len(exp_meta['files']):
        print(f"\n  {GREEN}✓ All {len(exp_meta['files'])} file(s) valid{NC}")
        if verbose and latest_data:
            print_result_summary(exp_id, latest_data)
        return True
    elif files_found == 0:
        print(f"\n  {YELLOW}⚠ No results found yet{NC}")
        return False
    else:
        print(f"\n  {YELLOW}⚠ {files_valid}/{len(exp_meta['files'])} file(s) valid{NC}")
        return False


def check_all_experiments(verbose: bool = False):
    """Check all experiments."""
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}Paper 3 Factorial Experiments: Results Verification{NC}")
    print(f"{BLUE}{'='*70}{NC}")

    results = {}
    for exp_id in EXPERIMENTS.keys():
        results[exp_id] = check_experiment(exp_id, verbose=verbose)

    # Summary
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}Summary{NC}")
    print(f"{BLUE}{'='*70}{NC}")

    total = len(EXPERIMENTS)
    complete = sum(results.values())
    pending = total - complete

    print(f"\n  Total experiments: {total}")
    print(f"  {GREEN}Complete: {complete}{NC}")
    print(f"  {YELLOW}Pending: {pending}{NC}")

    if complete == total:
        print(f"\n  {GREEN}✓ All experiments complete - ready for aggregation!{NC}")
    else:
        print(f"\n  {YELLOW}⚠ {pending} experiment(s) still pending{NC}")
        pending_list = [exp_id for exp_id, status in results.items() if not status]
        print(f"     Waiting for: {', '.join(pending_list)}")

    return complete == total


def main():
    parser = argparse.ArgumentParser(
        description='Quick verification tool for Paper 3 factorial experiment results'
    )
    parser.add_argument(
        'experiment',
        nargs='?',
        choices=list(EXPERIMENTS.keys()),
        default=None,
        help='Experiment ID to check (omit for all experiments)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Check all experiments (default if no experiment specified)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed result summaries'
    )

    args = parser.parse_args()

    if args.all or args.experiment is None:
        all_complete = check_all_experiments(verbose=args.verbose)
        sys.exit(0 if all_complete else 1)
    else:
        valid = check_experiment(args.experiment, verbose=args.verbose)
        sys.exit(0 if valid else 1)


if __name__ == '__main__':
    main()
