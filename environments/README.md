# Environment-Specific Configuration

This directory contains environment-specific configurations for the Databricks Asset Bundles.

## Structure

```
environments/
├── sandbox/
│   └── config.yml
├── dev/
│   └── config.yml
└── test/
    └── config.yml
```

## Environment Hierarchy

- **sandbox**: Development sandbox environment
- **dev**: Development environment with sub-environments (deva, devb)
- **test**: Test environment with sub-environments (testa, testb, qas)

## Configuration Files

Each `config.yml` contains:
- Environment metadata
- Databricks connection settings (using AWS Secrets Manager)
- Service principal configuration
- Permissions configuration
- Sub-environment definitions (where applicable)

## Secrets Manager Integration

Credentials are pulled from AWS Secrets Manager using the syntax:
```yaml
client_secret: ${SECRET:secret-name:key}
```

Expected secret structure:
```json
{
  "host": "https://workspace.cloud.databricks.com",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "service_principal_id": "your-sp-id"
}
```

## Usage

The `parameter_loader.py` script automatically loads configurations from these folders, falling back to the main `parameters.yml` file if environment-specific configs are not found.

```python
from scripts.parameter_loader import ParameterLoader

loader = ParameterLoader()
config = loader.get_databricks_config("sandbox")
permissions = loader.get_environment_permissions("sandbox")
sub_envs = loader.get_sub_environments("dev")
```