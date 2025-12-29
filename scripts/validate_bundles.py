#!/usr/bin/env python3
"""Validate Databricks Asset Bundle configurations"""

import sys
import yaml
from pathlib import Path

REQUIRED_BUNDLE_FIELDS = ['resources']
REQUIRED_SCHEMA_FIELDS = ['name', 'catalog_name']
REQUIRED_VOLUME_FIELDS = ['name', 'catalog_name', 'schema_name']

def validate_yaml_syntax(file_path):
    """Validate YAML syntax"""
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        return True, None
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {e}"

def validate_bundle_structure(file_path, config):
    """Validate bundle structure"""
    errors = []

    if 'resources' not in config:
        errors.append("Missing 'resources' section")
        return errors

    resources = config['resources']

    # Validate schemas
    if 'schemas' in resources:
        for schema_name, schema_config in resources['schemas'].items():
            for field in REQUIRED_SCHEMA_FIELDS:
                if field not in schema_config:
                    errors.append(f"Schema '{schema_name}' missing required field: {field}")

    # Validate volumes
    if 'volumes' in resources:
        for volume_name, volume_config in resources['volumes'].items():
            for field in REQUIRED_VOLUME_FIELDS:
                if field not in volume_config:
                    errors.append(f"Volume '{volume_name}' missing required field: {field}")

    return errors

def main():
    all_errors = []

    for file_path in sys.argv[1:]:
        # Skip non-bundle files
        if not any(x in file_path for x in ['databricks.yml', 'raw.schema.yml', 'raw.volume.yml']):
            continue

        valid, error = validate_yaml_syntax(file_path)
        if not valid:
            all_errors.append(f"{file_path}: {error}")
            continue

        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)

            if config:
                structure_errors = validate_bundle_structure(file_path, config)
                for error in structure_errors:
                    all_errors.append(f"{file_path}: {error}")

        except Exception as e:
            all_errors.append(f"{file_path}: Validation error: {e}")

    if all_errors:
        print("BUNDLE VALIDATION ERRORS:")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)

    print("All bundles validated successfully")

if __name__ == "__main__":
    main()
