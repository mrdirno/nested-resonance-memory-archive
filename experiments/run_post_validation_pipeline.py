#!/usr/bin/env python3
"""
POST-VALIDATION PIPELINE ORCHESTRATION

Purpose: Automated execution of validation analysis and composite scoring after C186-C189 complete

Pipeline Steps:
  1. Verify all experimental results files exist
  2. Execute validation analysis scripts (C186-C189)
  3. Generate publication figures (24 figures @ 300 DPI)
  4. Execute composite validation analysis
  5. Generate final scorecard and recommendation
  6. Create validation summary report

Execution:
  python3 run_post_validation_pipeline.py

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1018
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import time

# Experiment and validation script mappings
EXPERIMENTS = {
    'c186': {
        'name': 'Hierarchical Energy Dynamics',
        'results_file': 'cycle186_metapopulation_hierarchical_validation_results.json',
        'analysis_script': 'analyze_c186_hierarchical_validation.py',
        'validation_report': 'cycle186_validation_report.json',
        'expected_figures': 6
    },
    'c187': {
        'name': 'Network Structure Effects',
        'results_file': 'cycle187_network_structure_effects_results.json',
        'analysis_script': 'analyze_c187_network_validation.py',
        'validation_report': 'cycle187_validation_report.json',
        'expected_figures': 6
    },
    'c188': {
        'name': 'Memory Effects',
        'results_file': 'cycle188_memory_effects_results.json',
        'analysis_script': 'analyze_c188_memory_validation.py',
        'validation_report': 'cycle188_validation_report.json',
        'expected_figures': 6
    },
    'c189': {
        'name': 'Burst Clustering',
        'results_file': 'cycle189_burst_clustering_results.json',
        'analysis_script': 'analyze_c189_burst_validation.py',
        'validation_report': 'cycle189_validation_report.json',
        'expected_figures': 6
    }
}

COMPOSITE_SCRIPT = 'composite_validation_analysis.py'


def print_banner(message: str):
    """Print formatted banner."""
    print("\n" + "=" * 80)
    print(message.center(80))
    print("=" * 80 + "\n")


def check_experimental_results() -> dict:
    """
    Verify all experimental results files exist.

    Returns:
        dict with status for each experiment
    """
    print_banner("STEP 1: VERIFY EXPERIMENTAL RESULTS")

    results_dir = Path(__file__).parent / "results"
    status = {}

    for exp_id, exp_data in EXPERIMENTS.items():
        results_path = results_dir / exp_data['results_file']
        exists = results_path.exists()
        status[exp_id] = {
            'results_exist': exists,
            'results_path': str(results_path)
        }

        if exists:
            # Get file size and modification time
            file_size = results_path.stat().st_size
            mod_time = datetime.fromtimestamp(results_path.stat().st_mtime)
            status[exp_id]['file_size'] = file_size
            status[exp_id]['modified'] = mod_time.isoformat()
            print(f"✅ {exp_id.upper()}: {exp_data['name']}")
            print(f"   Path: {results_path}")
            print(f"   Size: {file_size / 1024:.1f} KB")
            print(f"   Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ {exp_id.upper()}: {exp_data['name']} - MISSING")
            print(f"   Expected: {results_path}")

        print()

    # Summary
    completed = sum(1 for s in status.values() if s['results_exist'])
    print(f"Experiments with results: {completed}/{len(EXPERIMENTS)}")
    print()

    return status


def run_validation_analysis(exp_id: str, exp_data: dict) -> dict:
    """
    Execute validation analysis script for given experiment.

    Args:
        exp_id: Experiment identifier (c186, c187, etc.)
        exp_data: Experiment metadata

    Returns:
        dict with execution status
    """
    script_path = Path(__file__).parent / exp_data['analysis_script']

    if not script_path.exists():
        return {
            'success': False,
            'error': f"Analysis script not found: {script_path}"
        }

    print(f"Running {exp_id.upper()} validation analysis...")
    start_time = time.time()

    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ {exp_id.upper()} validation complete ({elapsed:.1f}s)")
            return {
                'success': True,
                'elapsed': elapsed,
                'stdout': result.stdout
            }
        else:
            print(f"❌ {exp_id.upper()} validation FAILED")
            print(f"   Error: {result.stderr[:200]}")
            return {
                'success': False,
                'error': result.stderr,
                'elapsed': elapsed
            }

    except subprocess.TimeoutExpired:
        print(f"❌ {exp_id.upper()} validation TIMEOUT (>5 min)")
        return {
            'success': False,
            'error': 'Timeout after 5 minutes'
        }
    except Exception as e:
        print(f"❌ {exp_id.upper()} validation ERROR: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_all_validations() -> dict:
    """
    Execute all validation analysis scripts sequentially.

    Returns:
        dict with status for each validation
    """
    print_banner("STEP 2: EXECUTE VALIDATION ANALYSES")

    validation_status = {}
    total_elapsed = 0

    for exp_id, exp_data in EXPERIMENTS.items():
        status = run_validation_analysis(exp_id, exp_data)
        validation_status[exp_id] = status

        if status['success']:
            total_elapsed += status['elapsed']

        # Check if validation report was generated
        report_path = Path(__file__).parent / "results" / exp_data['validation_report']
        validation_status[exp_id]['report_exists'] = report_path.exists()

        if report_path.exists():
            print(f"   Report generated: {report_path.name}")
        else:
            print(f"   ⚠️ Report not found: {exp_data['validation_report']}")

        print()

    # Summary
    successful = sum(1 for s in validation_status.values() if s['success'])
    print(f"Validations completed: {successful}/{len(EXPERIMENTS)}")
    print(f"Total analysis time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    print()

    return validation_status


def run_composite_analysis() -> dict:
    """
    Execute composite validation analysis.

    Returns:
        dict with execution status and composite score
    """
    print_banner("STEP 3: COMPOSITE VALIDATION ANALYSIS")

    script_path = Path(__file__).parent / COMPOSITE_SCRIPT

    if not script_path.exists():
        return {
            'success': False,
            'error': f"Composite script not found: {script_path}"
        }

    print("Running composite validation analysis...")
    start_time = time.time()

    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=300
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ Composite analysis complete ({elapsed:.1f}s)")
            print()
            print(result.stdout)

            # Load composite report
            report_path = Path(__file__).parent / "results" / "composite_validation_report.json"
            if report_path.exists():
                with open(report_path, 'r') as f:
                    composite_data = json.load(f)
                return {
                    'success': True,
                    'elapsed': elapsed,
                    'composite_data': composite_data
                }
            else:
                return {
                    'success': True,
                    'elapsed': elapsed,
                    'warning': 'Report not found after execution'
                }
        else:
            print(f"❌ Composite analysis FAILED")
            print(f"   Error: {result.stderr[:200]}")
            return {
                'success': False,
                'error': result.stderr,
                'elapsed': elapsed
            }

    except subprocess.TimeoutExpired:
        print(f"❌ Composite analysis TIMEOUT")
        return {
            'success': False,
            'error': 'Timeout after 5 minutes'
        }
    except Exception as e:
        print(f"❌ Composite analysis ERROR: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def generate_pipeline_summary(
    results_status: dict,
    validation_status: dict,
    composite_status: dict
) -> dict:
    """
    Generate pipeline execution summary.

    Args:
        results_status: Experimental results verification status
        validation_status: Validation analysis status
        composite_status: Composite analysis status

    Returns:
        dict with complete pipeline summary
    """
    print_banner("PIPELINE EXECUTION SUMMARY")

    summary = {
        'timestamp': datetime.now().isoformat(),
        'results_status': results_status,
        'validation_status': validation_status,
        'composite_status': composite_status
    }

    # Count successes
    results_complete = sum(1 for s in results_status.values() if s['results_exist'])
    validations_complete = sum(1 for s in validation_status.values() if s['success'])
    composite_complete = composite_status.get('success', False)

    print(f"Experimental Results: {results_complete}/{len(EXPERIMENTS)}")
    print(f"Validation Analyses: {validations_complete}/{len(EXPERIMENTS)}")
    print(f"Composite Analysis: {'✅ Complete' if composite_complete else '❌ Failed'}")
    print()

    # Composite score if available
    if composite_complete and 'composite_data' in composite_status:
        comp_data = composite_status['composite_data']
        print("=" * 80)
        print("COMPOSITE VALIDATION SCORE")
        print("=" * 80)
        print()
        print(f"Total Score: {comp_data['total_score']:.1f} / {comp_data['max_total']:.1f}")
        print(f"Interpretation: {comp_data['interpretation']}")
        print(f"Confidence: {comp_data['confidence']}")
        print(f"Recommendation: {comp_data['recommendation']}")
        print()

        summary['composite_score'] = comp_data['total_score']
        summary['interpretation'] = comp_data['interpretation']
        summary['recommendation'] = comp_data['recommendation']

    # Save summary
    summary_path = Path(__file__).parent / "results" / "pipeline_execution_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Pipeline summary saved: {summary_path}")
    print()

    return summary


def main():
    """Execute post-validation pipeline."""
    print_banner("POST-VALIDATION PIPELINE ORCHESTRATION")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Workspace: {Path(__file__).parent}")
    print()

    # Step 1: Check experimental results
    results_status = check_experimental_results()

    results_complete = sum(1 for s in results_status.values() if s['results_exist'])
    if results_complete == 0:
        print("❌ ERROR: No experimental results found. Run experiments first.")
        sys.exit(1)
    elif results_complete < len(EXPERIMENTS):
        print(f"⚠️ WARNING: Only {results_complete}/{len(EXPERIMENTS)} experiments complete.")
        print("   Proceeding with available data...\n")

    # Step 2: Run validation analyses
    validation_status = run_all_validations()

    validations_complete = sum(1 for s in validation_status.values() if s['success'])
    if validations_complete == 0:
        print("❌ ERROR: All validation analyses failed.")
        sys.exit(1)

    # Step 3: Run composite analysis
    composite_status = run_composite_analysis()

    # Generate pipeline summary
    summary = generate_pipeline_summary(results_status, validation_status, composite_status)

    # Final message
    print_banner("PIPELINE EXECUTION COMPLETE")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if composite_status.get('success') and 'composite_score' in summary:
        score = summary['composite_score']
        if score >= 17.0:
            print("🎉 Framework STRONGLY VALIDATED - Proceed with Paper 4 submission")
            sys.exit(0)
        elif score >= 13.0:
            print("⚠️ Framework PARTIALLY VALIDATED - Consider refinement experiments")
            sys.exit(0)
        else:
            print("❌ Framework WEAKLY SUPPORTED or REJECTED - Major revision needed")
            sys.exit(1)
    else:
        print("⚠️ Composite analysis incomplete - Review validation outputs")
        sys.exit(1)


if __name__ == "__main__":
    main()
