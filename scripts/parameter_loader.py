#!/usr/bin/env python3
"""Utility to load and resolve parameters from parameters.yml"""

import os
import yaml
import re
import boto3
import json
from pathlib import Path

class ParameterLoader:
    def __init__(self, config_path="parameters.yml", environments_dir="environments"):
        self.config_path = Path(config_path)
        self.environments_dir = Path(environments_dir)
        self.config = self._load_config()
        self.env_configs = self._load_environment_configs()

    def _load_config(self):
        """Load YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _load_environment_configs(self):
        """Load environment-specific configurations from environments folder"""
        env_configs = {}
        
        if not self.environments_dir.exists():
            return env_configs
            
        for env_dir in self.environments_dir.iterdir():
            if env_dir.is_dir():
                config_file = env_dir / "config.yml"
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        env_configs[env_dir.name] = yaml.safe_load(f)
                        
        return env_configs

    def _get_secret(self, secret_name, key):
        """Retrieve secret from AWS Secrets Manager with fallback to hardcoded values"""
        # Fallback values for sandbox when AWS is not configured
        fallback_secrets = {
            'databricks-sandbox-credentials': {
                'host': 'https://dbc-0c2248b3-6656.cloud.databricks.com',
                'client_id': '111986ad-4fc6-45b4-9469-e7c7c581cbb6',
                'client_secret': 'dose9b72dea76c379efe05c765be4c9bde18',
                'service_principal_id': '111986ad-4fc6-45b4-9469-e7c7c581cbb6'
            }
        }
        
        try:
            session = boto3.Session()
            client = session.client('secretsmanager')
            
            response = client.get_secret_value(SecretId=secret_name)
            secret_dict = json.loads(response['SecretString'])
            
            return secret_dict.get(key, f"SECRET_NOT_FOUND:{key}")
        except Exception:
            # Use fallback for sandbox
            if secret_name in fallback_secrets:
                return fallback_secrets[secret_name].get(key, f"FALLBACK_NOT_FOUND:{key}")
            return f"SECRET_ERROR:{key}"

    def _resolve_env_vars(self, value):
        """Resolve environment variables and secrets in string values"""
        if isinstance(value, str):
            # Replace ${SECRET:secret_name:key} with AWS Secrets Manager values
            secret_pattern = r'\$\{SECRET:([^:]+):([^}]+)\}'
            secret_matches = re.findall(secret_pattern, value)
            
            for secret_name, key in secret_matches:
                secret_value = self._get_secret(secret_name, key)
                value = value.replace(f"${{SECRET:{secret_name}:{key}}}", secret_value)
            
            # Replace ${VAR_NAME} with environment variable values
            env_pattern = r'\$\{([^}]+)\}'
            env_matches = re.findall(env_pattern, value)

            for match in env_matches:
                env_value = os.getenv(match, f"${{{match}}}")  # Keep placeholder if not found
                value = value.replace(f"${{{match}}}", env_value)

        return value

    def get_databricks_config(self, environment="sandbox"):
        """Get Databricks configuration for specified environment"""
        # Try environment-specific folder first
        if environment in self.env_configs:
            env_config = self.env_configs[environment]["databricks"]
        elif environment in self.config["databricks"]["environments"]:
            env_config = self.config["databricks"]["environments"][environment]
        else:
            raise ValueError(f"Environment '{environment}' not found in configuration")

        # Resolve environment variables
        resolved_config = {}
        for key, value in env_config.items():
            resolved_config[key] = self._resolve_env_vars(value)

        return resolved_config

    def get_service_principal(self, environment="sandbox"):
        """Get service principal ID for environment"""
        # Try environment-specific folder first
        if environment in self.env_configs:
            return self.env_configs[environment]["service_principal"]["id"]
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

    def get_environment_permissions(self, environment="sandbox"):
        """Get permissions configuration for environment"""
        if environment in self.env_configs:
            return self.env_configs[environment].get("permissions", [])
        return []

    def get_sub_environments(self, environment):
        """Get sub-environments for a given environment"""
        if environment in self.env_configs:
            return self.env_configs[environment].get("sub_environments", [])
        return []

def main():
    """Example usage"""
    loader = ParameterLoader()

    # Get Databricks config for sandbox
    db_config = loader.get_databricks_config("sandbox")
    print("Databricks Config:", db_config)

    # Get service principal
    sp_id = loader.get_service_principal("sandbox")
    print("Service Principal:", sp_id)

    # Get environment permissions
    permissions = loader.get_environment_permissions("sandbox")
    print("Permissions:", permissions)

    # Get sub-environments for dev
    sub_envs = loader.get_sub_environments("dev")
    print("Dev Sub-environments:", sub_envs)

if __name__ == "__main__":
    main()
