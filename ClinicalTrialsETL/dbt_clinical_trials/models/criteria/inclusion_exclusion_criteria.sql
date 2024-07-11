
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

with cte as (
    SELECT
        protocol_section__identification_module__nct_id AS nct_id
--        , protocol_section__eligibility_module__eligibility_criteria
        , regexp_extract(
            protocol_section__eligibility_module__eligibility_criteria
            , '(?i)inclusion( criteria)?:?(?-i)[\n\r]*([\S\s]*?)(?i)exclusion( criteria)?(?-i)'
            , 2
          ) AS inclusion_criteria
        , regexp_extract(
            protocol_section__eligibility_module__eligibility_criteria
            , '(?i)exclusion( criteria)?(?-i):?[\n\r]*([\S\s]*)'
            , 2
          ) AS exclusion_criteria
        , concat('https://clinicaltrials.gov/study/', nct_id) as URL
    FROM {{ source('clinical_trials', 'clinical_trials') }}
)
select *
from cte
