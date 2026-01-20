-- 4. where might there be gaps in health care coverage?

with pop_by_zip as (
    select
        zip_code,
        sum(CAST(Total_Population AS INTEGER)) as total_population
    from {{ ref('stg_api_data') }}
    group by zip_code
),

providers_with_population as (
    select
        d.npi,
        d.provider_state_name as state,
        d.county,
        d.provider_postal_code_5 as zip,
        1 as provider_count
    from {{ ref('dim_provider_directory') }} d
)

, provider_counts as (
    select
        state,
        county,
        zip,
        sum(provider_count) as provider_count
    from providers_with_population
    group by state, county, zip
)

select
    pc.state,
    pc.county,
    sum(pop.total_population) as total_population,
    sum(pc.provider_count) as provider_count,
    round(sum(pc.provider_count) * 10000.0 / nullif(sum(pop.total_population),0),2) as providers_per_10k_population
from provider_counts pc
left join pop_by_zip pop
    on pc.zip = pop.zip_code
group by pc.state, pc.county
order by pc.state, pc.county
