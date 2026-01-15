-- Ensure provider_count is never negative
select *
from {{ ref('fct_healthcare_gaps') }}
where provider_count < 0
