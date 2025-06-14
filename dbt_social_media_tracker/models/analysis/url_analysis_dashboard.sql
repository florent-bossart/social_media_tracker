{{ config(materialized='view') }}

WITH url_extractions AS (
    -- Reddit URLs with artists
    SELECT 
        ee.entities_artists,
        ee.entities_genres,
        ee.confidence_score,
        ee.extraction_date,
        'reddit' as source_platform,
        unnest(crc.body_urls) as url,
        crc.author_clean as mention_author,
        crc.created_utc_fmt as mention_date,
        crp.title_clean as post_title,
        crp.source as subreddit
    FROM {{ source('analytics', 'entity_extraction') }} ee
    INNER JOIN {{ source('intermediate', 'cleaned_reddit_comments') }} crc 
        ON ee.original_text = crc.body_clean
    LEFT JOIN {{ source('intermediate', 'cleaned_reddit_posts') }} crp
        ON crc.post_id = crp.post_id
    WHERE ee.source_platform = 'reddit'
        AND ee.entities_artists IS NOT NULL
        AND crc.body_urls IS NOT NULL
        AND array_length(crc.body_urls, 1) > 0
    
    UNION ALL
    
    -- Reddit post URLs with artists
    SELECT 
        ee.entities_artists,
        ee.entities_genres,
        ee.confidence_score,
        ee.extraction_date,
        'reddit' as source_platform,
        unnest(crp.selftext_urls_array) as url,
        crp.author_clean as mention_author,
        crp.created_utc_fmt as mention_date,
        crp.title_clean as post_title,
        crp.source as subreddit
    FROM {{ source('analytics', 'entity_extraction') }} ee
    INNER JOIN {{ source('intermediate', 'cleaned_reddit_comments') }} crc 
        ON ee.original_text = crc.body_clean
    INNER JOIN {{ source('intermediate', 'cleaned_reddit_posts') }} crp
        ON crc.post_id = crp.post_id
    WHERE ee.source_platform = 'reddit'
        AND ee.entities_artists IS NOT NULL
        AND crp.selftext_urls_array IS NOT NULL
        AND array_length(crp.selftext_urls_array, 1) > 0
),
url_patterns AS (
    SELECT 
        url,
        CASE 
            WHEN url ILIKE '%youtube.com%' OR url ILIKE '%youtu.be%' THEN 'YouTube'
            WHEN url ILIKE '%spotify.com%' THEN 'Spotify'
            WHEN url ILIKE '%soundcloud.com%' THEN 'SoundCloud'
            WHEN url ILIKE '%bandcamp.com%' THEN 'Bandcamp'
            WHEN url ILIKE '%apple.com%' THEN 'Apple Music'
            WHEN url ILIKE '%amazon.com%' OR url ILIKE '%amazon.co.jp%' THEN 'Amazon Music'
            WHEN url ILIKE '%tidal.com%' THEN 'Tidal'
            WHEN url ILIKE '%deezer.com%' THEN 'Deezer'
            WHEN url ILIKE '%discogs.com%' THEN 'Discogs'
            WHEN url ILIKE '%last.fm%' THEN 'Last.fm'
            WHEN url ILIKE '%musicbrainz.org%' THEN 'MusicBrainz'
            WHEN url ILIKE '%genius.com%' THEN 'Genius'
            WHEN url ILIKE '%twitter.com%' OR url ILIKE '%x.com%' THEN 'Twitter/X'
            WHEN url ILIKE '%instagram.com%' THEN 'Instagram'
            WHEN url ILIKE '%facebook.com%' THEN 'Facebook'
            WHEN url ILIKE '%tiktok.com%' THEN 'TikTok'
            WHEN url ILIKE '%bilibili.com%' THEN 'Bilibili'
            WHEN url ILIKE '%niconico.jp%' OR url ILIKE '%nicovideo.jp%' THEN 'Niconico'
            WHEN url ILIKE '%reddit.com%' THEN 'Reddit'
            ELSE 'Other'
        END as url_category,
        jsonb_array_elements_text(entities_artists) as artist_name,
        source_platform,
        confidence_score,
        extraction_date,
        mention_author,
        mention_date,
        post_title,
        subreddit
    FROM url_extractions
)
SELECT 
    url_category,
    artist_name,
    COUNT(DISTINCT CONCAT(source_platform, '-', url, '-', mention_author, '-', mention_date::text)) as mention_count,
    COUNT(DISTINCT url) as unique_urls,
    COUNT(DISTINCT mention_author) as unique_authors,
    COUNT(DISTINCT subreddit) as unique_subreddits,
    AVG(confidence_score) as avg_confidence,
    MIN(mention_date) as first_mention,
    MAX(mention_date) as latest_mention,
    -- Sample URLs for reference (limit to prevent data bloat)
    array_agg(DISTINCT url) 
        FILTER (WHERE url IS NOT NULL) as sample_urls
FROM url_patterns
WHERE artist_name IS NOT NULL
    AND TRIM(artist_name) != ''
    AND LENGTH(TRIM(artist_name)) > 2
GROUP BY url_category, artist_name
HAVING COUNT(DISTINCT CONCAT(source_platform, '-', url, '-', mention_author, '-', mention_date::text)) >= 1
ORDER BY mention_count DESC, avg_confidence DESC
