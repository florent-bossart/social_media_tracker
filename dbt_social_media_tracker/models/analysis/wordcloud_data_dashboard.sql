{{ config(materialized='view') }}

SELECT
    word,
    frequency
FROM {{ source('analytics', 'wordcloud_data') }}
WHERE frequency >= 50
ORDER BY frequency DESC
