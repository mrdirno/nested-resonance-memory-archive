import os
import shutil

def move_stls():
    base_path = "fabrication/furniture"
    
    canon_designs = {
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
    
    moved_count = 0
    
    for series, designs in canon_designs.items():
        for design in designs:
            parts = design.split('_')
            if parts[0].isdigit():
                name_parts = parts[1:]
            else:
                name_parts = parts
            design_name = "_".join(name_parts)
            
            # Special case for 'the_end' -> 'the_end'
            # 'grid' -> 'grid'
            
            target_dir = os.path.join(base_path, series, design)
            
            components = ["shade", "base", "shaft"]
            
            for comp in components:
                possible_names = [
                    f"{design_name}_{comp}.stl",
                    f"{design_name.replace('the_', '')}_{comp}.stl"
                ]
                
                for filename in possible_names:
                    if os.path.exists(filename):
                        target_path = os.path.join(target_dir, filename)
                        print(f"Moving {filename} to {target_path}")
                        shutil.move(filename, target_path)
                        moved_count += 1
                        break

    print(f"Moved {moved_count} STL files.")

if __name__ == "__main__":
    move_stls()
