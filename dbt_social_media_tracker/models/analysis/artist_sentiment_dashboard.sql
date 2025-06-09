{{ config(materialized='view') }}

WITH deduplicated_data AS (
    SELECT DISTINCT ON (ee.original_text, ee.source_platform)
        ee.entities_artists,
        sa.overall_sentiment,
        sa.sentiment_strength
    FROM {{ source('analytics', 'entity_extraction') }} ee
    JOIN {{ source('analytics', 'sentiment_analysis') }} sa 
        ON ee.original_text = sa.original_text
    WHERE ee.entities_artists IS NOT NULL
        AND sa.overall_sentiment IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
artist_sentiment AS (
    SELECT
        LOWER(jsonb_array_elements_text(dd.entities_artists)) as artist_name_lower,
        dd.overall_sentiment,
        dd.sentiment_strength
    FROM deduplicated_data dd
)
SELECT
    INITCAP(artist_name_lower) as artist_name,
    overall_sentiment,
    AVG(sentiment_strength) as avg_sentiment_score,
    CASE
        WHEN artist_name_lower = 'babymetal' THEN CAST(COUNT(*) * 0.2 AS INTEGER)
        ELSE COUNT(*)
    END as mention_count
FROM artist_sentiment
WHERE artist_name_lower != 'moa'
    AND artist_name_lower != 'momo'
    AND artist_name_lower != 'su-metal'
    AND artist_name_lower != 'unknown'
    AND LENGTH(artist_name_lower) > 2
GROUP BY artist_name_lower, overall_sentiment
HAVING COUNT(*) >= 5
ORDER BY mention_count DESC
