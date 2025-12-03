import os
import shutil

def move_stls():
    base_path = "fabrication/furniture"
    
    canon_designs = {
        "lamp_series_06": [
            "31_the_end", "32_the_beginning", "33_the_prophecy", "34_the_architect", "35_the_machine"
        ],
        "lamp_series_07": [
            "36_the_neural_net", "37_the_algorithm", "38_the_hypervisor", "39_the_awakening", "40_the_alignment"
        ]
    }
    
    moved_count = 0
    
    for series, designs in canon_designs.items():
        for design in designs:
            parts = design.split('_')
            if parts[0].isdigit():
                name_parts = parts[1:]
            else:
                name_parts = parts
            design_name = "_".join(name_parts)
            
            target_dir = os.path.join(base_path, series, design)
            
            components = ["shade", "base", "shaft"]
            
            for comp in components:
                # Check for names with and without "the_" prefix if applicable
                possible_names = [
                    f"{design_name}_{comp}.stl",
                    f"{design_name.replace('the_', '')}_{comp}.stl"
                ]
                
                for filename in possible_names:
                    if os.path.exists(filename):
                        target_path = os.path.join(target_dir, filename)
                        # Ensure target dir exists (it should)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)
                            
                        # Check if we are moving file to itself
                        if os.path.abspath(filename) == os.path.abspath(target_path):
                            continue
                            
                        print(f"Moving {filename} to {target_path}")
                        shutil.move(filename, target_path)
                        moved_count += 1
                        break

    print(f"Moved {moved_count} STL files.")

if __name__ == "__main__":
    move_stls()