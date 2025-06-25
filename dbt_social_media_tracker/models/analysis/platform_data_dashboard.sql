{{ config(materialized='view') }}

SELECT
    ee.source_platform as platform,
    COUNT(*) as total_mentions,
    AVG(sa.sentiment_strength) as avg_sentiment,
    COALESCE(ia.active_artists, 0) as active_artists
FROM {{ source('analytics', 'entity_extraction') }} ee
LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa
    ON ee.original_text = sa.original_text
LEFT JOIN (
    SELECT
        source_platform,
        COUNT(DISTINCT artist_name) as active_artists
    FROM {{ ref('int_extracted_artists') }}
    GROUP BY source_platform
) ia ON ee.source_platform = ia.source_platform
GROUP BY ee.source_platform, ia.active_artists
ORDER BY total_mentions DESC
