## Models

### Raw
Raw models mirror the source data structure with minimal transformations and
serve as the base layer for downstream models.

### Staging
Staging models normalize raw data by flattening nested fields, standardizing
data types and naming conventions, and defining a consistent grain. These models
are materialized as views.

### Marts
Mart models provide analytics-ready datasets with clear semantics and are
optimized for frequent querying. These models are materialized as tables.

## Running dbt

Run staging models and tests:
dbt run --select staging/
dbt test --select staging/

Run mart models and tests:
dbt run --select marts/
dbt test --select marts/