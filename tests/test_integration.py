import pytest
import subprocess
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.parameter_loader import ParameterLoader

class TestBundleIntegration:

    @pytest.fixture
    def bundle_path(self):
        return Path("bundles/drs")

    @pytest.fixture
    def databricks_config(self):
        """Load Databricks configuration from parameters.yml"""
        loader = ParameterLoader()
        return loader.get_databricks_config("sandbox")

    def test_bundle_validate(self, bundle_path, databricks_config):
        """Test databricks bundle validate command"""
        # Set environment variables from config
        env = os.environ.copy()
        env["DATABRICKS_HOST"] = databricks_config["host"]
        env["DATABRICKS_CLIENT_ID"] = databricks_config["client_id"]
        env["DATABRICKS_CLIENT_SECRET"] = databricks_config["client_secret"]
        env["DATABRICKS_AUTH_TYPE"] = databricks_config["auth_type"]

        result = subprocess.run(
            ["databricks", "bundle", "validate", "--target", "sandbox"],
            cwd=bundle_path,
            capture_output=True,
            text=True,
            env=env
        )

        assert result.returncode == 0, f"Bundle validation failed: {result.stderr}"

    def test_bundle_plan_dry_run(self, bundle_path, databricks_config):
        """Test databricks bundle plan (dry run)"""
        # Set environment variables from config
        env = os.environ.copy()
        env["DATABRICKS_HOST"] = databricks_config["host"]
        env["DATABRICKS_CLIENT_ID"] = databricks_config["client_id"]
        env["DATABRICKS_CLIENT_SECRET"] = databricks_config["client_secret"]
        env["DATABRICKS_AUTH_TYPE"] = databricks_config["auth_type"]

        result = subprocess.run(
            ["databricks", "bundle", "plan", "--target", "sandbox", "--var", "lh_environment=sandbox"],
            cwd=bundle_path,
            capture_output=True,
            text=True,
            env=env
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
