import os
import sys
import json

def verify_catalog():
    base_path = "fabrication/furniture"
    
    # Canon list based on recent refinement cycles
    canon_designs = {
        "lamp_series_01": [
            "01_redshift", "02_event_horizon", "03_singularity", "04_supernova", "05_quantum_foam",
            "06_dark_matter", "07_multiverse", "08_time_crystal", "09_neutron_star", "10_final_theory"
        ],
        "lamp_series_02": [
            "11_turing", "12_growth", "13_colony", "14_swarm", "15_breath"
        ],
        "lamp_series_03": [
            "16_tesseract", "17_klein", "18_mobius", "19_voronoi", "20_fractal"
        ],
        "lamp_series_04": [
            "21_grid", "22_lattice", "23_glitch", "24_wire", "25_futurist"
        ],
        "lamp_series_05": [
            "26_impossible", "27_recursive", "28_chaos", "29_void", "30_unseen"
        ],
        "lamp_series_06": [
            "31_the_end", "32_the_beginning", "33_the_prophecy", "34_the_architect", "35_the_machine"
        ]
    }
    
    report = {
        "total_designs": 35,
        "verified": 0,
        "missing": [],
        "invalid": [],
        "details": {}
    }
    
    for series, designs in canon_designs.items():
        for design in designs:
            design_path = os.path.join(base_path, series, design)
            
            # Check directory
            if not os.path.isdir(design_path):
                report["missing"].append(f"{design} (Directory)")
                continue
                
            # Check components
            # Naming convention might vary slightly (e.g. redshift_shade.stl vs shade.stl)
            # Based on generation scripts, it's usually [design_name]_shade.stl
            
            # Extract simple name from folder name (e.g. 01_redshift -> redshift)
            # But wait, folder is 01_redshift, file is redshift_shade.stl
            # Design 31_the_end -> the_end_shade.stl?
            
            # Let's try to deduce the prefix.
            # Usually everything after the number.
            parts = design.split('_')
            if parts[0].isdigit():
                name_parts = parts[1:]
            else:
                name_parts = parts
                
            design_name = "_".join(name_parts)
            
            # Handle specific cases if naming is inconsistent
            # e.g. 06_dark_matter -> dark_shade.stl ? Or dark_matter_shade.stl?
            # I should check what files exist.
            
            files = os.listdir(design_path)
            stl_files = [f for f in files if f.endswith(".stl")]
            
            has_shade = False
            has_base = False
            has_shaft = False
            
            for f in stl_files:
                if "shade" in f: has_shade = True
                if "base" in f: has_base = True
                if "shaft" in f: has_shaft = True
                
                # Check size
                size = os.path.getsize(os.path.join(design_path, f))
                if size < 1024: # Less than 1KB is suspicious for a mesh
                    report["invalid"].append(f"{design}/{f} (Size: {size} bytes)")
            
            status = "OK"
            if not (has_shade and has_base and has_shaft):
                status = "INCOMPLETE"
                report["missing"].append(f"{design} (Components: Shade={has_shade}, Base={has_base}, Shaft={has_shaft})")
            else:
                report["verified"] += 1
                
            report["details"][design] = {
                "path": design_path,
                "components": stl_files,
                "status": status
            }

    print(json.dumps(report, indent=2))
    
    if report["verified"] == report["total_designs"]:
        print("\nSUCCESS: All 35 Designs Verified.")
        sys.exit(0)
    else:
        print(f"\nFAILURE: Only {report['verified']}/35 Designs Verified.")
        sys.exit(1)

if __name__ == "__main__":
    verify_catalog()
