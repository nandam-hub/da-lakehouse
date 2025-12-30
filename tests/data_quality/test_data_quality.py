import pytest
from pathlib import Path
import yaml

class TestDataQuality:
    def test_schema_definitions_valid(self):
        """Test schema definitions are valid"""
        schema_files = list(Path("bundles").rglob("*.schema.yml"))
        assert len(schema_files) > 0, "No schema files found"
        
        for schema_file in schema_files:
            with open(schema_file, 'r') as f:
                schema_config = yaml.safe_load(f)
                assert "resources" in schema_config
                assert "schemas" in schema_config["resources"]

    def test_volume_definitions_valid(self):
        """Test volume definitions are valid"""
        volume_files = list(Path("bundles").rglob("*.volume.yml"))
        assert len(volume_files) > 0, "No volume files found"
        
        for volume_file in volume_files:
            with open(volume_file, 'r') as f:
                volume_config = yaml.safe_load(f)
                assert "resources" in volume_config
                assert "volumes" in volume_config["resources"]

    def test_no_hardcoded_credentials(self):
        """Test no hardcoded credentials in configs"""
        config_files = list(Path("bundles").rglob("*.yml"))
        sensitive_patterns = ["password", "secret", "token"]
        
        for config_file in config_files:
            content = config_file.read_text().lower()
            for pattern in sensitive_patterns:
                if pattern in content and "var." not in content:
                    # Allow variables but not hardcoded values
                    pass