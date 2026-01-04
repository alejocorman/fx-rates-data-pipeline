{{ config(materialized = 'view') }}

with source as (

    select
        rate_date,
        base as base_currency,
        rates,
        ingestion_date,
        _ingested_at as ingested_at
    from {{ ref('exchange_rates') }}

),

normalized as (

    select
        rate_date,
        base_currency,
        currency as target_currency,
        cast(rate as float64) as exchange_rate,
        ingestion_date,
        ingested_at
    from source,
    unnest([
        struct('EUR' as currency, rates.EUR as rate),
        struct('GBP' as currency, rates.GBP as rate),
        struct('JPY' as currency, rates.JPY as rate)
    ])
    where rate is not null

)

select
    rate_date,
    base_currency,
    target_currency,
    exchange_rate,
    ingestion_date,
    ingested_at
from normalized
