SELECT
    'entity_extraction' AS stage,
    count(*) AS record_count,
    min(ee.extraction_date) AS earliest_date,
    max(ee.extraction_date) AS latest_date,
    avg(ee.confidence_score) AS avg_confidence
FROM
    {{ source('analytics', 'entity_extraction') }} ee
UNION ALL
SELECT
    'sentiment_analysis' AS stage,
    count(*) AS record_count,
    min(sa.processing_date) AS earliest_date,
    max(sa.processing_date) AS latest_date,
    avg(sa.sentiment_confidence) AS avg_confidence
FROM
    {{ source('analytics', 'sentiment_analysis') }} sa
UNION ALL
SELECT
    'trend_analysis' AS stage,
    count(*) AS record_count,
    min(ta.first_seen) AS earliest_date,
    max(ta.last_seen) AS latest_date,
    avg(ta.trend_strength) AS avg_confidence
FROM
    {{ source('analytics', 'trend_analysis') }} ta
UNION ALL
SELECT
    'summarization' AS stage,
    count(*) AS record_count,
    min(sm.analysis_date) AS earliest_date,
    max(sm.analysis_date) AS latest_date,
    avg(sm.confidence_score) AS avg_confidence
FROM
    {{ source('analytics', 'summarization_metrics') }} sm
WHERE
    sm.analysis_date IS NOT NULL
