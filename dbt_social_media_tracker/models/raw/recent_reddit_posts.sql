{{ config(
    materialized='view',
    schema='intermediate'
) }}

SELECT
    *
FROM
    {{ source('raw', 'reddit_posts') }}
WHERE
    fetch_date >= current_date - INTERVAL '7 days'
