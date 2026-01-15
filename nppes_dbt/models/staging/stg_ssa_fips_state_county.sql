with source as(
    select * from {{ source('nppes_raw', 'ssa_fips_state_county') }}
),
ssa_fips_state_county_cleaned as(
select
   fipscounty as Fips_County,
   countyname_fips as Fips_County_Name,
   state_name as State,
   cbsa_name as CBSA_Name

from source

)
select Fips_County,
       Fips_County_Name,
       State,
       CBSA_Name 
from ssa_fips_state_county_cleaned