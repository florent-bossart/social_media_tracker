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
            {{ source('analytics', 'trend_analysis') }}
        WHERE
            trend_analysis.trend_direction = 'up'
    ) AS trending_up_count,
    (
        SELECT
            round(avg(sentiment_analysis.sentiment_strength)::numeric, 2) AS round
        FROM
            {{ source('analytics', 'sentiment_analysis') }}
    ) AS avg_sentiment,
    (
        SELECT
            round(avg(summarization_metrics.confidence_score)::numeric, 2) AS round
        FROM
            {{ source('analytics', 'summarization_metrics') }}
    ) AS avg_confidence,
    (
        SELECT
            max(entity_extraction.extraction_date) AS max
        FROM
            {{ source('analytics', 'entity_extraction') }}
    ) AS latest_analysis_date
