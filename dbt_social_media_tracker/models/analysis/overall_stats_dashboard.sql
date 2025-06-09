{{ config(materialized='view') }}

WITH unique_artists AS (
    SELECT DISTINCT jsonb_array_elements_text(entities_artists) as artist_name
    FROM {{ source('analytics', 'entity_extraction') }}
    WHERE entities_artists IS NOT NULL
        AND jsonb_array_length(entities_artists) > 0
)
SELECT
    (SELECT COUNT(*) FROM {{ source('analytics', 'entity_extraction') }}) as total_extractions,
    (SELECT COUNT(*) FROM {{ source('analytics', 'sentiment_analysis') }}) as total_sentiments,
    (SELECT COUNT(*) FROM unique_artists) as unique_artists,
    (SELECT AVG(sentiment_strength)
     FROM {{ source('analytics', 'sentiment_analysis') }}
     WHERE sentiment_strength IS NOT NULL) as avg_sentiment,
    (SELECT COUNT(*)
     FROM {{ source('analytics', 'sentiment_analysis') }}
     WHERE overall_sentiment = 'positive') as positive_count,
    (SELECT COUNT(*)
     FROM {{ source('analytics', 'sentiment_analysis') }}) as total_sentiment_count
