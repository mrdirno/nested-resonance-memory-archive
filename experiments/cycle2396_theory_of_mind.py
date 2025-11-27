"""
Cycle 2396: Theory of Mind (Recursive Beliefs)
Gate 20: Predictive Empathy
Objective: Implement agents that model other agents' beliefs to predict their actions.
"""

import random
import sys

class BeliefState:
    """Represents what an Agent believes about the world."""
    def __init__(self, location_of_object):
        self.location = location_of_object

class Agent:
    def __init__(self, name):
        self.name = name
        self.beliefs = BeliefState(location_of_object="Basket") # Reality initially
        self.mental_models = {} # What I believe others believe: {agent_name: BeliefState}
        
    def perceive(self, location):
        """Update own belief based on observation."""
        self.beliefs.location = location
        print(f"[{self.name}] Sees object in {location}.")
        
    def model_other(self, other_agent, observed_location=None):
        """
        Update mental model of other agent.
        If observed_location is None, assumes other agent holds their last known belief.
        """
        if other_agent.name not in self.mental_models:
            # Default assumption: They know what I know (Naive Realism)
            self.mental_models[other_agent.name] = BeliefState(self.beliefs.location)
            
        if observed_location:
            # I saw them see it
            self.mental_models[other_agent.name].location = observed_location
            print(f"[{self.name}] Knows {other_agent.name} saw object in {observed_location}.")
        else:
            # I didn't see them see the change. I assume they still believe the old location.
            # This is the critical "False Belief" step.
            pass

    def predict_action(self, other_agent):
        """Predict where other_agent will look."""
        if other_agent.name in self.mental_models:
            believed_loc = self.mental_models[other_agent.name].location
            return believed_loc
        return "Unknown"

def run_sally_anne_test():
    print("Cycle 2396: Theory of Mind Verification (Sally-Anne Test)")
    print("========================================================")
    
    # 1. Setup
    sally = Agent("Sally")
    anne = Agent("Anne")
    observer = Agent("Observer") # The system/test runner or a smart agent
    
    object_location = "Basket"
    print(f"1. Object is in {object_location}.")
    sally.perceive(object_location)
    anne.perceive(object_location)
    
    # Observer models both
    observer.model_other(sally, object_location)
    observer.model_other(anne, object_location)
    
    # 2. Sally leaves
    print("\n2. Sally leaves the room.")
    
    # 3. Anne moves object
    object_location = "Box"
    print(f"3. Anne moves object to {object_location}.")
    anne.perceive(object_location)
    
    # Observer sees Anne move it, but knows Sally didn't see it
    observer.perceive(object_location) 
    observer.model_other(anne, object_location) # Anne saw it
    # Observer does NOT update model of Sally because Sally was absent
    
    # 4. Sally returns
    print("\n4. Sally returns.")
    
    # 5. Prediction
    print("\n--- Prediction Step ---")
    prediction = observer.predict_action(sally)
    reality = object_location
    
    print(f"Observer predicts Sally will look in: {prediction}")
    print(f"Object is actually in: {reality}")
    
    if prediction == "Basket" and reality == "Box":
        print("PASS: Observer correctly modeled Sally's False Belief.")
        print("Theory of Mind Operational.")
    else:
        print(f"FAIL: Prediction {prediction} matches Reality {reality} (Naive Realism) or is invalid.")
        sys.exit(1)

if __name__ == "__main__":
    run_sally_anne_test()
