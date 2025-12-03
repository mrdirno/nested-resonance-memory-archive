import json
import os

class HeliosShelf:
    def __init__(self, library_path="fabrication/library/HELIOS_LIBRARY_V2.json"):
        self.library_path = library_path
        self.data = self._load_library()
        
    def _load_library(self):
        if not os.path.exists(self.library_path):
            raise FileNotFoundError(f"Library not found at {self.library_path}")
        with open(self.library_path, 'r') as f:
            return json.load(f)
            
    def list_series(self):
        """Returns a list of available series."""
        return list(self.data.get("series", {}).keys())
        
    def list_designs(self, series_name=None):
        """Returns a list of designs, optionally filtered by series."""
        designs = []
        if series_name:
            series_data = self.data.get("series", {}).get(series_name, {})
            for d_key, d_val in series_data.items():
                designs.append(d_val)
        else:
            for s_key, s_val in self.data.get("series", {}).items():
                for d_key, d_val in s_val.items():
                    designs.append(d_val)
        return designs
        
    def get_design(self, design_id_or_name):
        """Retrieves a specific design by ID (e.g. '01') or Name (e.g. 'redshift')."""
        for s_key, s_val in self.data.get("series", {}).items():
            for d_key, d_val in s_val.items():
                if d_val["id"] == design_id_or_name or d_val["name"] == design_id_or_name:
                    return d_val
        return None
        
    def search(self, query):
        """Search designs by name or logic keyword."""
        results = []
        query = query.lower()
        for s_key, s_val in self.data.get("series", {}).items():
            for d_key, d_val in s_val.items():
                # Check name
                if query in d_val["name"].lower():
                    results.append(d_val)
                    continue
                
                # Check component metadata logic
                for comp_key, comp_val in d_val.get("components", {}).items():
                    logic = comp_val.get("metadata", {}).get("logic", "").lower()
                    if query in logic:
                        results.append(d_val)
                        break
        return results

    def read_source(self, design_id_or_name, component_type):
        """
        Reads the source code for a specific component of a design.
        
        Args:
            design_id_or_name (str): The ID (e.g. "01") or name (e.g. "redshift") of the design.
            component_type (str): The component type ("shade", "base", "shaft").
            
        Returns:
            str: The source code content of the generator file.
            None: If design or component is not found.
        """
        design = self.get_design(design_id_or_name)
        if not design:
            print(f"Design '{design_id_or_name}' not found.")
            return None
            
        comp_data = design.get("components", {}).get(component_type)
        if not comp_data:
            print(f"Component '{component_type}' not found in design '{design['name']}'.")
            return None
            
        filename = comp_data["file"]
        # Design path is relative to repo root in JSON, need to ensure we can access it
        # The JSON path is relative to where librarian ran? 
        # "path": "fabrication/furniture/lamp_series_01/01_redshift"
        
        full_path = os.path.join(design["path"], filename)
        
        if not os.path.exists(full_path):
            print(f"Source file not found at {full_path}")
            return None
            
        with open(full_path, 'r') as f:
            return f.read()

# Example Usage
if __name__ == "__main__":
    shelf = HeliosShelf()
    print(f"Loaded Shelf. Series: {shelf.list_series()}")
    
    design = shelf.get_design("01")
    if design:
        print(f"Found Design 01: {design['name']}")
        
    results = shelf.search("voronoi")
    print(f"Search 'voronoi' found {len(results)} designs: {[d['name'] for d in results]}")
    
    # Test Reader
    source = shelf.read_source("01", "shade")
    if source:
        print("\n--- Source Code Preview (01 Shade) ---")
        print(source[:200] + "...")
