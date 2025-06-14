{{ config(materialized='view') }}

WITH author_mentions AS (
    -- YouTube author mentions
    SELECT 
        cyc.author_clean as author_name,
        'youtube' as platform,
        jsonb_array_elements_text(ee.entities_artists) as artist_name,
        jsonb_array_elements_text(ee.entities_genres) as genre_name,
        ee.confidence_score,
        ee.extraction_date,
        cyc.published_at as mention_date,
        cyc.video_id,
        cyv.channel_title_clean,
        cyv.view_count,
        cyv.title_clean as video_title
    FROM {{ source('analytics', 'entity_extraction') }} ee
    INNER JOIN {{ source('intermediate', 'cleaned_youtube_comments') }} cyc 
        ON ee.original_text = cyc.text_clean
    LEFT JOIN {{ source('intermediate', 'cleaned_youtube_videos') }} cyv
        ON cyc.video_id = cyv.video_id
    WHERE ee.source_platform = 'youtube'
        AND ee.entities_artists IS NOT NULL
        AND cyc.author_clean IS NOT NULL
        AND TRIM(cyc.author_clean) != ''
    
    UNION ALL
    
    -- Reddit author mentions
    SELECT 
        crc.author_clean as author_name,
        'reddit' as platform,
        jsonb_array_elements_text(ee.entities_artists) as artist_name,
        jsonb_array_elements_text(ee.entities_genres) as genre_name,
        ee.confidence_score,
        ee.extraction_date,
        crc.created_utc_fmt::timestamp as mention_date,
        CAST(crc.post_id AS TEXT) as video_id,  -- Use post_id as identifier
        crp.source as channel_title_clean,      -- Use subreddit as "channel"
        NULL::integer as view_count,
        crp.title_clean as video_title          -- Use post title
    FROM {{ source('analytics', 'entity_extraction') }} ee
    INNER JOIN {{ source('intermediate', 'cleaned_reddit_comments') }} crc 
        ON ee.original_text = crc.body_clean
    LEFT JOIN {{ source('intermediate', 'cleaned_reddit_posts') }} crp
        ON crc.post_id = crp.post_id
    WHERE ee.source_platform = 'reddit'
        AND ee.entities_artists IS NOT NULL
        AND crc.author_clean IS NOT NULL
        AND TRIM(crc.author_clean) != ''
),
author_stats AS (
    SELECT 
        author_name,
        platform,
        COUNT(DISTINCT CONCAT(platform, '-', video_id, '-', artist_name, '-', mention_date::text)) as total_mentions,
        COUNT(DISTINCT artist_name) as unique_artists_mentioned,
        COUNT(DISTINCT genre_name) as unique_genres_mentioned,
        COUNT(DISTINCT video_id) as unique_sources,
        COUNT(DISTINCT channel_title_clean) as unique_channels_subreddits,
        AVG(confidence_score) as avg_confidence,
        MIN(mention_date) as first_mention,
        MAX(mention_date) as latest_mention,
        -- Platform specific metrics
        AVG(CASE WHEN platform = 'youtube' THEN view_count END) as avg_video_views,
        -- Most mentioned artists and genres (without LIMIT in array_agg)
        array_agg(DISTINCT artist_name ORDER BY artist_name) 
            FILTER (WHERE artist_name IS NOT NULL) as artists_mentioned,
        array_agg(DISTINCT genre_name ORDER BY genre_name) 
            FILTER (WHERE genre_name IS NOT NULL) as genres_mentioned,
        array_agg(DISTINCT channel_title_clean ORDER BY channel_title_clean) 
            FILTER (WHERE channel_title_clean IS NOT NULL) as channels_subreddits
    FROM author_mentions
    WHERE artist_name IS NOT NULL
        AND TRIM(artist_name) != ''
        AND LENGTH(TRIM(artist_name)) > 2
    GROUP BY author_name, platform
),
author_influence_score AS (
    SELECT 
        *,
        -- Calculate influence score based on multiple factors
        (
            (total_mentions * 0.4) +
            (unique_artists_mentioned * 0.3) +
            (unique_sources * 0.2) +
            (avg_confidence * 10 * 0.1)
        ) as influence_score,
        -- Activity consistency
        EXTRACT(DAYS FROM (latest_mention - first_mention)) + 1 as activity_days,
        ROUND(
            (total_mentions::float / NULLIF(EXTRACT(DAYS FROM (latest_mention - first_mention)) + 1, 0))::numeric, 2
        ) as mentions_per_day
    FROM author_stats
)
SELECT 
    author_name,
    platform,
    total_mentions,
    unique_artists_mentioned,
    unique_genres_mentioned,
    unique_sources,
    unique_channels_subreddits,
    ROUND(avg_confidence::numeric, 3) as avg_confidence,
    first_mention,
    latest_mention,
    activity_days,
    mentions_per_day,
    ROUND(influence_score::numeric, 2) as influence_score,
    avg_video_views,
    artists_mentioned,
    genres_mentioned,
    channels_subreddits,
    -- Categorize authors
    CASE 
        WHEN influence_score >= 50 THEN 'High Influence'
        WHEN influence_score >= 20 THEN 'Medium Influence'
        WHEN influence_score >= 10 THEN 'Regular Contributor'
        ELSE 'Casual Mention'
    END as influence_category,
    -- Activity pattern
    CASE 
        WHEN mentions_per_day >= 1 THEN 'Daily Active'
        WHEN mentions_per_day >= 0.5 THEN 'Frequent'
        WHEN mentions_per_day >= 0.1 THEN 'Regular'
        ELSE 'Occasional'
    END as activity_pattern
FROM author_influence_score
WHERE total_mentions >= 1  -- Filter out very casual users
ORDER BY influence_score DESC, total_mentions DESC
