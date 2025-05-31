SELECT
    sa.source_platform,
    count(*) AS total_comments,
    avg(sa.sentiment_strength) AS avg_sentiment_strength,
    count(
        CASE
            WHEN sa.overall_sentiment = 'positive' THEN 1
            ELSE NULL
        END) AS positive_count,
    count(
        CASE
            WHEN sa.overall_sentiment = 'neutral' THEN 1
            ELSE NULL
        END) AS neutral_count,
    count(
        CASE
            WHEN sa.overall_sentiment = 'negative' THEN 1
            ELSE NULL
        END) AS negative_count,
    round(
        count(
            CASE
                WHEN sa.overall_sentiment = 'positive' THEN 1
                ELSE NULL
            END
        )::numeric * 100.0 / count(*)::numeric,
        2
    ) AS positive_percentage
FROM
    {{ source('analytics', 'sentiment_analysis') }} sa
GROUP BY
    sa.source_platform
ORDER BY
    avg(sa.sentiment_strength) DESC
