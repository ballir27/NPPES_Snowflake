-- This model creates a dimension table for provider directory information

with providers as (
    select *
    from {{ ref('stg_npi_data') }}
    where npi is not null
    and provider_postal_code_5 is not null
      and (
            provider_organization_name is not null
         or (provider_first_name is not null and provider_last_name is not null)
      )
),

 deduped as (
    select *
    from (
        select *,
            row_number() over (
                partition by npi
                order by 
                    case when provider_first_name is not null and provider_last_name is not null then 1 else 0 end desc,
                    case when provider_organization_name is not null then 1 else 0 end desc,
                    last_update_date desc
            ) as rn
        from providers
    ) t
    where rn = 1
),
zip_to_county as (
    select
        zip,
        min(county) as county
    from {{ ref('stg_zip_data') }}
    group by zip
)

select
    d.npi,
    d.provider_first_name,
    d.provider_last_name,
    d.provider_organization_name,
        coalesce(
        nullif(concat_ws(' ', d.provider_first_name, d.provider_last_name), ''),
        d.provider_organization_name
    ) as provider_name,
    d.provider_gender_code,
    coalesce(t.classification, 'Unknown') as specialty_classification,
    t.specialization,
    d.provider_city_name,
    d.provider_state_name,
    coalesce(z.county, 'Unknown') as county,
    d.provider_postal_code_5
from deduped d
left join {{ ref('stg_nucc_taxonomy') }} t
    on d.provider_taxonomy_code_1 = t.code
left join zip_to_county z
    on d.provider_postal_code_5 = z.zip
