"""
HELIOS Type 3 OS - Command Line Interface
The bridge between the User and the Machine.
"""
import sys
import cmd
from code.helios.operator import UniversalOperator

class HeliosShell(cmd.Cmd):
    intro = 'Welcome to HELIOS. The Type 3 Operating System.\nType help or ? to list commands.\n'
    prompt = '(helios) '
    
    def __init__(self):
        super().__init__()
        print("Initializing Universal Operator...")
        self.op = UniversalOperator(resolution_mm=4.0) # Low res for interactive speed
        print("Operator Online. Hardware Ready.")
        
    def do_create(self, arg):
        'Create an object: create <shape> <x> <y> <z>'
        try:
            args = arg.split()
            if len(args) != 4:
                print("Usage: create <shape> <x> <y> <z>")
                return
                
            shape = args[0]
            x, y, z = float(args[1]), float(args[2]), float(args[3])
            
            print(f"Compiling {shape} at ({x}, {y}, {z})...")
            obj_id = self.op.create_object(shape, (x, y, z))
            stability = self.op.get_stability(obj_id)
            
            print(f"Object ID {obj_id} Created.")
            print(f"Stability Index: {stability:.4f}")
            if stability < 0.1:
                print(">> Status: STABLE")
            else:
                print(">> Status: UNSTABLE (Optimization needed)")
                
        except Exception as e:
            print(f"Error: {e}")
            
    def do_status(self, arg):
        'Check system status'
        print(f"Active Objects: {len(self.op.active_objects)}")
        for oid, data in self.op.active_objects.items():
            print(f"ID {oid}: {data['type']} at {data['location']}")
            
    def do_exit(self, arg):
        'Exit the shell'
        print("Shutting down HELIOS.")
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Non-interactive test mode
        shell = HeliosShell()
        shell.onecmd("create cube 50 50 50")
        shell.onecmd("status")
    else:
        HeliosShell().cmdloop()