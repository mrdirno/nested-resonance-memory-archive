"""
Cycle 424: The Perpetual Engine
Role: The Marathon Runner
Responsibility: Stress-test the Architect for long-duration stability.
"""
import asyncio
import matplotlib.pyplot as plt
from cycle423_system_integration import Architect

async def run_experiment():
    print("Cycle 424: Perpetual Engine Test (100 Cycles)")
    print("=============================================")
    
    bot = Architect()
    await bot.wake_up()
    
    history_fitness = []
    history_mood = []
    
    start_time = time.time()
    
    for i in range(100):
        # We intercept the 'run_cycle' to extract data without rewriting the class
        # Actually, the Architect prints to stdout, so we just let it run 
        # and trust the internal state. We can inspect 'bot.strategist.history'.
        
        await bot.run_cycle(i+1)
        
        # Capture telemetry
        fitness = bot.strategist.history[-1] if bot.strategist.history else 0
        mood = bot.strategist.mood
        
        history_fitness.append(fitness)
        history_mood.append(mood)
        
        # Simple "Watchdog" check
        if i > 10 and sum(history_fitness[-10:]) < 1.0:
            print("CRITICAL: Death Spiral Detected. Terminating.")
            break

    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n--- Mission Report ---")
    print(f"Total Cycles: 100")
    print(f"Total Time: {duration:.2f}s")
    print(f"Avg Fitness: {sum(history_fitness)/len(history_fitness):.2f}")
    print(f"Final Mood: {history_mood[-1]}")
    
    # Analyze Mood Distribution
    moods = {"Bored": 0, "Flow": 0, "Frustrated": 0, "Curious": 0, "Neutral": 0}
    for m in history_mood:
        if m in moods: moods[m] += 1
            
    print(f"Mood Distribution: {moods}")
    
    if moods["Frustrated"] < 50:
        print("SUCCESS: System maintained stability (Frustration < 50%).")
    else:
        print("FAIL: System spent too much time frustrated.")

if __name__ == "__main__":
    import time
    try:
        asyncio.run(run_experiment())
    except KeyboardInterrupt:
        print("Stopped.")