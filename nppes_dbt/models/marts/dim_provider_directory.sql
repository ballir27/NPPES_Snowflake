-- This model creates a dimension table for provider directory information

with providers as (
    select *
    from {{ ref('stg_npi_data') }}
    where npi is not null
),

deduped as (
    select *
    from (
        select *,
            row_number() over (
                partition by npi
                order by provider_postal_code desc, provider_organization_name desc
            ) as rn
        from providers
    ) t
    where rn = 1
)

select
    d.npi,
    d.provider_first_name,
    d.provider_last_name,
    d.provider_organization_name,
    d.provider_gender_code,
    t.classification as specialty_classification,
    t.specialization,
    d.provider_city_name,
    d.provider_state_name,
    z.county,
    d.provider_postal_code
from deduped d
left join {{ ref('stg_nucc_taxonomy') }} t
    on d.provider_taxonomy_code_1 = t.code
left join {{ ref('stg_zip_data') }} z
    on d.provider_postal_code = z.zip
