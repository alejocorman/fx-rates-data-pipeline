{{ config(materialized = 'table') }}

with stg as (

    select *
    from {{ ref('stg_exchange_rates') }}

),

latest_date as (

    select
        max(rate_date) as max_rate_date
    from stg

)

select
    s.rate_date,
    s.base_currency,
    s.target_currency,
    s.exchange_rate,
    s.ingestion_date,
    case
        when s.rate_date = l.max_rate_date then true
        else false
    end as is_latest
from stg s
cross join latest_date l
