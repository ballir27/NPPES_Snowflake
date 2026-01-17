select *
from {{ ref('dim_provider_directory') }}
where provider_name is null
   or provider_postal_code_5 is null
