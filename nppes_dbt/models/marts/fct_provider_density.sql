-- 2.which areas have the most/least providers per capita?

with provider_counts as (
    select
        provider_postal_code as zip,
        count(distinct npi) as provider_count
    from {{ ref('dim_provider_directory') }}
    group by provider_postal_code
),

population as (
    select
        zip_code as zip,
        total_population
    from {{ ref('stg_api_data') }}
)

select
    p.zip,
    p.provider_count,
    pop.total_population,
    coalesce(round(
        p.provider_count * 10000.0 / nullif(pop.total_population, 0), 2
    ), 0) as providers_per_10k_population
from provider_counts p
left join population pop
    on p.zip = pop.zip
