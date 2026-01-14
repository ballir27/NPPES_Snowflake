-- 3.what is the speciality mix in a given region?

select
    provider_state_name as state,
    county,
    specialty_classification,
    specialization,
    count(distinct npi) as provider_count
from {{ ref('dim_provider_directory') }}
group by 1,2,3,4
order by state, county, specialty_classification
