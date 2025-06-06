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
    min(sa.analysis_date) AS earliest_date,
    max(sa.analysis_date) AS latest_date,
    avg(sa.confidence_score) AS avg_confidence
FROM
    {{ source('analytics', 'sentiment_analysis') }} sa
UNION ALL
SELECT
    'artist_trends' AS stage,
    count(*) AS record_count,
    min(ta.first_seen) AS earliest_date,
    max(ta.last_seen) AS latest_date,
    avg(ta.trend_strength) AS avg_confidence
FROM
    {{ source('analytics', 'artist_trends') }} ta
UNION ALL
SELECT
    'summarization' AS stage,
    count(*) AS record_count,
    min(sm.analysis_date) AS earliest_date,
    max(sm.analysis_date) AS latest_date,
    avg(cast(sm.value as numeric)) AS avg_confidence
FROM
    {{ source('analytics', 'summarization_metrics') }} sm
WHERE
    sm.analysis_date IS NOT NULL
    AND sm.metric = 'confidence_score'
