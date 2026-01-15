with source as(
    select * from {{ source('nppes_raw', 'nucc_taxonomy') }}
),
nucc_taxonomy_cleaned as(
select 
    Code,
    Grouping,
    Classification,
    Specialization

from source
where Code is not null
)
select * from nucc_taxonomy_cleaned