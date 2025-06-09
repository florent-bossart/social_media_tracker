{{ config(materialized='view') }}

WITH decoded_artists AS (
    SELECT
        *,
        {{ url_decode('entity_name') }} as decoded_entity_name,
        UPPER({{ url_decode('entity_name') }}) as normalized_name
    FROM {{ source('analytics', 'artist_trends') }}
),
deduped_artists AS (
    SELECT
        decoded_entity_name AS artist_name,
        trend_strength,
        mention_count AS mentions,
        sentiment_score,
        trend_direction AS sentiment_direction,
        platforms,
        last_seen,
        ROW_NUMBER() OVER (
            PARTITION BY normalized_name 
            ORDER BY mention_count ASC, trend_strength ASC
        ) as rn
    FROM decoded_artists
)
SELECT 
    artist_name,
    trend_strength,
    mentions,
    sentiment_score,
    sentiment_direction,
    platforms,
    last_seen
FROM deduped_artists
WHERE rn = 1
ORDER BY trend_strength DESC, mentions DESC
