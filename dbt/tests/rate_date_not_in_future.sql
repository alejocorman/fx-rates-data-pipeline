select *
from {{ ref('exchange_rates') }}
where rate_date > current_date()