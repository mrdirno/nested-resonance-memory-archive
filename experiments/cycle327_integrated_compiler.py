"""
CYCLE 327: Integrated Matter Compiler
Objective: Combine Inverse Cymatics (GA) with Material Physics (Viscosity + Thresholding)
to solve for a complex shape (Square Donut).
"""
import numpy as np
import json
import os
import sys
import random
import copy
import scipy.ndimage

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.target_field import TargetField

# --- Physics Classes ---

class ViscousField:
    def __init__(self, width, height, viscosity=0.1):
        self.width = width
        self.height = height
        self.viscosity = viscosity
        
    def apply(self, field, iterations=1):
        # Gaussian blur approximates diffusion
        return scipy.ndimage.gaussian_filter(field, sigma=self.viscosity)

class ThresholdMatter:
    def __init__(self, threshold=0.5, sharpness=10.0):
        self.threshold = threshold
        self.sharpness = sharpness
        
    def apply_sigmoid(self, field):
        # Continuous Sigmoid for GA Gradient
        return 1.0 / (1.0 + np.exp(-self.sharpness * (field - self.threshold)))
        
    def apply_hard(self, field):
        # Binary Step for Final Output
        return (field > self.threshold).astype(float)

# --- Simulation Classes ---

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

# --- GA Classes ---

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

class IntegratedCompilerGA:
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
        
        # Physics Engine
        self.viscosity = ViscousField(target_field.width, target_field.height, viscosity=1.0)
        self.matter = ThresholdMatter(threshold=0.5, sharpness=10.0)
        
        self.best_genome = None
        self.best_fitness = -1.0
        self.best_error = float('inf')
        
    def evaluate(self, genome):
        # 1. Forward Cymatics (Soft Light)
        sim = CymaticSimulation(self.target_field.width, self.target_field.height, genome.emitters)
        soft_field = sim.calculate_density_field()
        
        # 2. Material Physics (Hard Matter)
        smoothed_field = self.viscosity.apply(soft_field)
        hard_field = self.matter.apply_sigmoid(smoothed_field) # Use sigmoid for gradient
        
        # 3. Error Calculation
        error = self.target_field.calculate_error(hard_field)
        fitness = 1.0 / (1.0 + error)
        return fitness, error

    def evolve(self, generations=100):
        for gen in range(generations):
            # Adaptive Mutation
            progress = gen / generations
            current_mutation_rate = self.mutation_rate * (1.0 - 0.5 * progress)
            current_sigma = 0.1 * (1.0 - 0.8 * progress)
            
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
    print("CYCLE 327: INTEGRATED MATTER COMPILER")
    print("=====================================")
    
    width, height = 128, 128
    
    # 1. Define Target (Square Donut)
    target = TargetField(width, height)
    target.field[:, :] = 0.0
    
    # Outer Square (32 to 96)
    target.field[32:96, 32:96] = 1.0
    # Inner Hole (48 to 80)
    target.field[48:80, 48:80] = 0.0
    
    print("Target: Square Donut (Hollow Square)")
    # target.display(scale=1)
    
    # 2. Initialize Solver
    print("\nInitializing Integrated GA (Pop=100, Emitters=16, Gen=200)...")
    solver = IntegratedCompilerGA(target, population_size=100, num_emitters=16, mutation_rate=0.2)
    
    # 3. Evolve
    print("\n--- Evolution Start ---")
    result = solver.evolve(generations=200)
    print("--- Evolution Complete ---")
    
    # 4. Results
    print(f"\nBest Error: {result['error']:.6f}")
    
    # 5. Visualize Result
    best_emitters = [Emitter(**p) for p in result['genome']]
    
    # Reconstruct Pipeline
    sim = CymaticSimulation(width, height, best_emitters)
    soft_field = sim.calculate_density_field()
    
    viscosity = ViscousField(width, height, viscosity=1.0)
    smoothed_field = viscosity.apply(soft_field)
    
    matter = ThresholdMatter(threshold=0.5)
    hard_field = matter.apply_hard(smoothed_field) # Final output is hard
    
    # Display
    print("\n--- Generated Pattern (Center Slice) ---")
    row = 64
    print("Target: ", "".join(["#" if x > 0.5 else "." for x in target.field[row, 32:96:2]]))
    print("Soft:   ", "".join(["#" if x > 0.5 else "." for x in soft_field[row, 32:96:2]]))
    print("Hard:   ", "".join(["#" if x > 0.5 else "." for x in hard_field[row, 32:96:2]]))
    
    # 6. Save
    results_data = {
        "cycle": 327,
        "target": "Square Donut",
        "best_error": result['error'],
        "emitters": result['genome']
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c327_integrated_compiler.json", "w") as f:
        json.dump(results_data, f, indent=2)
        
    if result['error'] < 0.05:
        print("\n>> SUCCESS: Integrated Compiler achieved Digital Matter fidelity.")
    else:
        print("\n>> RESULT: Improvement, but complexity limits remain.")

if __name__ == "__main__":
    main()
