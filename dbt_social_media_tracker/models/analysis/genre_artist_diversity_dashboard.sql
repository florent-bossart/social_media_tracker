{{ config(materialized='view') }}

SELECT
    genre,
    artist_diversity,
    popularity_score
FROM {{ source('analytics', 'genre_trends') }}
WHERE genre IS NOT NULL
ORDER BY artist_diversity DESC NULLS LAST, popularity_score DESC
