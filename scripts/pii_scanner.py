#!/usr/bin/env python3
"""PII Scanner for Databricks Asset Bundles"""

import re
import sys
import yaml
from pathlib import Path

PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'phone': r'\b\d{3}-\d{3}-\d{4}\b',
    'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    'aws_key': r'AKIA[0-9A-Z]{16}',
    'private_key': r'-----BEGIN (RSA )?PRIVATE KEY-----'
}

def scan_file(file_path):
    """Scan file for PII patterns"""
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"{file_path}:{line_num} - {pii_type}: {match.group()}")

    except Exception as e:
        print(f"Error scanning {file_path}: {e}")

    return violations

def main():
    violations = []

    for file_path in sys.argv[1:]:
        violations.extend(scan_file(file_path))

    if violations:
        print("PII VIOLATIONS FOUND:")
        for violation in violations:
            print(f"  {violation}")
        sys.exit(1)

    print("No PII violations found")

if __name__ == "__main__":
    main()
