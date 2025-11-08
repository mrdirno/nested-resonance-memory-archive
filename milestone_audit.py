#!/usr/bin/env python3
"""
Audit V6 Milestone Claims in Git Commit History

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Purpose: Identify inconsistencies in day-milestone claims
"""

from datetime import datetime, timedelta
import re
from typing import List, Tuple, Dict
import subprocess

def get_milestone_commits() -> List[Tuple[str, str, str]]:
    """Extract all commits with day milestone claims."""
    result = subprocess.run(
        ['git', 'log', '--all', '--pretty=format:%H|%ai|%s'],
        capture_output=True,
        text=True,
        check=True
    )

    commits = []
    for line in result.stdout.strip().split('\n'):
        if re.search(r'([0-9]{1,3})-day', line, re.IGNORECASE):
            commits.append(tuple(line.split('|', 2)))

    return commits

def parse_commit(commit_hash: str, commit_date: str, commit_msg: str) -> Dict:
    """Parse commit data and extract milestone claim."""
    # Extract day number from commit message
    match = re.search(r'([0-9]{1,3}(?:\.\d+)?)-day', commit_msg, re.IGNORECASE)
    day_claim = float(match.group(1)) if match else None

    # Parse commit datetime (format: 2025-11-07 22:44:31 -0800)
    dt = datetime.strptime(commit_date[:19], '%Y-%m-%d %H:%M:%S')

    # Extract cycle number if present
    cycle_match = re.search(r'Cycle (\d+)', commit_msg)
    cycle_num = int(cycle_match.group(1)) if cycle_match else None

    return {
        'hash': commit_hash[:8],
        'full_hash': commit_hash,
        'datetime': dt,
        'day_claim': day_claim,
        'cycle': cycle_num,
        'message': commit_msg
    }

def calculate_implied_start(commit_dt: datetime, day_claim: float) -> datetime:
    """Calculate implied V6 start date from milestone claim."""
    return commit_dt - timedelta(days=day_claim)

