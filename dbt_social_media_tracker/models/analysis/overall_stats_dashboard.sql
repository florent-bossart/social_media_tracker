{{ config(materialized='view') }}

SELECT
    (SELECT COUNT(*) FROM {{ source('analytics', 'entity_extraction') }}) as total_extractions,
    (SELECT COUNT(*) FROM {{ source('analytics', 'sentiment_analysis') }}) as total_sentiments,
    (SELECT COUNT(DISTINCT artist_name) FROM {{ ref('int_extracted_artists') }}) as unique_artists,
    (SELECT AVG(sentiment_strength)
     FROM {{ source('analytics', 'sentiment_analysis') }}
     WHERE sentiment_strength IS NOT NULL) as avg_sentiment,
    (SELECT COUNT(*)
     FROM {{ source('analytics', 'sentiment_analysis') }}
     WHERE overall_sentiment = 'positive') as positive_count,
    (SELECT COUNT(*)
     FROM {{ source('analytics', 'sentiment_analysis') }}) as total_sentiment_count
