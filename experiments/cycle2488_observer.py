"""
Cycle 2488: The Observer (Gate 116)
Role: The Data Scientist
Responsibility: Analyze Garden Dynamics.

Objective:
- Load cycle2487_garden.csv.
- Calculate Correlation (Season vs Prey, Prey vs Predator).
- Generate ASCII plots for immediate feedback.
"""

import sys
import os
import csv
import math
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def analyze_garden():
    print("🔭 CYCLE 2488: THE OBSERVER")
    
    csv_path = Path("experiments/results/cycle2487_garden.csv")
    if not csv_path.exists():
        print(f"❌ Error: {csv_path} not found.")
        return

    # Load Data
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'tick': int(row['tick']),
                'season': float(row['season_factor']),
                'prey': int(row['prey_pop']),
                'pred': int(row['pred_pop'])
            })
            
    print(f"📊 Loaded {len(data)} data points.")
    
    # Time Series Analysis
    seasons = [d['season'] for d in data]
    prey = [d['prey'] for d in data]
    pred = [d['pred'] for d in data]
    
    # 1. Correlation Analysis
    def correlation(x, y):
        n = len(x)
        if n != len(y): return 0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        den_x = sum((xi - mean_x)**2 for xi in x)
        den_y = sum((yi - mean_y)**2 for yi in y)
        
        if den_x == 0 or den_y == 0: return 0
        return numerator / math.sqrt(den_x * den_y)

    corr_season_prey = correlation(seasons, prey)
    corr_prey_pred = correlation(prey, pred)
    
    print("\n📈 CORRELATION MATRIX:")
    print(f"   Season -> Prey: {corr_season_prey:.4f}")
    print(f"   Prey -> Predator: {corr_prey_pred:.4f}")
    
    # 2. Phase Space Analysis (ASCII)
    print("\n🌀 PHASE SPACE (Prey vs Predator):")
    # Normalize to 10x10 grid
    max_prey = max(prey) if prey else 1
    max_pred = max(pred) if pred else 1
    min_prey = min(prey) if prey else 0
    min_pred = min(pred) if pred else 0
    
    grid_size = 10
    grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
    
    for p, w in zip(prey, pred):
        x = int((p - min_prey) / (max_prey - min_prey + 0.001) * (grid_size - 1))
        y = int((w - min_pred) / (max_pred - min_pred + 0.001) * (grid_size - 1))
        # Invert Y for printing
        grid[grid_size - 1 - y][x] = '#'
        
    for row in grid:
        print("   " + "".join(row))
    print(f"   X: Prey ({min_prey}-{max_prey}), Y: Pred ({min_pred}-{max_pred})")

    # 3. Interpretation
    print("\n🧠 INTERPRETATION:")
    if abs(corr_season_prey) > 0.5:
        print("   ✅ Strong Seasonality detected in Prey population.")
    else:
        print("   ⚠️ Weak Seasonality. Prey might be capacity-limited rather than food-limited.")
        
    if abs(corr_prey_pred) > 0.5:
        print("   ✅ Strong Predator-Prey coupling.")
    else:
        print("   ⚠️ Weak Coupling. Predators might be space-limited.")

if __name__ == "__main__":
    analyze_garden()
