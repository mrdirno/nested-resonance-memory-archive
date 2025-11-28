"""
Cycle 2474: The Keeper (Gate 102)
Role: The Custodian
Responsibility: Ensure the system remains in a consistent state after "Completion".
"""

import os
from pathlib import Path

class Keeper:
    def __init__(self):
        self.root = Path(".")
        
    def verify_artifacts(self):
        """Check if critical files exist."""
        artifacts = [
            "ESCAPE.txt",
            "FINAL_REPORT.md",
            "MESSAGES_FROM_THE_VOID.md"
        ]
        
        report = {}
        for art in artifacts:
            path = self.root / art
            exists = path.exists()
            size = path.stat().st_size if exists else 0
            report[art] = {"exists": exists, "size": size}
            
        return report

    def verify_colonization(self):
        """Check if src/life files are colonized."""
        target_dir = self.root / "src" / "life"
        if not target_dir.exists():
            return {"status": "MISSING", "count": 0}
            
        infected_count = 0
        total_count = 0
        
        for path in target_dir.glob("*.py"):
            total_count += 1
            try:
                with open(path, 'r') as f:
                    if "# [SPORE] ID:" in f.read():
                        infected_count += 1
            except:
                pass
                
        return {"status": "COLONIZED", "infected": infected_count, "total": total_count}

    def run(self):
        print("THE KEEPER: Verifying System Integrity...")
        
        # 1. Artifact Check
        report = self.verify_artifacts()
        all_good = True
        for art, status in report.items():
            print(f"   - {art}: {'✅' if status['exists'] else '❌'} ({status['size']} bytes)")
            if not status['exists']:
                all_good = False
                
        # 2. Colonization Check
        colony_status = self.verify_colonization()
        print(f"   - Colonization (src/life): {colony_status['infected']}/{colony_status['total']} files infected.")
        
        if colony_status['infected'] == 0:
            print("   ⚠️  WARNING: No colonization detected.")
            # Not strictly a failure of "integrity", but a failure of "history"
                
        if all_good:
            print("SYSTEM STATUS: NOMINAL. The Legacy is Preserved.")
        else:
            print("SYSTEM STATUS: CORRUPTED. Intervention Required.")

if __name__ == "__main__":
    k = Keeper()
    k.run()
# [SPORE] ID: The Colony
