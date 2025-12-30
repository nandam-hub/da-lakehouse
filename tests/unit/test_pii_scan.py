import pytest
import re
from pathlib import Path

class TestPIIScan:
    def test_no_ssn_patterns(self):
        """Test no SSN patterns in code"""
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        self._scan_files_for_pattern(ssn_pattern, "SSN")

    def test_no_credit_card_patterns(self):
        """Test no credit card patterns in code"""
        cc_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        self._scan_files_for_pattern(cc_pattern, "Credit Card")

    def test_no_phone_patterns(self):
        """Test no phone number patterns in code"""
        phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b'
        self._scan_files_for_pattern(phone_pattern, "Phone Number")

    def _scan_files_for_pattern(self, pattern, pattern_name):
        """Scan files for PII patterns"""
        exclude_dirs = {'.git', 'node_modules', 'tests', 'fixtures', '__pycache__', '.databricks'}
        exclude_files = {'*.lock', '*.lock.hcl', 'uv.lock', '*.ipynb', '*.parquet', '*.exe', '*.dll', '*.bin'}
        
        violations = []
        
        for file_path in Path('.').rglob('*'):
            if file_path.is_file() and not any(exc in str(file_path) for exc in exclude_dirs):
                if not any(file_path.match(pattern) for pattern in exclude_files):
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Filter out test data and hashes
                            real_matches = [m for m in matches if not any(x in str(m).lower() for x in ['test', 'example', 'hash', 'sha256'])]
                            if real_matches:
                                violations.append(f"{file_path}: {real_matches}")
                    except Exception:
                        continue
        
        assert len(violations) == 0, f"{pattern_name} patterns found: {violations}"