"""
CYCLE 323: High-Resolution Inverse Cymatics
Objective: Scale the Inverse Solver to 128x128 grid and 16 emitters to hold a complex shape ("Cross").
"""
import numpy as np
import json
import os
import sys
import random
import copy

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.target_field import TargetField

# --- Shared Classes (Redefined/Enhanced for this experiment) ---

class Emitter:
    def __init__(self, x, y, frequency, phase, amplitude=1.0):
        self.x = x
        self.y = y
        self.frequency = frequency
        self.phase = phase
        self.amplitude = amplitude

    def to_dict(self):
        return {
            "x": self.x, "y": self.y,
            "frequency": self.frequency, "phase": self.phase,
            "amplitude": self.amplitude
        }

class CymaticSimulation:
    def __init__(self, width, height, emitters, wave_speed=1.0):
        self.width = width
        self.height = height
        self.emitters = emitters
        self.wave_speed = wave_speed

    def calculate_density_field(self):
        # Vectorized calculation for performance on larger grid
        y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
        total_amplitude = np.zeros((self.height, self.width))
        
        for emitter in self.emitters:
            distance = np.sqrt((x_coords - emitter.x)**2 + (y_coords - emitter.y)**2)
            k = 2 * np.pi * emitter.frequency / self.wave_speed
            total_amplitude += emitter.amplitude * np.cos(k * distance + emitter.phase)
            
        max_amp = sum(e.amplitude for e in self.emitters)
        if max_amp == 0: max_amp = 1.0
        
        density_field = (total_amplitude + max_amp) / (2 * max_amp)
        return np.clip(density_field, 0.0, 1.0)

class Genome:
    def __init__(self, num_emitters, bounds):
        self.emitters = []
        self.bounds = bounds
        for _ in range(num_emitters):
            self.emitters.append(self._random_emitter())
            
    def _random_emitter(self):
        return Emitter(
            x=random.uniform(self.bounds['x'][0], self.bounds['x'][1]),
            y=random.uniform(self.bounds['y'][0], self.bounds['y'][1]),
            frequency=random.uniform(self.bounds['f'][0], self.bounds['f'][1]),
            phase=random.uniform(self.bounds['p'][0], self.bounds['p'][1]),
            amplitude=1.0
        )

    def mutate(self, rate, sigma):
        for emitter in self.emitters:
            if random.random() < rate:
                emitter.x += random.gauss(0, sigma * (self.bounds['x'][1] - self.bounds['x'][0]))
                emitter.y += random.gauss(0, sigma * (self.bounds['y'][1] - self.bounds['y'][0]))
                emitter.frequency += random.gauss(0, sigma * (self.bounds['f'][1] - self.bounds['f'][0]))
                emitter.phase += random.gauss(0, sigma * np.pi)
                
                # Clamp
                emitter.x = np.clip(emitter.x, self.bounds['x'][0], self.bounds['x'][1])
                emitter.y = np.clip(emitter.y, self.bounds['y'][0], self.bounds['y'][1])
                emitter.frequency = np.clip(emitter.frequency, self.bounds['f'][0], self.bounds['f'][1])
                emitter.phase = np.clip(emitter.phase, self.bounds['p'][0], self.bounds['p'][1])

