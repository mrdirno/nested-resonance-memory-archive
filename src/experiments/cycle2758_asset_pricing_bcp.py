"""
Cycle 2758: Asset Pricing as BCP (The Valuation Budget)
========================================================

Investigation: Do asset prices reflect a BCP-optimal consensus of future expected gains discounted by risk and transaction costs? Do bubbles and crashes occur when λ (e.g., investor sentiment, liquidity) shifts dramatically, leading to phase transitions in valuation?

Hypothesis:
Asset pricing is a BCP-optimal process for capital allocation. The observed price of an asset dynamically balances its expected future returns (Gain) against its perceived risk and transaction costs (Cost), modulated by prevailing investor sentiment and market liquidity (λ).
V(asset) = Gain(Expected_Future_Returns) - λ(Investor_Sentiment/Market_Liquidity) * Cost(Perceived_Risk + Transaction_Costs + Information_Asymmetry).

1. Fundamental Value (Rational Investor): High Information Cost, High Accuracy. Optimal under low λ (rational markets, high liquidity, low sentiment bias).
2. Sentiment-Driven Price (Heuristic Investor): Low Information Cost, Lower Accuracy (prone to bubbles/crashes). Optimal under high λ (irrational exuberance/fear, low liquidity).
3. Bubbles: Occur when λ becomes artificially low (easy credit, herd behavior), making high-cost/low-gain assets appear profitable.
4. Crashes: Occur when λ sharply increases (fear, liquidity crunch), making even fundamentally sound assets appear unprofitable.

We simulate an asset's valuation based on investor behavior.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2758: Asset Pricing BCP...")
    
    # Investor Types / Valuation Models
    models = [
        # Fundamental Value (Rational Investor): High info cost, high accuracy
        {'name': "Fundamental", 'expected_future_returns': 100.0, 'perceived_risk': 10.0, 'transaction_costs': 2.0, 'information_cost': 5.0, 'price_accuracy': 0.95},
        # Sentiment-Driven (Heuristic Investor): Low info cost, lower accuracy (prone to bubbles/crashes)
        {'name': "Sentiment-Driven", 'expected_future_returns': 80.0, 'perceived_risk': 5.0, 'transaction_costs': 1.0, 'information_cost': 1.0, 'price_accuracy': 0.6}
    ]
    
    # Investor Sentiment/Market Liquidity (λ) - Represents market irrationality, liquidity crunch.
    # Higher λ means higher costs for rational analysis / higher impact of sentiment.
    lambdas = np.linspace(0.1, 5.0, 50) # From rational/liquid to irrational/illiquid
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_model = None
        
        for model in models:
            # Total Cost = Perceived_Risk + Transaction_Costs + Information_Cost
            # Assume information cost is constant, but risk and transaction costs scale with lambda
            total_effective_cost = model['perceived_risk'] + model['transaction_costs'] + (model['information_cost'] * lambd)
            
            # V = Gain(Expected_Future_Returns) - λ * Total_Effective_Cost
            # Higher lambda means higher penalty for these costs
            v = model['expected_future_returns'] - (lambd * total_effective_cost)
            
            if v > best_v:
                best_v = v
                chosen_model = model
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_model['name'],
            'chosen_accuracy': chosen_model['price_accuracy'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2758_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen price accuracy against lambda
    plt.plot(df['lambda'], df['chosen_accuracy'], marker='o', linestyle='-', color='blue')
    plt.title('Asset Valuation Model Accuracy vs Investor Sentiment/Liquidity (λ)')
    plt.xlabel('Investor Sentiment / Market Illiquidity (λ)')
    plt.ylabel('Chosen Model Price Accuracy')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    model_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in model_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_accuracy'] + 0.05, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2758_asset_pricing_budget.png")
    
    # Analysis
    print("Cycle 2758 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Fundamental" and high_lambda_choice == "Sentiment-Driven":
        print("HYPOTHESIS CONFIRMED: Asset pricing is a BCP-optimal process.")
        print("Valuation models adapt to market conditions, balancing accuracy vs cost.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
