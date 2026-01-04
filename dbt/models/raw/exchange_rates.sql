{{ config(
    materialized='table',
    partition_by={
      "field": "rate_date",
      "data_type": "date"
    }
) }}

select
  cast(date as date) as rate_date,
  amount,
  base,
  rates,
  current_date() as ingestion_date,
  current_timestamp() as _ingested_at
from {{ source('raw', 'exchange_rates_gcs') }}