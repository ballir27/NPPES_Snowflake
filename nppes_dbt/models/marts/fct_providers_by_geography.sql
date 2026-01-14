-- 1.How many providers are in each state/country?

with providers as (
    select *
    from {{ ref('dim_provider_directory') }}
    where provider_state_name is not null
      and county is not null
),

counts as (
    select
        provider_state_name as state,
        county,
        count(distinct npi) as provider_count
    from providers
    group by 1,2
)

select *
from counts
order by state, county
