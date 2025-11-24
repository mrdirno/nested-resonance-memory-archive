"""
Hello Memory: Testing the NRM Memory System
"""
import time
import shutil
from pathlib import Path
from nrm_core.memory import PatternMemory, Pattern, PatternType

def main():
    print("Initializing Memory System...")
    # Use a temp directory for the DB to avoid polluting the repo with test DBs
    db_dir = Path("examples/temp_db")
    if db_dir.exists():
        shutil.rmtree(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    
    memory = PatternMemory(workspace_path=db_dir)
    
    print("Creating Pattern...")
    pattern = Pattern(
        pattern_id="test_pattern_001",
        pattern_type=PatternType.SYSTEM_BEHAVIOR,
        name="Hello World Pattern",
        description="A test pattern.",
        data={"value": 42, "message": "Hello NRM"},
        confidence=0.9,
        occurrences=1,
        first_seen=time.time(),
        last_seen=time.time(),
        metadata={"author": "Gemini"}
    )
    
    print(f"Storing Pattern: {pattern.name}")
    memory.store_pattern(pattern)
    
    print("Retrieving Pattern...")
    retrieved = memory.get_pattern("test_pattern_001")
    
    if retrieved:
        print(f"Success! Retrieved: {retrieved.name}")
        print(f"Data: {retrieved.data}")
    else:
        print("Failure: Pattern not found.")
        
    # Clean up
    shutil.rmtree(db_dir)

if __name__ == "__main__":
    main()
