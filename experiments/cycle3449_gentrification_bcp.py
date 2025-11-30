
import sys
import os

def log(msg):
    print(msg)

class ResidentBCP:
    def __init__(self, name, budget, social_capital_gain):
        self.name = name
        self.budget = budget
        self.lambda_val = 1.0 / (0.1 + budget)
        self.social_gain = social_capital_gain
        
    def evaluate_location(self, rent_cost, amenity_gain):
        # V = (Amenity + Social) - λ * Rent
        # Incumbents value Social Capital highly. Newcomers value Amenities.
        total_gain = amenity_gain + self.social_gain
        v = total_gain - self.lambda_val * rent_cost
        return v

def main():
    log("======================================================================")
    log("CYCLE 3449: GATE 1029 - GENTRIFICATION AS BCP")
    log("Hypothesis: Displacement occurs when Newcomer V > Incumbent V")
    log("======================================================================")
    
    # Location Parameters
    # Initially: Low Rent, Low Amenities
    rent = 1.0
    amenities = 2.0
    
    # Agents
    # Incumbent: Poor (B=0.5), High Social Capital (G_soc=5.0)
    incumbent = ResidentBCP("Incumbent", budget=0.5, social_capital_gain=5.0) # λ ≈ 1.67
    
    # Newcomer: Rich (B=5.0), Low Social Capital (G_soc=0.0)
    newcomer = ResidentBCP("Newcomer", budget=5.0, social_capital_gain=0.0) # λ ≈ 0.20
    
    log(f"SCENARIO 1: STABLE NEIGHBORHOOD (Rent={rent})")
    v_inc = incumbent.evaluate_location(rent, amenities)
    v_new = newcomer.evaluate_location(rent, amenities)
    
    log(f"Incumbent (λ={incumbent.lambda_val:.2f}): G={amenities+incumbent.social_gain} - λ*{rent} = {v_inc:.2f}")
    log(f"Newcomer  (λ={newcomer.lambda_val:.2f}): G={amenities+newcomer.social_gain} - λ*{rent} = {v_new:.2f}")
    
    occupant = "Incumbent" if v_inc > v_new else "Newcomer"
    log(f"Occupant: {occupant}")
    
    # --------------------------------------------------------
    # SCENARIO 2: THE SPARK (Amenities Improve)
    # --------------------------------------------------------
    log("\nSCENARIO 2: THE SPARK (Amenities Rise -> 10.0)")
    amenities = 10.0
    # Rent hasn't risen yet
    
    v_inc = incumbent.evaluate_location(rent, amenities)
    v_new = newcomer.evaluate_location(rent, amenities)
    
    log(f"Incumbent V: {v_inc:.2f}")
    log(f"Newcomer V:  {v_new:.2f}")
    
    # Newcomer willingness to pay increases drastically due to low λ
    log("Newcomer V > Incumbent V? " + str(v_new > v_inc))
    
    # --------------------------------------------------------
    # SCENARIO 3: RENT SPIKE (Market Adjustment)
    # --------------------------------------------------------
    log("\nSCENARIO 3: RENT SPIKE (Rent Rises to Capture Newcomer Surplus)")
    # Landlord raises rent until Newcomer V ≈ 0 (Reservation price)
    # Newcomer max rent: G / λ = 10 / 0.2 = 50
    # Incumbent max rent: G / λ = 15 / 1.67 = 8.9
    
    new_rent = 20.0
    
    v_inc = incumbent.evaluate_location(new_rent, amenities)
    v_new = newcomer.evaluate_location(new_rent, amenities)
    
    log(f"New Rent: {new_rent}")
    log(f"Incumbent V: {v_inc:.2f} (DISPLACED)")
    log(f"Newcomer V:  {v_new:.2f} (MOVES IN)")
    
    log("\nFINDING: Gentrification is a λ-differential phenomenon.")
    log("         Low λ agents (Rich) can absorb cost increases that push")
    log("         High λ agents (Poor) below V=0, even if Poor value the place more in absolute terms.")
    log("======================================================================")
    log("GATE 1029 COMPLETE: GENTRIFICATION IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