def main():
    # Repository creation date
    REPO_CREATED = datetime(2025, 10, 25, 22, 26, 7)

    print("=" * 80)
    print("V6 MILESTONE AUDIT REPORT")
    print("=" * 80)
    print(f"\nRepository Created: {REPO_CREATED.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Repository creation is the EARLIEST possible V6 start date\n")

    # Get all milestone commits
    raw_commits = get_milestone_commits()
    commits = [parse_commit(*c) for c in raw_commits]

    # Sort by datetime (chronological order)
    commits.sort(key=lambda x: x['datetime'])

    print(f"Total commits with day milestone claims: {len(commits)}\n")

    # Track unique implied start dates
    implied_starts = {}
    inconsistencies = []
    impossible_claims = []

    print("=" * 80)
    print("CHRONOLOGICAL MILESTONE ANALYSIS")
    print("=" * 80)
    print(f"{'Commit':<10} {'Date/Time':<20} {'Days':<8} {'Cycle':<8} {'Implied V6 Start':<20} {'Status'}")
    print("-" * 100)

    for c in commits:
        implied_start = calculate_implied_start(c['datetime'], c['day_claim'])
        implied_start_key = implied_start.strftime('%Y-%m-%d')

        # Track unique implied start dates
        if implied_start_key not in implied_starts:
            implied_starts[implied_start_key] = []
        implied_starts[implied_start_key].append(c)

        # Check if implied start is before repository creation
        status = "OK"
        if implied_start < REPO_CREATED:
            days_before = (REPO_CREATED - implied_start).days
            status = f"IMPOSSIBLE (-{days_before}d before repo)"
            impossible_claims.append({
                **c,
                'implied_start': implied_start,
                'days_before_repo': days_before
            })

        print(f"{c['hash']:<10} {c['datetime'].strftime('%Y-%m-%d %H:%M'):<20} "
              f"{c['day_claim']:<8.1f} {c['cycle'] or 'N/A':<8} "
              f"{implied_start.strftime('%Y-%m-%d %H:%M'):<20} {status}")

    print("\n" + "=" * 80)
    print("SUMMARY OF IMPLIED V6 START DATES")
    print("=" * 80)

    for start_date in sorted(implied_starts.keys()):
        commits_for_date = implied_starts[start_date]
        count = len(commits_for_date)
        earliest_claim = min(c['day_claim'] for c in commits_for_date)
        latest_claim = max(c['day_claim'] for c in commits_for_date)

        status = ""
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        if start_dt < REPO_CREATED:
            days_before = (REPO_CREATED - start_dt).days
            status = f" [IMPOSSIBLE: {days_before} days before repo creation]"

        print(f"\nImplied Start: {start_date}{status}")
        print(f"  - Commits: {count}")
        print(f"  - Day claims: {earliest_claim:.1f} to {latest_claim:.1f}")
        print(f"  - Cycles: {', '.join(str(c['cycle']) for c in commits_for_date if c['cycle'])}")

    print("\n" + "=" * 80)
    print("INCONSISTENCIES FOUND")
    print("=" * 80)

    if len(implied_starts) > 1:
        print(f"\n❌ CRITICAL: {len(implied_starts)} different implied V6 start dates found!")
        print(f"   Expected: All milestones should imply the SAME V6 start date")
        print(f"   Found: {len(implied_starts)} different start dates\n")

        # Calculate range of implied start dates
        all_start_dates = [datetime.strptime(d, '%Y-%m-%d') for d in implied_starts.keys()]
        earliest_implied = min(all_start_dates)
        latest_implied = max(all_start_dates)
        date_range = (latest_implied - earliest_implied).days

        print(f"   Implied start date range: {date_range} days")
        print(f"   Earliest implied start: {earliest_implied.strftime('%Y-%m-%d')}")
        print(f"   Latest implied start: {latest_implied.strftime('%Y-%m-%d')}")
    else:
        print("\n✓ All milestones imply the same V6 start date (consistent)")

    if impossible_claims:
        print(f"\n❌ CRITICAL: {len(impossible_claims)} commits claim milestones BEFORE repository creation!")
        print(f"   These commits claim V6 started before the repository existed:\n")

        for claim in impossible_claims:
            print(f"   {claim['hash']} (Cycle {claim['cycle'] or 'N/A'})")
            print(f"     - Claimed: {claim['day_claim']:.1f}-day milestone")
            print(f"     - Commit date: {claim['datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     - Implied V6 start: {claim['implied_start'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     - Problem: {claim['days_before_repo']} days BEFORE repo creation")
            print(f"     - Message: {claim['message'][:80]}...\n")
    else:
        print("\n✓ No impossible claims (all implied start dates are after repo creation)")

    print("\n" + "=" * 80)
    print("COMMITS REQUIRING CORRECTION")
    print("=" * 80)

    if impossible_claims:
        print(f"\nAll {len(impossible_claims)} commits with impossible milestone claims need correction:")
        print("\nCommit hashes to fix:")
        for claim in impossible_claims:
            print(f"  {claim['full_hash']}")

        print("\n⚠️  WARNING: These commits claim V6 milestones that imply V6 started")
        print(f"    BEFORE the repository was created ({REPO_CREATED.strftime('%Y-%m-%d')})")
        print("\n    This is logically impossible and must be corrected.")
    else:
        print("\n✓ No corrections needed - all milestone claims are consistent")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if impossible_claims or len(implied_starts) > 1:
        print("\n1. Establish the TRUE V6 start date")
        print("   - V6 cannot start before repository creation (2025-10-25)")
        print("   - Review documentation to determine actual V6 start date")

        print("\n2. Recalculate all milestone claims")
        print("   - Use: days_since_v6_start = (commit_date - v6_start_date).days")
        print("   - Ensure consistency across all commits")

        print("\n3. Consider git commit message amendment")
        print("   - Use interactive rebase to fix commit messages")
        print("   - OR: Document discrepancy in research notes")
        print("   - OR: Add correction commits explaining the error")

        print("\n4. Future milestone commits")
        print("   - Use automated calculation to ensure consistency")
        print("   - Reference a documented V6_START_DATE constant")
    else:
        print("\n✓ No action required - milestone claims are consistent")

if __name__ == '__main__':
    main()
