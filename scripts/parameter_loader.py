#!/usr/bin/env python3
"""Utility to load and resolve parameters from parameters.yml"""

import os
import yaml
import re
from pathlib import Path

class ParameterLoader:
    def __init__(self, config_path="parameters.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        """Load YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _resolve_env_vars(self, value):
        """Resolve environment variables in string values"""
        if isinstance(value, str):
            # Replace ${VAR_NAME} with environment variable values
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)

            for match in matches:
                env_value = os.getenv(match, f"${{{match}}}")  # Keep placeholder if not found
                value = value.replace(f"${{{match}}}", env_value)

        return value

    def get_databricks_config(self, environment="sandbox"):
        """Get Databricks configuration for specified environment"""
        if environment not in self.config["databricks"]["environments"]:
            raise ValueError(f"Environment '{environment}' not found in configuration")

        env_config = self.config["databricks"]["environments"][environment]

        # Resolve environment variables
        resolved_config = {}
        for key, value in env_config.items():
            resolved_config[key] = self._resolve_env_vars(value)

        return resolved_config

    def get_service_principal(self, environment="sandbox"):
        """Get service principal ID for environment"""
        return self.config["service_principals"].get(environment)

    def get_oidc_config(self):
        """Get OIDC configuration"""
        oidc_config = self.config["oidc"]

        # Resolve environment variables
        resolved_config = {}
        for section, values in oidc_config.items():
            resolved_config[section] = {}
            for key, value in values.items():
                resolved_config[section][key] = self._resolve_env_vars(value)

        return resolved_config

    def get_secrets_config(self):
        """Get secrets configuration"""
        secrets_config = self.config["secrets"]

        # Resolve environment variables
        resolved_config = {}
        for key, value in secrets_config.items():
            resolved_config[key] = self._resolve_env_vars(value)

        return resolved_config

def main():
    """Example usage"""
    loader = ParameterLoader()

    # Get Databricks config for sandbox
    db_config = loader.get_databricks_config("sandbox")
    print("Databricks Config:", db_config)

    # Get service principal
    sp_id = loader.get_service_principal("sandbox")
    print("Service Principal:", sp_id)

    # Get OIDC config
    oidc_config = loader.get_oidc_config()
    print("OIDC Config:", oidc_config)

if __name__ == "__main__":
    main()
