with source as(
    select * from {{ source('nppes_raw', 'api_data') }}
),
api_cleaned as(
select 
    "total_population" as Total_Population,
    "zip_code" as Zip_Code

from source
)
select Total_Population,Zip_Code from api_cleaned