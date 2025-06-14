{{ config(materialized='view') }}

WITH youtube_enriched AS (
    SELECT 
        ee.id,
        ee.source_platform,
        ee.original_text,
        ee.entities_artists,
        ee.entities_genres,
        ee.confidence_score,
        ee.extraction_date,
        ee.source_date,
        -- YouTube metadata
        cyc.video_id,
        cyc.comment_id,
        cyc.author_clean as comment_author,
        cyc.published_at as comment_published_at,
        cyc.keyword_clean,
        -- Video metadata
        cyv.title_clean as video_title,
        cyv.channel_title_clean,
        cyv.view_count,
        cyv.like_count,
        cyv.comment_count as video_comment_count,
        cyv.duration_seconds
    FROM {{ source('analytics', 'entity_extraction') }} ee
    INNER JOIN {{ source('intermediate', 'cleaned_youtube_comments') }} cyc 
        ON ee.original_text = cyc.text_clean
    LEFT JOIN {{ source('intermediate', 'cleaned_youtube_videos') }} cyv
        ON cyc.video_id = cyv.video_id
    WHERE ee.source_platform = 'youtube'
        AND ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
reddit_enriched AS (
    SELECT 
        ee.id,
        ee.source_platform,
        ee.original_text,
        ee.entities_artists,
        ee.entities_genres,
        ee.confidence_score,
        ee.extraction_date,
        ee.source_date,
        -- Reddit metadata
        crc.comment_id,
        crc.post_id,
        crc.author_clean as comment_author,
        crc.body_urls,
        crc.created_utc_fmt as comment_created_at,
        -- Post metadata
        crp.title_clean as post_title,
        crp.author_clean as post_author,
        crp.source as subreddit,
        crp.selftext_urls_array as post_urls
    FROM {{ source('analytics', 'entity_extraction') }} ee
    INNER JOIN {{ source('intermediate', 'cleaned_reddit_comments') }} crc 
        ON ee.original_text = crc.body_clean
    LEFT JOIN {{ source('intermediate', 'cleaned_reddit_posts') }} crp
        ON crc.post_id = crp.post_id
    WHERE ee.source_platform = 'reddit'
        AND ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
artist_stats_enriched AS (
    SELECT
        LOWER(jsonb_array_elements_text(entities_artists)) as artist_name_lower,
        jsonb_array_elements_text(entities_artists) as artist_name,
        source_platform,
        -- Fix: Count distinct mentions based on unique content identifiers
        COUNT(DISTINCT CASE 
            WHEN source_platform = 'youtube' THEN CONCAT(video_id, '-', comment_id)
            WHEN source_platform = 'reddit' THEN CONCAT(post_id, '-', comment_id)
            ELSE id::text
        END) as mention_count,
        AVG(confidence_score) as avg_confidence,
        COUNT(DISTINCT CASE 
            WHEN source_platform = 'youtube' THEN video_id 
            WHEN source_platform = 'reddit' THEN CAST(post_id AS TEXT)
        END) as unique_sources_count,
        -- YouTube specific metrics
        COUNT(DISTINCT CASE WHEN source_platform = 'youtube' THEN CONCAT(video_id, '-', comment_id) END) as youtube_mentions,
        COUNT(DISTINCT CASE WHEN source_platform = 'youtube' THEN video_id END) as unique_videos,
        COUNT(DISTINCT CASE WHEN source_platform = 'youtube' THEN channel_title_clean END) as unique_channels,
        AVG(CASE WHEN source_platform = 'youtube' THEN view_count END) as avg_video_views,
        -- Reddit specific metrics  
        COUNT(DISTINCT CASE WHEN source_platform = 'reddit' THEN CONCAT(post_id, '-', comment_id) END) as reddit_mentions,
        COUNT(DISTINCT CASE WHEN source_platform = 'reddit' THEN post_id END) as unique_posts,
        COUNT(DISTINCT CASE WHEN source_platform = 'reddit' THEN subreddit END) as unique_subreddits,
        COUNT(DISTINCT CASE WHEN source_platform = 'reddit' AND body_urls IS NOT NULL THEN CONCAT(post_id, '-', comment_id) END) as mentions_with_urls
    FROM (
        SELECT entities_artists, source_platform, confidence_score, video_id, channel_title_clean, view_count, 
               comment_id::text, id, NULL::text as post_id, NULL::text as subreddit, NULL::text[] as body_urls FROM youtube_enriched
        UNION ALL
        SELECT entities_artists, source_platform, confidence_score, NULL::text as video_id, NULL::text as channel_title_clean, NULL::integer as view_count,
               comment_id::text, id, post_id::text as post_id, subreddit, body_urls FROM reddit_enriched
    ) combined
    GROUP BY artist_name_lower, artist_name, source_platform
)
SELECT
    artist_name,
    SUM(mention_count) as total_mentions,
    SUM(youtube_mentions) as youtube_mentions,
    SUM(reddit_mentions) as reddit_mentions,
    SUM(unique_videos) as unique_videos_mentioned,
    SUM(unique_channels) as unique_channels,
    SUM(unique_posts) as unique_posts_mentioned,
    SUM(unique_subreddits) as unique_subreddits,
    SUM(mentions_with_urls) as mentions_with_urls,
    AVG(avg_confidence) as trend_strength,
    AVG(avg_video_views) as avg_video_views,
    ROUND(
        ((SUM(youtube_mentions)::float / NULLIF(SUM(mention_count), 0)) * 100)::numeric, 2
    ) as youtube_percentage,
    ROUND(
        ((SUM(reddit_mentions)::float / NULLIF(SUM(mention_count), 0)) * 100)::numeric, 2
    ) as reddit_percentage
FROM artist_stats_enriched
WHERE artist_name_lower NOT IN ('moa', 'momo', 'su-metal', 'unknown')
    AND artist_name_lower NOT ILIKE 'hall of%'
    AND artist_name_lower NOT ILIKE '%playlist%'
    AND LENGTH(artist_name_lower) > 2
GROUP BY artist_name_lower, artist_name
HAVING SUM(mention_count) >= 1
ORDER BY total_mentions DESC, trend_strength DESC
