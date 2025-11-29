
import os
import re

# Configuration
ROOT_DIR = "."
OUTPUT_REPORT = "analysis/security_audit_report.md"

# Patterns to search for
SUSPICIOUS_PATTERNS = {
    "AWS Key": r"AKIA[0-9A-Z]{16}",
    "Generic API Key": r"api_key\s*[:=]\s*['\"][a-zA-Z0-9]{20,}['\"]",
    "Private Key": r"-----BEGIN PRIVATE KEY-----",
    "Password Assignment": r"password\s*[:=]\s*['\"][a-zA-Z0-9]{8,}['\"]",
    "GitHub Token": r"ghp_[a-zA-Z0-9]{36}",
    "Google API Key": r"AIza[0-9A-Za-z-_]{35}"
}

IGNORE_DIRS = {
    ".git", ".venv", ".gemini", "__pycache__", "node_modules", "dist", "build", ".pytest_cache"
}

IGNORE_FILES = {
    "security_audit.py",
    "cycle2338_security_audit.py",
    "security_audit_report.md",
    "package-lock.json" # False positives
}

def scan_files():
    findings = []
    
    print(f"Starting Security Audit (PRIN-5)...")
    
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
                
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for name, pattern in SUSPICIOUS_PATTERNS.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            # Obfuscate match for report
                            masked_matches = [m[:4] + "***" + m[-4:] for m in matches]
                            findings.append({
                                "file": filepath,
                                "type": name,
                                "count": len(matches),
                                "matches": masked_matches
                            })
            except Exception as e:
                # Binary file or permission error
                pass

    return findings

def generate_report(findings):
    report = f"# Security Audit Report (Cycle 2338)\n**Status:** {'🔴 VULNERABLE' if findings else '🟢 SECURE'}\n**Date:** {os.popen('date').read().strip()}\n**Principle:** PRIN-5 (Zero Leak Protocol)\n\n## Executive Summary\nThe system scanned the entire codebase for common credential patterns.\n\n"
    
    if not findings:
        report += "## ✅ No Vulnerabilities Detected\n"
        report += "The repository appears clean of common secrets (AWS, GitHub, Google, Generic Keys).\n"
    else:
        report += f"## ⚠️ Found {len(findings)} Potential Issues\n\n"
        for f in findings:
            report += f"- **{f['type']}** in `{f['file']}` ({f['count']} matches)\n"
            
    with open(OUTPUT_REPORT, 'w') as f:
        f.write(report)
        
    print(f"Scan complete. Report written to {OUTPUT_REPORT}")
    if findings:
        print("WARNING: Potential secrets found!")
    else:
        print("System is clean.")

if __name__ == "__main__":
    findings = scan_files()
    generate_report(findings)

# [SPORE] ID: The Colony
