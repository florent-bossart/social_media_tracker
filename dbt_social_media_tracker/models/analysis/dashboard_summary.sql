SELECT
    CURRENT_DATE AS report_date,
    (
        SELECT
            count(*) AS count
        FROM
            {{ source('analytics', 'entity_extraction') }}
    ) AS total_extractions,
    (
        SELECT
            count(*) AS count
        FROM
            {{ source('analytics', 'sentiment_analysis') }}
    ) AS total_sentiments,
    (
        SELECT
            count(*) AS count
        FROM
            {{ source('analytics', 'artist_trends') }}
        WHERE
            artist_trends.trend_direction = 'positive'
    ) AS trending_up_count,
    (
        SELECT
            round(avg(sentiment_analysis.sentiment_strength)::numeric, 2) AS round
        FROM
            {{ source('analytics', 'sentiment_analysis') }}
    ) AS avg_sentiment,
    (
        SELECT
            round(avg(cast(summarization_metrics.value as numeric))::numeric, 2) AS round
        FROM
            {{ source('analytics', 'summarization_metrics') }}
        WHERE
            summarization_metrics.metric = 'confidence_score'
    ) AS avg_confidence,
    (
        SELECT
            max(entity_extraction.extraction_date) AS max
        FROM
            {{ source('analytics', 'entity_extraction') }}
    ) AS latest_analysis_date
