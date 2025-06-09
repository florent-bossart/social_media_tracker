{{ config(materialized='view') }}

WITH deduplicated_data AS (
    SELECT DISTINCT ON (ee.original_text, ee.source_platform)
        ee.original_text,
        ee.source_platform,
        ee.entities_genres,
        ee.confidence_score,
        sa.sentiment_strength,
        sa.overall_sentiment,
        ee.extraction_date
    FROM {{ source('analytics', 'entity_extraction') }} ee
    LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa 
        ON ee.original_text = sa.original_text
    WHERE ee.entities_genres IS NOT NULL
        AND jsonb_array_length(ee.entities_genres) > 0
),
genre_text_pairs AS (
    SELECT DISTINCT
        LOWER(jsonb_array_elements_text(dd.entities_genres)) as genre_lower,
        dd.original_text,
        dd.source_platform,
        dd.confidence_score,
        dd.sentiment_strength,
        dd.extraction_date
    FROM deduplicated_data dd
    WHERE dd.entities_genres IS NOT NULL
        AND jsonb_array_length(dd.entities_genres) > 0
),
genre_stats AS (
    SELECT
        genre_lower,
        COUNT(DISTINCT CONCAT(original_text, '||', source_platform)) as mention_count,
        AVG(confidence_score) as trend_strength,
        AVG(COALESCE(sentiment_strength, 5.0)) as sentiment_score
    FROM genre_text_pairs
    GROUP BY genre_lower
    HAVING COUNT(DISTINCT CONCAT(original_text, '||', source_platform)) >= 5
)
SELECT
    INITCAP(genre_lower) as genre,
    CASE
        WHEN genre_lower = 'metal' THEN CAST(mention_count * 1 AS INTEGER)
        ELSE mention_count
    END as mention_count,
    sentiment_score,
    trend_strength,
    trend_strength as popularity_score
FROM genre_stats
WHERE genre_lower != 'babymetal'
    AND LENGTH(genre_lower) > 2
ORDER BY mention_count DESC
