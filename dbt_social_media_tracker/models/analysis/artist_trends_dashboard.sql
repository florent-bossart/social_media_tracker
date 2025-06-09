{{ config(materialized='view') }}

WITH deduplicated_data AS (
    SELECT DISTINCT ON (ee.original_text, ee.source_platform)
        ee.original_text,
        ee.source_platform,
        ee.entities_artists,
        ee.confidence_score,
        sa.sentiment_strength
    FROM {{ source('analytics', 'entity_extraction') }} ee
    LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa 
        ON ee.original_text = sa.original_text
    WHERE ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
artist_stats AS (
    SELECT
        LOWER(jsonb_array_elements_text(dd.entities_artists)) as artist_name_lower,
        COUNT(*) as mention_count,
        AVG(dd.confidence_score) as avg_confidence,
        COUNT(DISTINCT dd.source_platform) as platform_count,
        AVG(COALESCE(dd.sentiment_strength, 5.0)) as sentiment_score
    FROM deduplicated_data dd
    GROUP BY artist_name_lower
    HAVING COUNT(*) >= 3  -- Only artists with at least 3 mentions
),
filtered_artists AS (
    SELECT
        artist_name_lower,
        mention_count,
        avg_confidence,
        platform_count,
        sentiment_score
    FROM artist_stats
    WHERE artist_name_lower NOT ILIKE 'hall of%'
        AND artist_name_lower NOT ILIKE '%playlist%'
        AND artist_name_lower != 'moa'
        AND artist_name_lower != 'momo'
        AND artist_name_lower != 'su-metal'
        AND artist_name_lower != 'unknown'
        AND LENGTH(artist_name_lower) > 2
)
SELECT
    INITCAP(artist_name_lower) as artist_name,
    CASE
        WHEN artist_name_lower = 'babymetal' THEN CAST(mention_count * 0.2 AS INTEGER)
        ELSE mention_count
    END as mention_count,
    sentiment_score,
    avg_confidence as trend_strength,
    CASE
        WHEN sentiment_score >= 7 THEN 'positive'
        WHEN sentiment_score <= 4 THEN 'negative'
        ELSE 'neutral'
    END as trend_direction,
    CASE
        WHEN mention_count >= 50 THEN 'high'
        WHEN mention_count >= 20 THEN 'medium'
        ELSE 'low'
    END as engagement_level,
    platform_count
FROM filtered_artists
ORDER BY mention_count DESC
