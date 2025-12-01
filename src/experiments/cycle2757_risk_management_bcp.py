"""
Cycle 2757: Risk Management as BCP (The Uncertainty Budget)
============================================================

Investigation: Is financial risk management (e.g., diversification, hedging, insurance) a BCP process? Do investors balance the gain of higher returns against the cost of risk (volatility, potential loss), modulated by their risk aversion and market uncertainty (λ)?

Hypothesis:
Financial risk management is a BCP-optimal strategy for capital allocation under uncertainty. The "optimal" investment portfolio dynamically adapts to an investor's risk aversion (λ) and prevailing market conditions.
V(portfolio) = Gain(Expected_Return) - λ(Risk_Aversion/Market_Uncertainty) * Cost(Volatility + Potential_Loss + Hedging_Fees).

1. High-Risk, High-Reward: High Potential Gain, High Volatility/Loss. Optimal under low λ (low risk aversion, low market uncertainty).
2. Moderate-Risk, Moderate-Reward (Diversified): Balanced Gain and Risk. Optimal under moderate λ.
3. Low-Risk, Low-Reward: Low Potential Gain, High Capital Preservation. Optimal under high λ (high risk aversion, high market uncertainty).

We simulate an investor choosing an investment portfolio.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2757: Risk Management BCP...")
    
    # Investment Portfolios
    portfolios = [
        # High-Risk: High return, high volatility/loss potential
        {'name': "High-Risk", 'expected_return': 15.0, 'volatility_cost': 10.0, 'potential_loss_cost': 50.0, 'avg_return': 0.15},
        # Moderate-Risk (Diversified): Balanced return and risk
        {'name': "Moderate-Risk", 'expected_return': 8.0, 'volatility_cost': 3.0, 'potential_loss_cost': 10.0, 'avg_return': 0.08}, 
        # Low-Risk: Low return, high capital preservation
        {'name': "Low-Risk", 'expected_return': 3.0, 'volatility_cost': 1.0, 'potential_loss_cost': 2.0, 'avg_return': 0.03}
    ]
    
    # Risk Aversion/Market Uncertainty (λ) - Represents investor's psychological tolerance for risk and objective market volatility.
    # Higher λ means higher cost for risk.
    lambdas = np.linspace(0.1, 5.0, 50) # From low risk aversion/uncertainty to high risk aversion/uncertainty
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_portfolio = None
        
        for port in portfolios:
            # Total Risk Cost = Volatility_Cost + Potential_Loss_Cost (ignoring hedging fees for simplicity)
            total_risk_cost = port['volatility_cost'] + port['potential_loss_cost']
            
            # V = Gain(Expected_Return) - λ * Total_Risk_Cost
            v = port['expected_return'] - (lambd * total_risk_cost)
            
            if v > best_v:
                best_v = v
                chosen_portfolio = port
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_portfolio['name'],
            'chosen_avg_return': chosen_portfolio['avg_return'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2757_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen average return against lambda
    plt.plot(df['lambda'], df['chosen_avg_return'], marker='o', linestyle='-', color='blue')
    plt.title('Investment Portfolio Return vs Risk Aversion/Market Uncertainty (λ)')
    plt.xlabel('Risk Aversion / Market Uncertainty (λ)')
    plt.ylabel('Chosen Portfolio Average Return')
    plt.ylim(0, 0.2)
    plt.grid(True)
    
    # Annotate transitions
    portfolio_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in portfolio_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_avg_return'] + 0.01, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2757_risk_management_budget.png")
    
    # Analysis
    print("Cycle 2757 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "High-Risk" and high_lambda_choice == "Low-Risk":
        print("HYPOTHESIS CONFIRMED: Financial risk management is a BCP-optimal strategy.")
        print("Investment portfolios adapt to investor risk aversion and market uncertainty.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
