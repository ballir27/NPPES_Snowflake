with source as(
    select * from {{ source('nppes_raw', 'npi_data') }}
),
npi_cleaned as(
select 
    "NPI" as NPI,
    "Entity Type Code" as "Entity_Type",
    "Replacement NPI" as "Replacement_NPI",
    "Employer Identification Number (EIN)" as "Employer_Identification_Number",
    "Provider Organization Name (Legal Business Name)" as "Provider_Organization_Name",
    "Provider Last Name (Legal Name)" as "Provider_Last_Name",
    "Provider First Name" as "Provider_First_Name",
    "Provider Middle Name" as "Provider_Middle_Name",
    "Provider Sex Code" as "Provider_Gender_Code",
    "Certification Date" as "Certificate_Date",
    "Last Update Date" as "Last_Update_Date",
    "NPI Deactivation Date" as "NPI_Deactivation_Date",
    "Provider First Line Business Mailing Address" as "Provider_Address_1",
    "Provider Second Line Business Mailing Address" as "Provider_Address_2",
    "Provider Business Mailing Address City Name" as "Provider_City_Name",
    "Provider Business Mailing Address State Name" as "Provider_State_Name",
    "Provider Business Mailing Address Postal Code" as "Provider_Postal_Code",
    "Provider Business Mailing Address Country Code (If outside U.S.)" as "Provider_Country_Code",
    "Provider Business Mailing Address Telephone Number" as "Provider_Telephone_Number",
    "Provider Business Mailing Address Fax Number" as "Provider_Fax_Number",
    "Healthcare Provider Taxonomy Code_1" as "Provider_Taxonomy_Code_1"

from source
where "NPI" is not null
)
select "NPI",
       "Entity_Type",
       "Replacement_NPI",
       "Employer_Identification_Number",
       "Provider_Organization_Name",
       "Provider_Last_Name",
       "Provider_First_Name",
       "Provider_Middle_Name",
       "Provider_Gender_Code",
       "Certificate_Date",
       "Last_Update_Date",
       "NPI_Deactivation_Date",
       "Provider_Address_1",
       "Provider_Address_2",
       "Provider_City_Name",
       "Provider_State_Name",
       "Provider_Postal_Code",
       "Provider_Country_Code",
       "Provider_Telephone_Number",
       "Provider_Fax_Number",
       "Provider_Taxonomy_Code_1"
from npi_cleaned