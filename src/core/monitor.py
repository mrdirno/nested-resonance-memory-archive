import math
import statistics

class BCPMonitor:
    def __init__(self):
        self.fitness_history = []
        self.generation_data = []

    def record_generation(self, gen_data):
        self.fitness_history.append(gen_data["value"])
        self.generation_data.append(gen_data)

    def get_stats(self, num_generations=5):
        if not self.fitness_history:
            return {
                "avg_fitness": 0.0,
                "max_fitness": 0.0,
                "min_fitness": 0.0,
                "stagnation_variance": 0.0,
                "total_generations": 0,
                "active_params": None
            }
        
        recent_fitness = self.fitness_history[-num_generations:]
        
        stats = {
            "avg_fitness": statistics.mean(recent_fitness) if recent_fitness else 0.0,
            "max_fitness": max(recent_fitness) if recent_fitness else 0.0,
            "min_fitness": min(recent_fitness) if recent_fitness else 0.0,
            "stagnation_variance": (max(recent_fitness) - min(recent_fitness)) if len(recent_fitness) > 1 else 0.0,
            "total_generations": len(self.fitness_history),
            "active_params": self.generation_data[-1]["params_used"] if self.generation_data else None
        }
        return stats

    def report_status(self, num_generations=5):
        stats = self.get_stats(num_generations)
        
        report = f"""
--- GARDEN STATUS REPORT (Last {num_generations} Generations) ---
Total Generations: {stats["total_generations"]}
Average Fitness: {stats["avg_fitness"]:.2f}
Max Fitness: {stats["max_fitness"]:.2f}
Min Fitness: {stats["min_fitness"]:.2f}
Stagnation Variance: {stats["stagnation_variance"]:.2f}
Active Parameter Ranges:
  Budget: {stats["active_params"]["budget_range"][0]:.1f} - {stats["active_params"]["budget_range"][1]:.1f}
  Gain:   {stats["active_params"]["gain_range"][0]:.1f} - {stats["active_params"]["gain_range"][1]:.1f}
  Cost:   {stats["active_params"]["cost_range"][0]:.1f} - {stats["active_params"]["cost_range"][1]:.1f}
--------------------------------------------------
"""
        return report
