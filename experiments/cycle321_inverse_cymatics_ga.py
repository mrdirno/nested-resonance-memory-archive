"""
CYCLE 321: Inverse Cymatics (Genetic Algorithm)
Objective: Use a Genetic Algorithm to find the emitter configuration that generates a target pattern.
Target: Square.
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

# --- Shared Cymatics Classes (Redefined for self-containment) ---

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
        density_field = np.zeros((self.height, self.width), dtype=float)
        y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
        
        total_amplitude = np.zeros((self.height, self.width))
        
        for emitter in self.emitters:
            distance = np.sqrt((x_coords - emitter.x)**2 + (y_coords - emitter.y)**2)
            k = 2 * np.pi * emitter.frequency / self.wave_speed
            total_amplitude += emitter.amplitude * np.cos(k * distance + emitter.phase)
            
        # Normalize to 0-1 range
        # Max possible amplitude is sum of all emitter amplitudes
        max_amp = sum(e.amplitude for e in self.emitters)
        if max_amp == 0: max_amp = 1.0
        
        # Shift and scale: -Max to +Max -> 0 to 1
        # (Amp + Max) / (2 * Max)
        density_field = (total_amplitude + max_amp) / (2 * max_amp)
        return np.clip(density_field, 0.0, 1.0)

# --- Genetic Algorithm ---

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
            amplitude=1.0 # Fixed amplitude for now
        )

    def mutate(self, rate=0.1, sigma=0.1):
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

class GeneticSolver:
    def __init__(self, target_field, population_size=50, num_emitters=4):
        self.target_field = target_field
        self.pop_size = population_size
        self.num_emitters = num_emitters
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

    def evolve(self, generations=100):
        history = []
        
        for gen in range(generations):
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
            
            # Log
            avg_fitness = sum(f for f, g, e in fitness_scores) / self.pop_size
            history.append({
                "gen": gen,
                "best_error": self.best_error,
                "avg_fitness": avg_fitness
            })
            
            if gen % 10 == 0:
                print(f"Gen {gen:3d}: Best Error = {self.best_error:.6f}, Avg Fitness = {avg_fitness:.4f}")
            
            # Selection (Tournament) & Crossover
            new_pop = []
            
            # Elitism (Keep top 2)
            new_pop.append(copy.deepcopy(fitness_scores[0][1]))
            new_pop.append(copy.deepcopy(fitness_scores[1][1]))
            
            while len(new_pop) < self.pop_size:
                parent1 = self._tournament(fitness_scores)
                parent2 = self._tournament(fitness_scores)
                child = self._crossover(parent1, parent2)
                child.mutate(rate=0.2, sigma=0.1)
                new_pop.append(child)
                
            self.population = new_pop
            
        return self.best_genome, history

    def _tournament(self, scores, k=3):
        candidates = random.sample(scores, k)
        return max(candidates, key=lambda x: x[0])[1]

    def _crossover(self, p1, p2):
        child = Genome(self.num_emitters, self.bounds)
        # Uniform crossover of emitters
        for i in range(self.num_emitters):
            if random.random() < 0.5:
                child.emitters[i] = copy.deepcopy(p1.emitters[i])
            else:
                child.emitters[i] = copy.deepcopy(p2.emitters[i])
        return child

def main():
    print("CYCLE 321: INVERSE CYMATICS (GENETIC ALGORITHM)")
    print("===============================================")
    
    # 1. Define Target (Square)
    width, height = 50, 50
    target = TargetField(width, height)
    target.set_square(25, 25, 20, density=1.0)
    
    print("Target: Square (Size 20) in 50x50 Grid")
    target.display()
    
    # 2. Initialize Solver
    solver = GeneticSolver(target, population_size=50, num_emitters=4)
    
    # 3. Evolve
    print("\n--- Evolution Start ---")
    best_genome, history = solver.evolve(generations=100)
    print("--- Evolution Complete ---")
    
    # 4. Results
    print(f"\nBest Error: {solver.best_error:.6f}")
    print("Best Configuration:")
    for i, e in enumerate(best_genome.emitters):
        print(f"  Emitter {i}: x={e.x:.1f}, y={e.y:.1f}, f={e.frequency:.2f}, p={e.phase:.2f}")
        
    # 5. Visualize Result
    sim = CymaticSimulation(width, height, best_genome.emitters)
    result_field = sim.calculate_density_field()
    
    # Create a temp TargetField just to use its display method
    result_display = TargetField(width, height)
    result_display.field = result_field
    print("\n--- Generated Pattern ---")
    result_display.display()
    
    # 6. Save
    results = {
        "cycle": 321,
        "target": "Square",
        "best_error": solver.best_error,
        "emitters": [e.to_dict() for e in best_genome.emitters],
        "history": history
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c321_inverse_cymatics.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if solver.best_error < 0.15: # Threshold for "Soft Success"
        print("\n>> SUCCESS: GA converged to a reasonable approximation.")
    else:
        print("\n>> RESULT: GA struggled to find a perfect match (Expected for complex inverse problem).")

if __name__ == "__main__":
    main()
