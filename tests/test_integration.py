import pytest
import subprocess
import os
from pathlib import Path

class TestBundleIntegration:

    @pytest.fixture
    def bundle_path(self):
        return Path("bundles/drs")

    def test_bundle_validate(self, bundle_path):
        """Test databricks bundle validate command"""
        result = subprocess.run(
            ["databricks", "bundle", "validate"],
            cwd=bundle_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Bundle validation failed: {result.stderr}"

    def test_bundle_plan_dry_run(self, bundle_path):
        """Test databricks bundle plan (dry run)"""
        # Skip if no Databricks CLI configured
        if not os.getenv("DATABRICKS_HOST"):
            pytest.skip("Databricks CLI not configured")

        result = subprocess.run(
            ["databricks", "bundle", "plan", "--var", "lh_environment=test"],
            cwd=bundle_path,
            capture_output=True,
            text=True
        )

        # Plan should succeed even without deployment
        assert result.returncode == 0, f"Bundle plan failed: {result.stderr}"

    def test_yaml_syntax_all_bundles(self):
        """Test YAML syntax for all bundle files"""
        import yaml

        bundle_files = list(Path("bundles").rglob("*.yml")) + list(Path("bundles").rglob("*.yaml"))

        for file_path in bundle_files:
            with open(file_path) as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"YAML syntax error in {file_path}: {e}")

    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist in bundle files"""
        import re

        secret_patterns = [
            r'password\s*[:=]\s*["\']?[^"\'\s]+',
            r'secret\s*[:=]\s*["\']?[^"\'\s]+',
            r'token\s*[:=]\s*["\']?[^"\'\s]+',
        ]

        bundle_files = list(Path("bundles").rglob("*.yml")) + list(Path("bundles").rglob("*.yaml"))

        for file_path in bundle_files:
            with open(file_path) as f:
                content = f.read()

            for pattern in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Allow variable references like ${var.secret}
                    if not match.group().startswith("${"):
                        pytest.fail(f"Potential hardcoded secret in {file_path}: {match.group()}")
