{{ config(materialized='view') }}

WITH genre_normalization AS (
    SELECT
        id,
        analysis_timestamp,
        genre_name as original_genre_name,
        -- Apply comprehensive genre normalization
        CASE
            WHEN LOWER(TRIM(genre_name)) IN ('pop', 'j-pop', 'jpop', 'j pop') THEN 'J-Pop'
            WHEN LOWER(TRIM(genre_name)) IN ('rock', 'j-rock', 'jrock', 'j rock') THEN 'J-Rock'
            WHEN LOWER(TRIM(genre_name)) IN ('metal', 'j-metal', 'jmetal') THEN 'Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('hip hop', 'hip-hop', 'hiphop', 'rap') THEN 'Hip-Hop'
            WHEN LOWER(TRIM(genre_name)) IN ('electronic', 'electro', 'edm', 'electropop') THEN 'Electronic'
            WHEN LOWER(TRIM(genre_name)) IN ('indie', 'independent') THEN 'Indie'
            WHEN LOWER(TRIM(genre_name)) IN ('alternative', 'alt') THEN 'Alternative'
            WHEN LOWER(TRIM(genre_name)) IN ('punk', 'j-punk', 'jpunk') THEN 'Punk'
            WHEN LOWER(TRIM(genre_name)) IN ('folk', 'j-folk', 'jfolk', 'traditional folk') THEN 'Folk'
            WHEN LOWER(TRIM(genre_name)) IN ('jazz', 'j-jazz', 'jjazz') THEN 'Jazz'
            WHEN LOWER(TRIM(genre_name)) IN ('classical', 'classic', 'orchestral') THEN 'Classical'
            WHEN LOWER(TRIM(genre_name)) IN ('blues', 'j-blues', 'jblues') THEN 'Blues'
            WHEN LOWER(TRIM(genre_name)) IN ('country', 'j-country', 'jcountry') THEN 'Country'
            WHEN LOWER(TRIM(genre_name)) IN ('reggae', 'j-reggae', 'jreggae') THEN 'Reggae'
            WHEN LOWER(TRIM(genre_name)) IN ('funk', 'j-funk', 'jfunk') THEN 'Funk'
            WHEN LOWER(TRIM(genre_name)) IN ('soul', 'j-soul', 'jsoul') THEN 'Soul'
            WHEN LOWER(TRIM(genre_name)) IN ('r&b', 'rnb', 'r and b', 'rhythm and blues') THEN 'R&B'
            WHEN LOWER(TRIM(genre_name)) IN ('vocal', 'vocals') THEN 'Vocal'
            WHEN LOWER(TRIM(genre_name)) IN ('instrumental', 'instru') THEN 'Instrumental'
            WHEN LOWER(TRIM(genre_name)) IN ('acoustic', 'unplugged') THEN 'Acoustic'
            WHEN LOWER(TRIM(genre_name)) IN ('experimental', 'avant-garde') THEN 'Experimental'
            WHEN LOWER(TRIM(genre_name)) IN ('progressive', 'prog') THEN 'Progressive'
            WHEN LOWER(TRIM(genre_name)) IN ('symphonic', 'orchestra', 'orchestral') THEN 'Symphonic'
            WHEN LOWER(TRIM(genre_name)) IN ('ambient', 'chillout', 'chill') THEN 'Ambient'
            WHEN LOWER(TRIM(genre_name)) IN ('dance', 'dancefloor') THEN 'Dance'
            WHEN LOWER(TRIM(genre_name)) IN ('house', 'tech house') THEN 'House'
            WHEN LOWER(TRIM(genre_name)) IN ('techno', 'tech') THEN 'Techno'
            WHEN LOWER(TRIM(genre_name)) IN ('trance', 'psytrance') THEN 'Trance'
            WHEN LOWER(TRIM(genre_name)) IN ('dubstep', 'dub step') THEN 'Dubstep'
            WHEN LOWER(TRIM(genre_name)) IN ('garage', 'uk garage') THEN 'Garage'
            WHEN LOWER(TRIM(genre_name)) IN ('drum and bass', 'dnb', 'd&b', 'drum&bass') THEN 'Drum & Bass'
            WHEN LOWER(TRIM(genre_name)) IN ('breakbeat', 'break beat') THEN 'Breakbeat'
            WHEN LOWER(TRIM(genre_name)) IN ('hardcore', 'hard core') THEN 'Hardcore'
            WHEN LOWER(TRIM(genre_name)) IN ('hardstyle', 'hard style') THEN 'Hardstyle'
            WHEN LOWER(TRIM(genre_name)) IN ('new wave', 'newwave') THEN 'New Wave'
            WHEN LOWER(TRIM(genre_name)) IN ('post rock', 'post-rock', 'postrock') THEN 'Post-Rock'
            WHEN LOWER(TRIM(genre_name)) IN ('post punk', 'post-punk', 'postpunk') THEN 'Post-Punk'
            WHEN LOWER(TRIM(genre_name)) IN ('shoegaze', 'shoe gaze') THEN 'Shoegaze'
            WHEN LOWER(TRIM(genre_name)) IN ('grunge', 'grung') THEN 'Grunge'
            WHEN LOWER(TRIM(genre_name)) IN ('emo', 'emotional') THEN 'Emo'
            WHEN LOWER(TRIM(genre_name)) IN ('screamo', 'scream') THEN 'Screamo'
            WHEN LOWER(TRIM(genre_name)) IN ('metalcore', 'metal core') THEN 'Metalcore'
            WHEN LOWER(TRIM(genre_name)) IN ('deathcore', 'death core') THEN 'Deathcore'
            WHEN LOWER(TRIM(genre_name)) IN ('black metal', 'blackmetal') THEN 'Black Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('death metal', 'deathmetal') THEN 'Death Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('power metal', 'powermetal') THEN 'Power Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('heavy metal', 'heavymetal') THEN 'Heavy Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('thrash metal', 'thrashmetal', 'thrash') THEN 'Thrash Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('speed metal', 'speedmetal') THEN 'Speed Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('doom metal', 'doommetal', 'doom') THEN 'Doom Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('sludge metal', 'sludgemetal', 'sludge') THEN 'Sludge Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('stoner metal', 'stonermetal', 'stoner') THEN 'Stoner Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('nu metal', 'numetal', 'nu-metal') THEN 'Nu Metal'
            WHEN LOWER(TRIM(genre_name)) IN ('pop rock', 'poprock') THEN 'Pop Rock'
            -- Default: Use proper title case for other genres
            ELSE INITCAP(LOWER(TRIM(genre_name)))
        END as normalized_genre_name,
        popularity_score,
        sentiment_trend,
        artist_diversity,
        platforms_count,
        source_file
    FROM {{ source('analytics', 'trend_summary_top_genres') }}
    WHERE genre_name IS NOT NULL
        AND TRIM(genre_name) != ''
        AND LOWER(TRIM(genre_name)) NOT IN ('nan', 'null', 'none', '')
),
aggregated_genres AS (
    SELECT
        analysis_timestamp,
        normalized_genre_name as genre_name,
        SUM(popularity_score) as popularity_score,
        -- For sentiment_trend, take the value from the entry with highest popularity
        (ARRAY_AGG(sentiment_trend ORDER BY popularity_score DESC))[1] as sentiment_trend,
        SUM(artist_diversity) as artist_diversity,
        MAX(platforms_count) as platforms_count,
        -- Take source file from first entry (they should be the same for same timestamp)
        (ARRAY_AGG(source_file ORDER BY id))[1] as source_file,
        COUNT(*) as merged_entries_count
    FROM genre_normalization
    GROUP BY analysis_timestamp, normalized_genre_name
)
SELECT
    analysis_timestamp,
    genre_name,
    popularity_score,
    sentiment_trend,
    artist_diversity,
    platforms_count,
    source_file,
    merged_entries_count
FROM aggregated_genres
ORDER BY analysis_timestamp DESC, popularity_score DESC
