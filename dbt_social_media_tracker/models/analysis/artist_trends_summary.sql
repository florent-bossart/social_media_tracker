SELECT
    ta.entity_name AS artist_name,
    ta.mention_count,
    ta.sentiment_score,
    ta.trend_strength,
    ta.trend_direction,
    ta.engagement_level,
    ta.platforms,
    sa.overall_sentiment AS latest_sentiment,
    sa.confidence_score AS sentiment_confidence,
    ta.first_seen,
    ta.last_seen
FROM
    {{ source('analytics', 'artist_trends') }} ta
LEFT JOIN
    {{ source('analytics', 'sentiment_analysis') }} sa ON sa.artist_sentiment::text LIKE ('%' || ta.entity_name || '%')
WHERE
    ta.entity_type = 'artist'
ORDER BY
    ta.trend_strength DESC, ta.mention_count DESC
