-- Combined view of entities and their sentiments
-- This model joins entity extractions with their corresponding sentiment analyses.

WITH entity_extraction AS (
    SELECT * FROM {{ source('analytics', 'entity_extraction') }}
),

sentiment_analysis AS (
    SELECT
        id,
        source_platform,
        original_text,
        sentiment_strength AS sentiment_score,
        overall_sentiment AS sentiment_label,
        sentiment_reasoning,
        artist_sentiment,
        confidence_score,
        analysis_date
    FROM {{ source('analytics', 'sentiment_analysis') }}
)

SELECT
    ee.id AS entity_extraction_id,
    ee.source_platform,
    ee.original_text,
    ee.extraction_date,
    ee.confidence_score AS entity_confidence_score,
    ee.entities_artists,
    ee.entities_artists_count,
    ee.entities_songs,
    ee.entities_songs_count,
    ee.entities_genres,
    ee.entities_genres_count,
    ee.entities_song_indicators,
    ee.entities_song_indicators_count,
    ee.entities_sentiment_indicators,
    ee.entities_sentiment_indicators_count,
    ee.entities_music_events,
    ee.entities_music_events_count,
    ee.entities_temporal_references,
    ee.entities_temporal_references_count,
    ee.entities_other_entities,
    ee.entities_other_entities_count,

    sa.id AS sentiment_analysis_id,
    sa.sentiment_score,
    sa.sentiment_label,
    sa.sentiment_reasoning,
    sa.artist_sentiment,
    sa.confidence_score AS sentiment_confidence_score,
    sa.analysis_date AS sentiment_analysis_date
FROM
    entity_extraction ee
LEFT JOIN
    sentiment_analysis sa ON ee.original_text = sa.original_text AND ee.source_platform = sa.source_platform
    -- Consider a more robust join key if available, e.g., a shared comment_id
    -- if entities and sentiments are linked to a common source record.
    -- If original_text is very long, this join could be inefficient or inexact.
