{{ config(materialized='view') }}

SELECT
    artist_name,
    overall_sentiment,
    AVG(sentiment_strength) as avg_sentiment_score,
    CASE
        WHEN artist_name_lower = 'babymetal' THEN CAST(COUNT(*) * 0.2 AS INTEGER)
        ELSE COUNT(*)
    END as mention_count
FROM {{ ref('int_extracted_artists') }}
WHERE overall_sentiment IS NOT NULL
    AND artist_name_lower NOT IN ('moa', 'momo', 'su-metal', 'unknown')
    AND LENGTH(artist_name_lower) > 2
GROUP BY artist_name, artist_name_lower, overall_sentiment
HAVING COUNT(*) >= 3  -- Only artists with at least 3 mentions
ORDER BY mention_count DESC
