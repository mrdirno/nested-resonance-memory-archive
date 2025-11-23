from typing import Dict, List, Optional
import networkx as nx
from .schemas import LevelSchema, MesoLinker

class NRMMetaController:
    """
    The central engine responsible for managing the hierarchical stack of scales
    and the Meso-Linkers that connect them.
    """
    def __init__(self):
        self.levels: Dict[int, LevelSchema] = {}
        self.linkers: Dict[int, MesoLinker] = {} # Keyed by source_level
        self.graph = nx.DiGraph()

    def register_level(self, schema: LevelSchema):
        """Registers a new scale in the hierarchy."""
        if schema.level_index in self.levels:
            raise ValueError(f"Level {schema.level_index} already registered.")
        
        self.levels[schema.level_index] = schema
        self.graph.add_node(schema.level_index, schema=schema)
        print(f"[NRM] Registered Level {schema.level_index}: {schema.name}")

    def register_linker(self, linker: MesoLinker):
        """Registers a connection between two scales."""
        # Validate existence of levels
        if linker.source_level not in self.levels:
            raise ValueError(f"Source Level {linker.source_level} not registered.")
        if linker.target_level not in self.levels:
            raise ValueError(f"Target Level {linker.target_level} not registered.")
            
        # Validate hierarchy direction (already checked by Pydantic, but double check graph logic)
        if linker.source_level >= linker.target_level:
             raise ValueError("Linker must point upwards in the hierarchy.")

        self.linkers[linker.source_level] = linker
        self.graph.add_edge(linker.source_level, linker.target_level, linker=linker)
        print(f"[NRM] Registered Linker: L{linker.source_level} -> L{linker.target_level}")

    def validate_architecture(self) -> bool:
        """
        Checks if the stack is consistent.
        1. Levels must be contiguous (optional, but good for now).
        2. Graph must be a DAG (Directed Acyclic Graph).
        """
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Hierarchy contains cycles! This violates the stack architecture.")
            
        return True

    def resolve_path(self, start_level: int, end_level: int) -> List[MesoLinker]:
        """
        Finds the sequence of linkers needed to move from start_level to end_level.
        """
        if start_level not in self.levels or end_level not in self.levels:
            raise ValueError("Start or End level not registered.")
            
        try:
            path_indices = nx.shortest_path(self.graph, source=start_level, target=end_level)
        except nx.NetworkXNoPath:
            raise ValueError(f"No path found from Level {start_level} to {end_level}.")
            
        # Convert indices to list of linkers
        path_linkers = []
        for i in range(len(path_indices) - 1):
            source = path_indices[i]
            target = path_indices[i+1]
            # Retrieve linker from graph edge
            linker = self.graph[source][target]['linker']
            path_linkers.append(linker)
            
        return path_linkers

    def get_level(self, index: int) -> LevelSchema:
        return self.levels.get(index)
