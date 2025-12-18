# `raw` Layer Databricks Asset Bundles

This directory contains [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/) that deploy Unity Catalog Schemas and `EXTERNAL` Volumes for the `raw` layer of the Lakehouse.

Each subdirectory represents a data source family (e.g., `guidewire_cda`, `drs`) and contains a complete bundle definition.

---

## Quick Start

### Prerequisites

1. **Databricks CLI** installed and configured, per this setup repo
    - https://github.com/amic-app/da-de-windev-setup


2. **Authentication profiles** configured in `~/.databrickscfg`
   ```ini
   [dev]
   host = https://amic-enterprise-workspace.cloud.databricks.com
   token = # found in BeyondTrust for Databricks - enterprise_object_owner_dev

   [test]
   host = https://amic-enterprise-workspace.cloud.databricks.com
   token = # found in BeyondTrust for Databricks - enterprise_object_owner_test
   ```

### Deploy a Bundle

```bash
# Navigate to the bundle directory
cd bundles/guidewire_cda

# Validate the bundle configuration
databricks bundle validate -t deva --profile dev

# Deploy the bundle
databricks bundle deploy -t deva --profile dev

# Destroy a bundle (use with caution!)
databricks bundle destroy -t deva --profile dev
```

---

## Shared Configuration (`_common.yml`)

The `_common.yml` file contains variables that are shared across all bundles in this repository. This ensures consistency and reduces duplication.

### What's Shared

**Service Principal Mapping** - Single source of truth for environment-specific service principals:
```yaml
service_principals:
  dev: 8323ced5-d447-4a03-b1c9-243d5fae00c5  # enterprise_object_owner_dev
  test: fb3648e1-7d19-4a94-a4db-5f69eaf8cf8b # enterprise_object_owner_test
  prod: 6f148b62-472e-40c4-bb1d-35aa176822bf # enterprise_object_owner_prod
```

**Environment Variables** - Common variable definitions used by all bundles:
- `amic_environment` - AMIC environment suffix (deva, testb, qas, prod)
- `aws_environment` - AWS bucket environment (dev or prod)
- `lh_environment` - Lakehouse catalog prefix (dev, test, prod)

### How to Use `_common.yml` in a Bundle

Include it at the top of your `databricks.yml`:

```yaml
bundle:
  name: your_bundle_name

include:
  - ../_common.yml           # Shared variables
  - resources/raw.schema.yml
  - resources/raw.volume.yml
```

>[!WARNING]
Important YAML anchors (`&anchor_name`) cannot be shared across files. Each bundle must define its own anchors, but they can reference the shared variables from `_common.yml` using `${var.service_principals.dev}`.

### When to Update `_common.yml`

- **Service principal IDs change** - Update once, applies to all bundles
- **New environment added** - Add to the `service_principals` map
- **New shared variable needed** - Add to the `variables` section


## Bundle Structure Reference

```
bundles/
├── _common.yml                    # Shared variables and configuration
├── README.md                      # This file
├── guidewire_cda/                 # Example bundle
│   ├── databricks.yml             # Bundle configuration & targets
│   ├── README.md                  # Bundle-specific documentation
│   └── resources/
│       ├── raw.schema.yml         # Schema resource definition
│       └── raw.volume.yml         # Volume resource definition
└── drs/                           # Example bundle
    ├── databricks.yml
    └── resources/
        ├── raw.schema.yml
        └── raw.volume.yml
```


## See Also

- [Repository README](../README.md) - Why we split raw and bronze layers
- [Databricks Asset Bundles Documentation](https://docs.databricks.com/aws/en/dev-tools/bundles/)
- [Unity Catalog External Volumes](https://docs.databricks.com/aws/en/connect/unity-catalog/volumes.html)
