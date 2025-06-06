SELECT
    ta.first_seen AS analysis_date,
    count(DISTINCT ta.entity_name) AS unique_entities,
    avg(ta.sentiment_score) AS avg_sentiment,
    avg(ta.trend_strength) AS avg_trend_strength,
    count(
        CASE
            WHEN ta.trend_direction = 'positive' THEN 1
            ELSE NULL
        END) AS trending_up,
    count(
        CASE
            WHEN ta.trend_direction = 'negative' THEN 1
            ELSE NULL
        END) AS trending_down,
    count(
        CASE
            WHEN ta.trend_direction = 'neutral' THEN 1
            ELSE NULL
        END) AS trending_neutral
FROM
    {{ source('analytics', 'artist_trends') }} ta
GROUP BY
    ta.first_seen
ORDER BY
    ta.first_seen DESC
