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

        # Look for population dynamics in 'experiments' array (actual data format)
        if 'experiments' in data:
            # Group by frequency to compute variance
            freq_groups = defaultdict(list)
            for exp in data['experiments']:
                freq = exp.get('frequency', 'unknown')
                agent_count = exp.get('final_agent_count', 0)
                freq_groups[freq].append(agent_count)

            # Analyze each frequency group
            for freq, agent_counts in freq_groups.items():
                if len(agent_counts) > 1:
                    mean_pop = np.mean(agent_counts)
                    variance = np.var(agent_counts)

                    # Clustering pattern: High population with low variance
                    if mean_pop > 50 and variance < 100:
                        patterns.append({
                            'type': 'clustering',
                            'strength': mean_pop / (variance + 1),
                            'frequency': freq,
                            'mean_population': mean_pop,
                            'variance': variance,
                            'n_samples': len(agent_counts)
                        })

                    # Dispersion pattern: Low population with high variance
                    elif mean_pop < 30 and variance > 50:
                        patterns.append({
                            'type': 'dispersion',
                            'strength': variance / (mean_pop + 1),
                            'frequency': freq,
                            'mean_population': mean_pop,
                            'variance': variance,
                            'n_samples': len(agent_counts)
                        })

                    # Fragmentation pattern: Medium population with high variance
                    elif 30 <= mean_pop <= 50 and variance > 100:
                        patterns.append({
                            'type': 'fragmentation',
                            'strength': variance / mean_pop,
                            'frequency': freq,
                            'mean_population': mean_pop,
                            'variance': variance,
                            'n_samples': len(agent_counts)
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

        # Look for time series data in 'experiments' array
        if 'experiments' in data:
            # Group by frequency and analyze composition events
            freq_groups = defaultdict(list)
            for exp in data['experiments']:
                freq = exp.get('frequency', 'unknown')
                comp_events = exp.get('avg_composition_events', 0)
                freq_groups[freq].append(comp_events)

            # Analyze temporal dynamics within each frequency
            for freq, comp_events in freq_groups.items():
                if len(comp_events) > 1:
                    mean_events = np.mean(comp_events)
                    std_events = np.std(comp_events)

                    # Steady state pattern: Low variance in composition events
                    if std_events < 5 and mean_events > 20:
                        patterns.append({
                            'type': 'steady_state',
                            'stability': mean_events / (std_events + 0.1),
                            'frequency': freq,
                            'mean_events': mean_events,
                            'std_events': std_events,
                            'n_samples': len(comp_events)
                        })

                    # Oscillation pattern: Medium variance (dynamic but regular)
                    elif 5 <= std_events <= 20 and mean_events > 50:
                        patterns.append({
                            'type': 'oscillation',
                            'amplitude': std_events,
                            'frequency': freq,
                            'mean_events': mean_events,
                            'std_events': std_events,
                            'n_samples': len(comp_events)
                        })

                    # Burst pattern: Very high variance (intermittent activity)
                    elif std_events > 20:
                        patterns.append({
                            'type': 'burst',
                            'intensity': std_events,
                            'frequency': freq,
                            'mean_events': mean_events,
                            'std_events': std_events,
                            'n_samples': len(comp_events)
                        })

        return patterns

    def detect_interaction_patterns(self, data: Dict) -> List[Dict]:
        """Detect interaction patterns (basin preferences, frequency responses).

        Args:
            data: Experimental data dictionary

        Returns:
            List of detected interaction patterns
        """
        patterns = []

        # Look for basin preferences in experiments
        if 'experiments' in data:
            # Count basin occurrences
            basin_counts = Counter()
            freq_basin = defaultdict(lambda: Counter())

            for exp in data['experiments']:
                basin = exp.get('basin', 'unknown')
                freq = exp.get('frequency', 'unknown')
                if basin != 'unknown':
                    basin_counts[basin] += 1
                    freq_basin[freq][basin] += 1

            # Detect strong basin preference
            if len(basin_counts) >= 2:
                total = sum(basin_counts.values())
                dominant_basin = basin_counts.most_common(1)[0]
                if dominant_basin[1] / total > 0.8:
                    patterns.append({
                        'type': 'basin_dominance',
                        'dominant_basin': dominant_basin[0],
                        'frequency': dominant_basin[1] / total,
                        'total_experiments': total,
                        'basin_counts': dict(basin_counts)
                    })

            # Detect frequency-dependent basin preference
            for freq, basins in freq_basin.items():
                if len(basins) >= 2:
                    total_freq = sum(basins.values())
                    dominant = basins.most_common(1)[0]
                    if dominant[1] / total_freq > 0.7:
                        patterns.append({
                            'type': 'frequency_basin_preference',
                            'frequency': freq,
                            'preferred_basin': dominant[0],
                            'preference_strength': dominant[1] / total_freq,
                            'n_experiments': total_freq
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

        # Look for pattern persistence across frequencies
        if 'experiments' in data:
            # Sort experiments by frequency
            freq_pops = []
            experiments_sorted = sorted(data['experiments'], key=lambda x: x.get('frequency', 0))

            # Group by frequency and get mean population
            freq_groups = defaultdict(list)
            for exp in experiments_sorted:
                freq = exp.get('frequency', 0)
                pop = exp.get('final_agent_count', 0)
                freq_groups[freq].append(pop)

            # Get mean population per frequency
            for freq in sorted(freq_groups.keys()):
                mean_pop = np.mean(freq_groups[freq])
                freq_pops.append(mean_pop)

            if len(freq_pops) >= 2:
                # Retention pattern: Consistent values across frequencies
                pop_std = np.std(freq_pops)
                pop_mean = np.mean(freq_pops)

                if pop_std < 10 and pop_mean > 10:
                    patterns.append({
                        'type': 'retention',
                        'consistency': pop_mean / (pop_std + 0.1),
                        'mean': pop_mean,
                        'std': pop_std,
                        'n_frequencies': len(freq_pops)
                    })

                # Decay pattern: Declining trend across frequencies
                if len(freq_pops) >= 3:
                    trend = np.polyfit(range(len(freq_pops)), freq_pops, 1)[0]
                    if trend < -2:
                        patterns.append({
                            'type': 'decay',
                            'rate': abs(trend),
                            'initial': freq_pops[0],
                            'final': freq_pops[-1],
                            'n_frequencies': len(freq_pops)
                        })

                    # Transfer pattern: Increasing trend
                    elif trend > 2:
                        patterns.append({
                            'type': 'transfer',
                            'rate': trend,
                            'initial': freq_pops[0],
                            'final': freq_pops[-1],
                            'n_frequencies': len(freq_pops)
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
