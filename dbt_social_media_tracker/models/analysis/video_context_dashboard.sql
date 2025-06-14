{{ config(materialized='view') }}

WITH video_artist_mentions AS (
    SELECT 
        cyv.video_id,
        cyv.title_clean as video_title,
        cyv.channel_title_clean,
        cyv.published_at as video_published_at,
        cyv.view_count,
        cyv.like_count,
        cyv.comment_count as total_comments,
        cyv.duration_seconds,
        cyv.keyword_clean,
        cyv.fetch_date,
        -- Artist mentions
        jsonb_array_elements_text(ee.entities_artists) as artist_name,
        jsonb_array_elements_text(ee.entities_genres) as genre_name,
        ee.confidence_score,
        ee.extraction_date,
        cyc.comment_id,
        cyc.author_clean as comment_author,
        cyc.published_at as comment_published_at,
        ee.original_text as comment_text
    FROM {{ source('analytics', 'entity_extraction') }} ee
    INNER JOIN {{ source('intermediate', 'cleaned_youtube_comments') }} cyc 
        ON ee.original_text = cyc.text_clean
    INNER JOIN {{ source('intermediate', 'cleaned_youtube_videos') }} cyv
        ON cyc.video_id = cyv.video_id
    WHERE ee.source_platform = 'youtube'
        AND ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
video_metrics AS (
    SELECT 
        video_id,
        video_title,
        channel_title_clean,
        video_published_at,
        view_count,
        like_count,
        total_comments,
        duration_seconds,
        keyword_clean,
        -- Artist mention metrics
        COUNT(DISTINCT artist_name) as unique_artists_mentioned,
        COUNT(DISTINCT genre_name) as unique_genres_mentioned,
        COUNT(*) as total_artist_mentions,
        COUNT(DISTINCT comment_author) as unique_commenters,
        AVG(confidence_score) as avg_confidence,
        -- Top mentioned artists
        array_agg(DISTINCT artist_name ORDER BY artist_name) 
            FILTER (WHERE artist_name IS NOT NULL) as artists_mentioned,
        array_agg(DISTINCT genre_name ORDER BY genre_name) 
            FILTER (WHERE genre_name IS NOT NULL) as genres_mentioned,
        -- Engagement metrics
        ROUND(
            ((COUNT(*)::float / NULLIF(total_comments, 0)) * 100)::numeric, 2
        ) as artist_mention_percentage,
        MIN(comment_published_at) as first_artist_mention,
        MAX(comment_published_at) as latest_artist_mention
    FROM video_artist_mentions
    GROUP BY 
        video_id, video_title, channel_title_clean, video_published_at,
        view_count, like_count, total_comments, duration_seconds, keyword_clean
)
SELECT 
    video_id,
    video_title,
    'https://www.youtube.com/watch?v=' || video_id as video_url,
    channel_title_clean,
    video_published_at,
    view_count,
    like_count,
    total_comments,
    ROUND(duration_seconds / 60.0, 1) as duration_minutes,
    keyword_clean,
    unique_artists_mentioned,
    unique_genres_mentioned,
    total_artist_mentions,
    unique_commenters,
    avg_confidence,
    artist_mention_percentage,
    artists_mentioned,
    genres_mentioned,
    first_artist_mention,
    latest_artist_mention,
    -- Engagement scoring
    CASE 
        WHEN artist_mention_percentage >= 10 THEN 'High'
        WHEN artist_mention_percentage >= 5 THEN 'Medium'
        ELSE 'Low'
    END as artist_engagement_level,
    -- Music content indicators
    CASE 
        WHEN keyword_clean ILIKE '%music%' 
            OR video_title ILIKE '%music%'
            OR video_title ILIKE '%song%'
            OR video_title ILIKE '%album%'
            OR video_title ILIKE '%mv%'
            OR video_title ILIKE '%official%'
        THEN true 
        ELSE false 
    END as is_music_content,
    -- Video freshness
    CASE 
        WHEN video_published_at >= CURRENT_DATE - INTERVAL '30 days' THEN 'Recent'
        WHEN video_published_at >= CURRENT_DATE - INTERVAL '90 days' THEN 'Moderate'
        ELSE 'Older'
    END as video_age_category
FROM video_metrics
WHERE unique_artists_mentioned >= 1
ORDER BY total_artist_mentions DESC, avg_confidence DESC, view_count DESC
