import os
import re

TERMS = {
    "distributed": "distributed",
    "Distributed": "Distributed",
    "worker": "worker",
    "Worker": "Worker",
    "WORKER": "WORKER",
    "dispatcher": "dispatcher",
    "Dispatcher": "Dispatcher",
    "aggregator": "aggregator",
    "Aggregator": "Aggregator",
    "EvolutionMonitor": "EvolutionMonitor",
    "HyperMutationEvent": "HyperMutationEvent",
    "KnowledgeBase": "KnowledgeBase",
    "KNOWLEDGE_BASE": "KNOWLEDGE_BASE"
}

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            content = f.read()
        except UnicodeDecodeError:
            return False # skip binaries
            
    original = content
    for old, new in TERMS.items():
        # Using word boundaries for some? No, let's just do direct replace
        # But be careful with partial matches. e.g. "fruitful" -> "aggregatorful".
        # Let's use regex with word boundaries for lower/upper case single words.
        if old in ["distributed", "Distributed", "worker", "Worker", "WORKER", "dispatcher", "Dispatcher", "aggregator", "Aggregator"]:
            content = re.sub(r'\b' + re.escape(old) + r'\b', new, content)
        else:
            content = content.replace(old, new)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified_files = 0
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py') or file.endswith('.md') or file.endswith('.json'):
                filepath = os.path.join(root, file)
                if refactor_file(filepath):
                    print(f"Refactored: {filepath}")
                    modified_files += 1
                    
    # Also refactor root markdown/python files
    for file in os.listdir('.'):
        if os.path.isfile(file) and (file.endswith('.py') or file.endswith('.md')):
            if refactor_file(file):
                print(f"Refactored root file: {file}")
                modified_files += 1
                
    print(f"Total files modified: {modified_files}")

if __name__ == "__main__":
    main()