class InverseCymaticsGA:
    def __init__(self, target_field, population_size=100, num_emitters=16, mutation_rate=0.1):
        self.target_field = target_field
        self.pop_size = population_size
        self.num_emitters = num_emitters
        self.mutation_rate = mutation_rate
        self.bounds = {
            'x': (0, target_field.width),
            'y': (0, target_field.height),
            'f': (0.1, 1.0),
            'p': (0, 2 * np.pi)
        }
        self.population = [Genome(num_emitters, self.bounds) for _ in range(population_size)]
        self.best_genome = None
        self.best_fitness = -1.0
        self.best_error = float('inf')
        
    def evaluate(self, genome):
        sim = CymaticSimulation(self.target_field.width, self.target_field.height, genome.emitters)
        generated_field = sim.calculate_density_field()
        error = self.target_field.calculate_error(generated_field)
        fitness = 1.0 / (1.0 + error)
        return fitness, error

    def evolve(self, generations=200):
        history = []
        
        for gen in range(generations):
            # Adaptive Mutation: Decrease rate and sigma as generations progress
            progress = gen / generations
            current_mutation_rate = self.mutation_rate * (1.0 - 0.5 * progress)
            current_sigma = 0.1 * (1.0 - 0.8 * progress) # Start at 0.1, end at 0.02
            
            # Evaluate
            fitness_scores = []
            for genome in self.population:
                fitness, error = self.evaluate(genome)
                fitness_scores.append((fitness, genome, error))
                
                if fitness > self.best_fitness:
                    self.best_fitness = fitness
                    self.best_genome = copy.deepcopy(genome)
                    self.best_error = error
            
            # Sort
            fitness_scores.sort(key=lambda x: x[0], reverse=True)
            
            avg_fitness = sum(f for f, g, e in fitness_scores) / self.pop_size
            
            if gen % 10 == 0:
                print(f"Gen {gen:3d}: Best Error = {self.best_error:.6f}, Avg Fitness = {avg_fitness:.4f}")
            
            # Selection & Crossover
            new_pop = []
            
            # Elitism (Keep top 5)
            for i in range(5):
                new_pop.append(copy.deepcopy(fitness_scores[i][1]))
            
            while len(new_pop) < self.pop_size:
                parent1 = self._tournament(fitness_scores)
                parent2 = self._tournament(fitness_scores)
                child = self._crossover(parent1, parent2)
                child.mutate(rate=current_mutation_rate, sigma=current_sigma)
                new_pop.append(child)
                
            self.population = new_pop
            
        return {
            'genome': [e.to_dict() for e in self.best_genome.emitters],
            'error': self.best_error,
            'fitness': self.best_fitness
        }

    def _tournament(self, scores, k=5):
        candidates = random.sample(scores, k)
        return max(candidates, key=lambda x: x[0])[1]

    def _crossover(self, p1, p2):
        child = Genome(self.num_emitters, self.bounds)
        for i in range(self.num_emitters):
            if random.random() < 0.5:
                child.emitters[i] = copy.deepcopy(p1.emitters[i])
            else:
                child.emitters[i] = copy.deepcopy(p2.emitters[i])
        return child

def main():
    print("CYCLE 323: HIGH-RESOLUTION INVERSE CYMATICS")
    print("===========================================")
    
    # 1. Define Target (Cross)
    width, height = 128, 128
    target = TargetField(width, height)
    
    # Create Cross Shape
    # Vertical Bar
    target.set_square(64, 64, 80, density=0.0) # Clear first? No, set_square overwrites.
    # Actually, TargetField logic is additive or overwrites? It sets.
    # Let's manually build a cross using set_square logic but we need rectangular bars.
    # TargetField only has set_square and set_circle.
    # We can simulate a cross by setting points or extending TargetField.
    # Or just use overlapping squares to make a thick cross.
    
    # Vertical Bar (Approximated by small squares or just direct array manipulation if allowed, 
    # but let's stick to API if possible. Actually, I can just modify the field directly since I imported the class)
    # Wait, TargetField.field is accessible.
    
    target.field[:, :] = 0.0 # Reset
    
    # Vertical Bar
    target.field[24:104, 56:72] = 1.0
    # Horizontal Bar
    target.field[56:72, 24:104] = 1.0
    
    print("Target: Cross Shape in 128x128 Grid")
    target.display(scale=1) # Might be too large for console, but let's try
    
    # 2. Initialize Solver
    print("\nInitializing GA (Pop=100, Emitters=16, Gen=200)...")
    solver = InverseCymaticsGA(target, population_size=100, num_emitters=16, mutation_rate=0.2)
    
    # 3. Evolve
    print("\n--- Evolution Start ---")
    result = solver.evolve(generations=200)
    print("--- Evolution Complete ---")
    
    # 4. Results
    print(f"\nBest Error: {result['error']:.6f}")
    
    # 5. Visualize Result
    best_emitters = [Emitter(**p) for p in result['genome']]
    sim = CymaticSimulation(width, height, best_emitters)
    result_field = sim.calculate_density_field()
    
    result_display = TargetField(width, height)
    result_display.field = result_field
    print("\n--- Generated Pattern ---")
    result_display.display(scale=1)
    
    # 6. Save
    results_data = {
        "cycle": 323,
        "target": "Cross",
        "best_error": result['error'],
        "emitters": result['genome']
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c323_high_res_inverse.json", "w") as f:
        json.dump(results_data, f, indent=2)
        
    if result['error'] < 0.12:
        print("\n>> SUCCESS: High-Res GA converged significantly.")
    else:
        print("\n>> RESULT: Convergence limited. Higher complexity requires more compute/emitters.")

if __name__ == "__main__":
    main()
