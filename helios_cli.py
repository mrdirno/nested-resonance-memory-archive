"""
HELIOS Type 3 OS - Command Line Interface
The bridge between the User and the Machine.
"""
import sys
import cmd
from code.helios.operator import UniversalOperator
from code.helios.nlp import NaturalLanguageInterface

class HeliosShell(cmd.Cmd):
    intro = 'Welcome to HELIOS. The Type 3 Operating System.\nType help or ? to list commands.\nOr just speak naturally (e.g., "Create a cube at 50 50 50").\n'
    prompt = '(helios) '
    
    def __init__(self):
        super().__init__()
        print("Initializing Universal Operator...")
        self.op = UniversalOperator(resolution_mm=4.0) # Low res for interactive speed
        self.nlp = NaturalLanguageInterface()
        print("Operator Online. Hardware Ready.")
        print("Natural Language Processor Online.")
        
    def default(self, line):
        """
        Handle natural language commands.
        """
        intent = self.nlp.parse(line)
        action = intent.get('action')
        
        if action == 'create':
            self.do_create(f"{intent['shape']} {intent['location'][0]} {intent['location'][1]} {intent['location'][2]}")
        elif action == 'move':
            self.do_move(f"{intent['id']} {intent['target'][0]} {intent['target'][1]} {intent['target'][2]}")
        elif action == 'delete':
            self.do_delete(f"{intent['id']}")
        elif action == 'status':
            self.do_status("")
        elif action == 'help':
            self.do_help("")
        elif action == 'unknown':
            print(f"I didn't understand: '{intent.get('original_text')}'")
            print("Try: 'Create a cube at 50 50 50' or 'Move object 1 to 20 20 20'")
        else:
            print(f"Error: Action '{action}' not implemented.")

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

    def do_move(self, arg):
        'Move an object: move <id> <x> <y> <z>'
        try:
            args = arg.split()
            if len(args) != 4:
                print("Usage: move <id> <x> <y> <z>")
                return
            
            obj_id = int(args[0])
            x, y, z = float(args[1]), float(args[2]), float(args[3])
            
            print(f"Relocating Object {obj_id} to ({x}, {y}, {z})...")
            self.op.move_object(obj_id, (x, y, z))
            stability = self.op.get_stability(obj_id)
            
            print(f"Object {obj_id} Moved.")
            print(f"Stability Index: {stability:.4f}")
             
        except Exception as e:
            print(f"Error: {e}")

    def do_delete(self, arg):
        'Delete an object: delete <id>'
        try:
            obj_id = int(arg.strip())
            if self.op.delete_object(obj_id):
                print(f"Object {obj_id} deleted.")
            else:
                print(f"Object {obj_id} not found.")
        except ValueError:
             print("Usage: delete <id>")
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
        print("\n--- Testing Standard Commands ---")
        shell.onecmd("create cube 50 50 50")
        shell.onecmd("status")
        
        print("\n--- Testing NLP Commands ---")
        shell.default("Make a cube at 30 30 30")
        shell.default("Move object 2 to 40 40 40")
        shell.default("Status report")
        shell.default("Delete object 1")
        shell.default("Status")
    else:
        HeliosShell().cmdloop()