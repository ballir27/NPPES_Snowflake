-- Which is the speciality mix in each state?

select
    provider_state_name as state,
    specialty_classification,
    count(distinct npi) as provider_count
from {{ ref('dim_provider_directory') }}
group by
    provider_state_name,
    specialty_classification
