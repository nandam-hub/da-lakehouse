import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.parameter_loader import ParameterLoader

class TestParameterLoader:
    def test_load_config(self):
        """Test loading configuration"""
        loader = ParameterLoader()
        assert loader.config is not None
        assert "databricks" in loader.config

    def test_get_databricks_config_sandbox(self):
        """Test getting sandbox databricks config"""
        loader = ParameterLoader()
        config = loader.get_databricks_config("sandbox")
        assert config["host"] == "https://dbc-0c2248b3-6656.cloud.databricks.com"
        assert config["auth_type"] == "oauth-m2m"

    def test_get_service_principal(self):
        """Test getting service principal"""
        loader = ParameterLoader()
        sp_id = loader.get_service_principal("sandbox")
        assert sp_id is not None

    def test_environment_permissions(self):
        """Test getting environment permissions"""
        loader = ParameterLoader()
        permissions = loader.get_environment_permissions("sandbox")
        assert isinstance(permissions, list)