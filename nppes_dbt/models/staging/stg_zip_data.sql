with source as (
    select * from {{ source('nppes_raw', 'zip_data') }}
),
zip_cleaned as (
    select 
        ZIP,
        COUNTY as County,
        USPS_ZIP_PREF_CITY as City,
        USPS_ZIP_PREF_STATE as State,
        RES_RATIO as Residential_ratio,
        BUS_RATIO as Business_ratio,
        OTH_RATIO as Other_ratio,
        TOT_RATIO as Total_ratio
    from source
)
select 
    ZIP,
    County,
    City,
    State,
    Residential_ratio,
    Business_ratio,
    Other_ratio,
    Total_ratio
from zip_cleaned
