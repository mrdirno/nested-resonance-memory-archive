"""
NRM Core: Interface Facade
"""
from .resonance import ResonantField
import json

class NRMInterface:
    def __init__(self):
        self.field = ResonantField()
        
    def handle_request(self, method, payload):
        if method == "ADD_NODE":
            node_id = payload.get("id")
            vector = payload.get("vector")
            self.field.add_node(node_id, vector)
            return {"status": "ok", "msg": f"Node {node_id} added"}
            
        elif method == "QUERY":
            vector = payload.get("vector")
            self.field.stimulate(vector)
            active = self.field.get_active_nodes()
            # Return top 3
            sorted_nodes = sorted(active.items(), key=lambda x: x[1], reverse=True)[:3]
            return {"status": "ok", "results": sorted_nodes}
            
        return {"status": "error", "msg": "Unknown method"}
