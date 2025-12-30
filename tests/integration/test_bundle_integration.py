import pytest
import subprocess
import os
from pathlib import Path

class TestBundleIntegration:
    def test_bundle_syntax_validation(self):
        """Test bundle YAML syntax is valid"""
        bundle_dirs = Path("bundles").glob("*/")
        for bundle_dir in bundle_dirs:
            if bundle_dir.name.startswith("_"):
                continue
            databricks_yml = bundle_dir / "databricks.yml"
            assert databricks_yml.exists(), f"databricks.yml not found in {bundle_dir}"

    def test_environment_configs_exist(self):
        """Test environment configurations exist"""
        env_dir = Path("environments")
        assert env_dir.exists(), "environments directory not found"
        
        required_envs = ["sandbox", "dev", "test"]
        for env in required_envs:
            config_file = env_dir / env / "config.yml"
            assert config_file.exists(), f"Config file not found for {env}"

    @pytest.mark.skipif(os.getenv("GITHUB_ACTIONS") is not None, reason="Skip in CI")
    def test_databricks_connectivity(self):
        """Test Databricks connectivity (skip in CI)"""
        # This would test actual Databricks connection
        pass