{{ config(materialized='view') }}

SELECT
    COUNT(DISTINCT artist_name_lower) as artists_without_genre
FROM {{ ref('int_extracted_artists') }}
WHERE has_genre = 0
