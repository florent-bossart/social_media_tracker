-- Intermediate model to extract and normalize artist data once
-- This avoids repeating expensive JSONB operations across multiple dashboard models
{{ config(materialized='table') }}

WITH deduplicated_extractions AS (
    SELECT DISTINCT ON (ee.original_text, ee.source_platform)
        ee.original_text,
        ee.source_platform,
        ee.entities_artists,
        ee.entities_genres,
        ee.confidence_score,
        sa.overall_sentiment,
        sa.sentiment_strength
    FROM {{ source('analytics', 'entity_extraction') }} ee
    LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa
        ON ee.original_text = sa.original_text
    WHERE ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
extracted_artists AS (
    SELECT
        original_text,
        source_platform,
        LOWER(TRIM(jsonb_array_elements_text(entities_artists))) as artist_name_lower,
        CASE
            WHEN entities_genres IS NOT NULL
                AND jsonb_array_length(entities_genres) > 0
            THEN 1
            ELSE 0
        END as has_genre,
        confidence_score,
        overall_sentiment,
        sentiment_strength
    FROM deduplicated_extractions
)
SELECT
    original_text,
    source_platform,
    artist_name_lower,
    INITCAP(artist_name_lower) as artist_name,
    has_genre,
    confidence_score,
    overall_sentiment,
    sentiment_strength
FROM extracted_artists
WHERE artist_name_lower != ''
    AND artist_name_lower IS NOT NULL
    AND artist_name_lower != 'moa'  -- Filter out known noise
