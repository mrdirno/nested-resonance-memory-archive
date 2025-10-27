#!/usr/bin/env python3
"""
Paper 5D: Emergence Pattern Catalog - Pattern Mining Tool

Analyzes existing experimental datasets (C171, C175, C176, C177, C255)
to identify and classify recurring emergent patterns in NRM systems.

Pattern Categories:
1. Spatial Patterns: Clustering, dispersion, fragmentation
2. Temporal Patterns: Oscillations, bursts, steady states
3. Interaction Patterns: Synergy, antagonism, independence
4. Memory Patterns: Retention, decay, transfer

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class PatternMiner:
    """Mine emergent patterns from experimental datasets."""

    def __init__(self, data_dir: Path):
        """Initialize pattern miner.

        Args:
            data_dir: Directory containing experimental result JSON files
        """
        self.data_dir = Path(data_dir)
        self.patterns = {
            'spatial': [],
            'temporal': [],
            'interaction': [],
            'memory': []
        }
        self.pattern_stats = defaultdict(lambda: {'count': 0, 'examples': []})

    def load_experiment(self, filename: str) -> Dict:
        """Load experimental results from JSON file.

        Args:
            filename: Name of JSON file in data_dir

        Returns:
            Dictionary containing experimental data
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return {}

        with open(filepath, 'r') as f:
            return json.load(f)

    def detect_spatial_patterns(self, data: Dict) -> List[Dict]:
        """Detect spatial patterns (clustering, dispersion, fragmentation).

        Args:
            data: Experimental data dictionary

        Returns:
            List of detected spatial patterns
        """
        patterns = []

        # Look for population dynamics
        if 'results' in data:
            for condition in data['results']:
                if 'mean_population' in condition:
                    pop = condition['mean_population']
                    variance = condition.get('std_population', 0) ** 2

                    # Clustering pattern: High population with low variance
                    if pop > 50 and variance < 100:
                        patterns.append({
                            'type': 'clustering',
                            'strength': pop / (variance + 1),
                            'condition': condition.get('condition', 'unknown'),
                            'population': pop,
                            'variance': variance
                        })

                    # Dispersion pattern: Low population with high variance
                    elif pop < 30 and variance > 200:
                        patterns.append({
                            'type': 'dispersion',
                            'strength': variance / (pop + 1),
                            'condition': condition.get('condition', 'unknown'),
                            'population': pop,
                            'variance': variance
                        })

                    # Fragmentation pattern: Medium population with very high variance
                    elif 30 <= pop <= 50 and variance > 300:
                        patterns.append({
                            'type': 'fragmentation',
                            'strength': variance / pop,
                            'condition': condition.get('condition', 'unknown'),
                            'population': pop,
                            'variance': variance
                        })

        return patterns

    def detect_temporal_patterns(self, data: Dict) -> List[Dict]:
        """Detect temporal patterns (oscillations, bursts, steady states).

        Args:
            data: Experimental data dictionary

        Returns:
            List of detected temporal patterns
        """
        patterns = []

        # Look for time series data
        if 'results' in data:
            for condition in data['results']:
                # Steady state pattern: Low variance over time
                if 'std_population' in condition:
                    std = condition['std_population']
                    mean = condition.get('mean_population', 0)

                    if std < 5 and mean > 20:
                        patterns.append({
                            'type': 'steady_state',
                            'stability': mean / (std + 0.1),
                            'condition': condition.get('condition', 'unknown'),
                            'mean': mean,
                            'std': std
                        })

                    # Oscillation pattern: Medium variance with periodic structure
                    elif 5 <= std <= 15:
                        patterns.append({
                            'type': 'oscillation',
                            'amplitude': std,
                            'condition': condition.get('condition', 'unknown'),
                            'mean': mean,
                            'std': std
                        })

                    # Burst pattern: Very high variance with intermittent spikes
                    elif std > 20:
                        patterns.append({
                            'type': 'burst',
                            'intensity': std,
                            'condition': condition.get('condition', 'unknown'),
                            'mean': mean,
                            'std': std
                        })

        return patterns

    def detect_interaction_patterns(self, data: Dict) -> List[Dict]:
        """Detect interaction patterns (synergy, antagonism, independence).

        Args:
            data: Experimental data dictionary

        Returns:
            List of detected interaction patterns
        """
        patterns = []

        # Look for mechanism interactions
        if 'results' in data:
            results_dict = {}
            for condition in data['results']:
                code = condition.get('condition', condition.get('code', 'unknown'))
                results_dict[code] = condition

            # Check for synergy (interaction > sum of main effects)
            if '11' in results_dict and '10' in results_dict and '01' in results_dict and '00' in results_dict:
                baseline = results_dict['00'].get('mean_population', 0)
                h1_only = results_dict['10'].get('mean_population', 0)
                h2_only = results_dict['01'].get('mean_population', 0)
                both = results_dict['11'].get('mean_population', 0)

                h1_effect = h1_only - baseline
                h2_effect = h2_only - baseline
                expected = baseline + h1_effect + h2_effect
                interaction = both - expected

                if abs(interaction) > 5:
                    if interaction > 0:
                        patterns.append({
                            'type': 'synergy',
                            'strength': interaction,
                            'h1_effect': h1_effect,
                            'h2_effect': h2_effect,
                            'observed': both,
                            'expected': expected
                        })
                    else:
                        patterns.append({
                            'type': 'antagonism',
                            'strength': abs(interaction),
                            'h1_effect': h1_effect,
                            'h2_effect': h2_effect,
                            'observed': both,
                            'expected': expected
                        })
                else:
                    patterns.append({
                        'type': 'independence',
                        'strength': abs(interaction),
                        'h1_effect': h1_effect,
                        'h2_effect': h2_effect,
                        'observed': both,
                        'expected': expected
                    })

        return patterns

    def detect_memory_patterns(self, data: Dict) -> List[Dict]:
        """Detect memory patterns (retention, decay, transfer).

        Args:
            data: Experimental data dictionary

        Returns:
            List of detected memory patterns
        """
        patterns = []

        # Look for pattern persistence across conditions
        if 'results' in data:
            populations = []
            for condition in data['results']:
                if 'mean_population' in condition:
                    populations.append(condition['mean_population'])

            if len(populations) > 1:
                # Retention pattern: Consistent values across conditions
                pop_std = np.std(populations)
                pop_mean = np.mean(populations)

                if pop_std < 10 and pop_mean > 20:
                    patterns.append({
                        'type': 'retention',
                        'consistency': pop_mean / (pop_std + 0.1),
                        'mean': pop_mean,
                        'std': pop_std,
                        'n_conditions': len(populations)
                    })

                # Decay pattern: Declining trend across conditions
                elif len(populations) >= 3:
                    trend = np.polyfit(range(len(populations)), populations, 1)[0]
                    if trend < -2:
                        patterns.append({
                            'type': 'decay',
                            'rate': abs(trend),
                            'initial': populations[0],
                            'final': populations[-1],
                            'n_conditions': len(populations)
                        })

                    # Transfer pattern: Increasing trend
                    elif trend > 2:
                        patterns.append({
                            'type': 'transfer',
                            'rate': trend,
                            'initial': populations[0],
                            'final': populations[-1],
                            'n_conditions': len(populations)
                        })

        return patterns

    def mine_experiment(self, filename: str) -> Dict:
        """Mine all patterns from a single experiment.

        Args:
            filename: Experiment result JSON filename

        Returns:
            Dictionary containing all detected patterns by category
        """
        print(f"\nMining patterns from {filename}...")
        data = self.load_experiment(filename)

        if not data:
            return {'spatial': [], 'temporal': [], 'interaction': [], 'memory': []}

        patterns = {
            'spatial': self.detect_spatial_patterns(data),
            'temporal': self.detect_temporal_patterns(data),
            'interaction': self.detect_interaction_patterns(data),
            'memory': self.detect_memory_patterns(data)
        }

        # Update statistics
        for category, category_patterns in patterns.items():
            for pattern in category_patterns:
                pattern_type = pattern.get('type', 'unknown')
                self.pattern_stats[f"{category}/{pattern_type}"]['count'] += 1
                self.pattern_stats[f"{category}/{pattern_type}"]['examples'].append({
                    'experiment': filename,
                    'details': pattern
                })

        # Print summary
        total = sum(len(p) for p in patterns.values())
        print(f"  Found {total} patterns:")
        for category, category_patterns in patterns.items():
            if category_patterns:
                print(f"    {category}: {len(category_patterns)}")

        return patterns

    def mine_all_experiments(self, experiment_files: List[str]) -> Dict:
        """Mine patterns from multiple experiments.

        Args:
            experiment_files: List of experiment result JSON filenames

        Returns:
            Dictionary mapping experiment names to detected patterns
        """
        all_patterns = {}

        for filename in experiment_files:
            patterns = self.mine_experiment(filename)
            all_patterns[filename] = patterns

        return all_patterns

    def generate_taxonomy(self) -> Dict:
        """Generate pattern taxonomy from mined patterns.

        Returns:
            Dictionary containing pattern taxonomy with frequencies
        """
        taxonomy = {}

        for pattern_key, stats in sorted(self.pattern_stats.items(),
                                         key=lambda x: x[1]['count'], reverse=True):
            category, pattern_type = pattern_key.split('/')

            if category not in taxonomy:
                taxonomy[category] = {}

            taxonomy[category][pattern_type] = {
                'frequency': stats['count'],
                'percentage': 0,  # Will be calculated below
                'representative_examples': stats['examples'][:3]  # Top 3 examples
            }

        # Calculate percentages within each category
        for category in taxonomy:
            total = sum(p['frequency'] for p in taxonomy[category].values())
            for pattern_type in taxonomy[category]:
                taxonomy[category][pattern_type]['percentage'] = \
                    (taxonomy[category][pattern_type]['frequency'] / total * 100) if total > 0 else 0

        return taxonomy

    def save_results(self, all_patterns: Dict, taxonomy: Dict, output_file: Path):
        """Save pattern mining results to JSON.

        Args:
            all_patterns: Dictionary of all mined patterns
            taxonomy: Pattern taxonomy
            output_file: Path to output JSON file
        """
        results = {
            'metadata': {
                'analysis': 'Paper 5D - Emergence Pattern Catalog',
                'experiments_analyzed': list(all_patterns.keys()),
                'total_experiments': len(all_patterns),
                'total_patterns': sum(sum(len(p) for p in patterns.values())
                                     for patterns in all_patterns.values())
            },
            'patterns_by_experiment': all_patterns,
            'taxonomy': taxonomy,
            'pattern_statistics': dict(self.pattern_stats)
        }

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to {output_file}")

    def print_summary(self, taxonomy: Dict):
        """Print pattern mining summary.

        Args:
            taxonomy: Pattern taxonomy dictionary
        """
        print("\n" + "="*70)
        print("PATTERN TAXONOMY SUMMARY")
        print("="*70)

        for category in taxonomy:
            print(f"\n{category.upper()} PATTERNS:")
            for pattern_type, stats in sorted(taxonomy[category].items(),
                                             key=lambda x: x[1]['frequency'],
                                             reverse=True):
                freq = stats['frequency']
                pct = stats['percentage']
                print(f"  {pattern_type}: {freq} occurrences ({pct:.1f}%)")

        print("\n" + "="*70)


def main():
    """Main execution function."""
    print("="*70)
    print("PAPER 5D: EMERGENCE PATTERN CATALOG - PATTERN MINING")
    print("="*70)
    print("\nAnalyzing existing experimental datasets for emergent NRM patterns...")

    # Setup paths
    # Use git repository for data source, dev workspace for output
    data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/data/results")

    # Initialize miner
    miner = PatternMiner(data_dir)

    # Experiments to analyze
    experiments = [
        'cycle171_fractal_swarm_bistability.json',
        'cycle175_high_resolution_transition.json',
        'cycle176_ablation_study_v4.json',
        'cycle177_h1_energy_pooling_results.json'
    ]

    # Mine patterns from all experiments
    all_patterns = miner.mine_all_experiments(experiments)

    # Generate taxonomy
    taxonomy = miner.generate_taxonomy()

    # Print summary
    miner.print_summary(taxonomy)

    # Save results
    output_file = output_dir / "paper5d_pattern_mining_results.json"
    miner.save_results(all_patterns, taxonomy, output_file)

    print(f"\nPattern mining complete! Found {len(miner.pattern_stats)} distinct pattern types.")
    print(f"Results saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
