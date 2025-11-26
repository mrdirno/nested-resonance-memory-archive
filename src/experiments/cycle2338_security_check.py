
"""
Cycle 2338: Security Integrity Check (PRIN-5 Verification)
Goal: Ensure 'Zero Leak' compliance by scanning for sensitive patterns.
Method:
1. Define regex patterns for common secrets (API keys, private keys, passwords).
2. Scan all files in the repository (excluding .git and .venv).
3. Report any matches.
"""

import os
import sys
import re
import json

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def run_security_scan(root_dir):
    print(f"Cycle 2338: Initiating Security Scan on {root_dir}...")
    
    # 1. Define Threat Patterns (PRIN-5)
    patterns = {
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Private Key": r"-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
        "Generic Secret": r"(?i)(password|secret|token|api_key)['\"]?\s*[:=]\s*['\"][^'\"]+['\"]",
        "Gemini API Key": r"AIza[0-9A-Za-z-_]{35}"
    }
    
    compiled_patterns = {name: re.compile(regex) for name, regex in patterns.items()}
    
    # 2. Scan Loop
    findings = []
    files_scanned = 0
    
    ignore_dirs = {'.git', '.venv', '__pycache__', 'node_modules', 'dist', 'build', '.pytest_cache', '.gemini'}
    ignore_files = {'cycle2338_security_check.py', '.env.example', 'package-lock.json', 'yarn.lock'}
    
    for root, dirs, files in os.walk(root_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file in ignore_files:
                continue
                
            file_path = os.path.join(root, file)
            files_scanned += 1
            
            try:
                # Skip large files or binary files
                if os.path.getsize(file_path) > 1024 * 1024: # 1MB limit
                    continue
                    
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for name, pattern in compiled_patterns.items():
                        matches = pattern.finditer(content)
                        for match in matches:
                            # Check context to avoid false positives (e.g. "secret" in comments)
                            # For now, just report it
                            findings.append({
                                "file": str(file_path),
                                "type": name,
                                "match_preview": match.group(0)[:20] + "..." # Truncate for safety in report
                            })
                            
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # 3. Report
    print(f"\nScan Complete. {files_scanned} files analyzed.")
    
    if findings:
        print(f"\n[ALERT] {len(findings)} potential security issues found:")
        for f in findings:
            print(f"  - {f['type']} in {f['file']} (Match: {f['match_preview']})")
            
        # Save detailed report (but NOT the full secrets)
        with open("analysis/security_audit_cycle2338.json", "w") as f:
            json.dump(findings, f, indent=2)
    else:
        print("\n[SUCCESS] Zero Leaks detected. PRIN-5 Compliant.")
        
    return len(findings) == 0

if __name__ == "__main__":
    success = run_security_scan(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    if not success:
        sys.exit(1)
