{{ config(materialized='view') }}

WITH platform_artists AS (
    SELECT
        ee.source_platform,
        jsonb_array_elements_text(ee.entities_artists) as artist_name
    FROM {{ source('analytics', 'entity_extraction') }} ee
    WHERE ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
)
SELECT
    ee.source_platform as platform,
    COUNT(*) as total_mentions,
    AVG(sa.sentiment_strength) as avg_sentiment,
    COALESCE(pa.active_artists, 0) as active_artists
FROM {{ source('analytics', 'entity_extraction') }} ee
LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa
    ON ee.original_text = sa.original_text
LEFT JOIN (
    SELECT
        source_platform,
        COUNT(DISTINCT artist_name) as active_artists
    FROM platform_artists
    GROUP BY source_platform
) pa ON ee.source_platform = pa.source_platform
GROUP BY ee.source_platform, pa.active_artists
ORDER BY total_mentions DESC
