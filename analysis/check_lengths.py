import re

with open('/Volumes/dual/DUALITY-ZERO-V2/bridge-ui/constants.ts', 'r') as f:
    content = f.read()

matches = re.findall(r"\[TranscendentalNumber\.(\w+)\]:\s*'(\d+)'", content)

print("Lengths:")
for name, digits in matches:
    print(f"{name}: {len(digits)}")
