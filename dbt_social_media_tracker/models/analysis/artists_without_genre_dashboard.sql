{{ config(materialized='view') }}

WITH all_artists AS (
    SELECT DISTINCT
        LOWER(TRIM(jsonb_array_elements_text(ee.entities_artists))) as artist_name
    FROM {{ source('analytics', 'entity_extraction') }} ee
    WHERE ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
artists_with_genres AS (
    SELECT DISTINCT
        LOWER(TRIM(jsonb_array_elements_text(ee.entities_artists))) as artist_name
    FROM {{ source('analytics', 'entity_extraction') }} ee
    WHERE ee.entities_artists IS NOT NULL
        AND ee.entities_genres IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
        AND jsonb_array_length(ee.entities_genres) > 0
)
SELECT
    COUNT(*) as artists_without_genre
FROM all_artists a
WHERE a.artist_name NOT IN (SELECT artist_name FROM artists_with_genres)
    AND a.artist_name != ''
    AND a.artist_name IS NOT NULL
