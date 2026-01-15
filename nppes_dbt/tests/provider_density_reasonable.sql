

select *
from {{ ref('fct_provider_density') }}
where providers_per_10k_population < 00 
