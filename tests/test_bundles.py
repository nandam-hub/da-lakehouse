import pytest
import yaml
from pathlib import Path

class TestBundleConfigurations:

    def test_common_yml_structure(self):
        """Test _common.yml has required structure"""
        common_path = Path("bundles/_common.yml")
        assert common_path.exists()

        with open(common_path) as f:
            config = yaml.safe_load(f)

        assert "variables" in config
        assert "service_principals" in config["variables"]
        assert "sandbox" in config["variables"]["service_principals"]["default"]

    def test_drs_bundle_structure(self):
        """Test DRS bundle configuration"""
        drs_path = Path("bundles/drs/databricks.yml")
        assert drs_path.exists()

        with open(drs_path) as f:
            config = yaml.safe_load(f)

        assert "include" in config
        assert "../_common.yml" in config["include"]

    def test_schema_configuration(self):
        """Test schema resource configuration"""
        schema_path = Path("bundles/drs/resources/raw.schema.yml")
        assert schema_path.exists()

        with open(schema_path) as f:
            config = yaml.safe_load(f)

        assert "resources" in config
        assert "schemas" in config["resources"]

        schema = config["resources"]["schemas"]["raw_schema"]
        assert "name" in schema
        assert "catalog_name" in schema
        assert "grants" in schema

    def test_service_principal_ids_format(self):
        """Test service principal IDs are valid UUIDs"""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

        common_path = Path("bundles/_common.yml")
        with open(common_path) as f:
            config = yaml.safe_load(f)

        principals = config["variables"]["service_principals"]["default"]
        for env, sp_id in principals.items():
            if not sp_id.startswith("#"):  # Skip commented entries
                assert re.match(uuid_pattern, sp_id), f"Invalid UUID for {env}: {sp_id}"
