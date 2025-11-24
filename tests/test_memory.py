import pytest
import shutil
from pathlib import Path
from nrm_core.memory import PatternMemory, Pattern, PatternType

@pytest.fixture
def memory_system():
    db_dir = Path("tests/temp_db")
    if db_dir.exists():
        shutil.rmtree(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    
    memory = PatternMemory(workspace_path=db_dir)
    yield memory
    
    # Cleanup
    shutil.rmtree(db_dir)

def test_store_and_retrieve_pattern(memory_system):
    pattern = Pattern(
        pattern_id="p1",
        pattern_type=PatternType.SYSTEM_BEHAVIOR,
        name="Test Pattern",
        description="A test description",
        data={"foo": "bar"},
        confidence=0.9,
        occurrences=1,
        first_seen=0.0,
        last_seen=0.0
    )
    
    memory_system.store_pattern(pattern)
    
    retrieved = memory_system.get_pattern("p1")
    assert retrieved is not None
    assert retrieved.name == "Test Pattern"
    assert retrieved.description == "A test description"
    assert retrieved.data["foo"] == "bar"

def test_pattern_not_found(memory_system):
    retrieved = memory_system.get_pattern("non_existent")
    assert retrieved is None

def test_search_patterns(memory_system):
    p1 = Pattern(pattern_id="p1", pattern_type=PatternType.SYSTEM_BEHAVIOR, name="Alpha", description="Desc 1", data={}, confidence=0.5, occurrences=1, first_seen=0, last_seen=0)
    p2 = Pattern(pattern_id="p2", pattern_type=PatternType.TASK_EXECUTION, name="Beta", description="Desc 2", data={}, confidence=0.5, occurrences=1, first_seen=0, last_seen=0)
    
    memory_system.store_pattern(p1)
    memory_system.store_pattern(p2)
    
    results = memory_system.search_patterns(pattern_type=PatternType.SYSTEM_BEHAVIOR)
    assert len(results) == 1
    assert results[0].pattern_id == "p1"
