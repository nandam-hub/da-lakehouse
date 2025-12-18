# da-lakehouse-raw

[Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/) that enable Schema and External Volume creation for the `raw` layer of the Lakehouse.


## Why Split Data Ingestion into `raw` and `bronze` Repositories?

![why_raw_bundles](docs/why_raw_bundles.png)


### 1. Single Source of Truth for Raw Data

Since there's only one `raw` source per `(amic_app_id, amic_environment)`, we need infrastructure that reflects this constraint.

- **This repository (`da-lakehouse-raw`)**: Creates and manages the foundational `raw` layer
  - Unity Catalog schemas (e.g., `guidewire_cda_deva`)
  - External volumes pointing to S3 buckets
  - Deployed once per environment with `mode: production`

- **The `da-lakehouse-bronze` repository**: Builds on top of the `raw` layer
  - Delta tables, streaming jobs, DLT, and transformations
  - Multiple concurrent development deployments allowed
  - Each developer/feature can have isolated bronze schemas

### 2. Prevent Deployment Conflicts

**Without separation**, every `databricks bundle deploy` from a developer would attempt to:
- Recreate or modify the shared `raw` schema
- Potentially drop and recreate volumes
- Create race conditions when multiple developers deploy simultaneously

**With separation**, deploying bronze bundles:
- Only references existing `raw` infrastructure (read-only dependency)
- Can't accidentally destroy shared raw data
- Developers work in isolated namespaces without stepping on each other

### 3. Independent Lifecycle Management

**Raw layer** (this repo):
- Changes infrequently (only when adding new data sources)
- Requires careful coordination and review
- Deployed by platform/data engineering team
- Tightly controlled permissions

**Bronze layer** (separate repo):
- Iterates rapidly during development
- Developers can experiment freely
- CI/CD can deploy/destroy test environments safely
- Schema changes and job logic evolve independently

### 4. Clear Ownership and Permissions

Separating concerns makes it easier to enforce least-privilege access:

- **Raw schemas/volumes**: Owned by service principals, read-only for most users
- **Bronze development schemas**: Developers have full control in their namespaces
- **Bronze production schemas**: Restricted to service principals (via CI/CD pipelines)

### 5. Simplified Mental Model

Developers working on bronze transformations don't need to understand or manage:
- External volume configuration
- S3 bucket permissions and paths
- Cross-environment schema naming conventions
- Catalog-level infrastructure decisions

They simply reference the raw data that already exists and focus on their transformation logic.
