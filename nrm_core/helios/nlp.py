"""
HELIOS Natural Language Interface
"The Replicator" - Text-to-Matter Translation Layer.
"""
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NaturalLanguageInterface:
    """
    Parses natural language text into structured operational intents
    for the Universal Operator.
    """
    def __init__(self):
        self.intents = [
            (r'(?i)create\s+(?:a\s+)?(\w+)\s+(?:at\s+)?(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)', self._parse_create),
            (r'(?i)make\s+(?:a\s+)?(\w+)\s+(?:at\s+)?(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)', self._parse_create),
            (r'(?i)move\s+(?:object\s+)?(\d+)\s+(?:to\s+)?(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)', self._parse_move),
            (r'(?i)load\s+(?:model\s+)?([\w\./\\-]+)', self._parse_load),
            (r'(?i)import\s+(?:model\s+)?([\w\./\\-]+)', self._parse_load),
            (r'(?i)delete\s+(?:object\s+)?(\d+)', self._parse_delete),
            (r'(?i)remove\s+(?:object\s+)?(\d+)', self._parse_delete),
            (r'(?i)status|report|list', self._parse_status),
            (r'(?i)help', self._parse_help)
        ]

    def parse(self, text: str):
        """
        Main entry point. Returns a dictionary with 'action' and parameters,
        or None if no match found.
        """
        text = text.strip()
        for pattern, handler in self.intents:
            match = re.search(pattern, text)
            if match:
                return handler(match)
        
        return {"action": "unknown", "original_text": text}

    def _parse_create(self, match):
        shape = match.group(1).lower()
        x = float(match.group(2))
        y = float(match.group(3))
        z = float(match.group(4))
        return {
            "action": "create",
            "shape": shape,
            "location": (x, y, z)
        }

    def _parse_load(self, match):
        filename = match.group(1)
        return {
            "action": "load",
            "filename": filename
        }

    def _parse_move(self, match):
        obj_id = int(match.group(1))
        x = float(match.group(2))
        y = float(match.group(3))
        z = float(match.group(4))
        return {
            "action": "move",
            "id": obj_id,
            "target": (x, y, z)
        }

    def _parse_delete(self, match):
        obj_id = int(match.group(1))
        return {
            "action": "delete",
            "id": obj_id
        }

    def _parse_status(self, match):
        return {
            "action": "status"
        }
        
    def _parse_help(self, match):
        return {
            "action": "help"
        }

if __name__ == "__main__":
    # Quick Test
    nlp = NaturalLanguageInterface()
    print(nlp.parse("Create a cube at 50, 50, 50"))
    print(nlp.parse("Move object 1 to 20 20 20"))
    print(nlp.parse("Status report"))
    print(nlp.parse("Make me a sandwich"))
