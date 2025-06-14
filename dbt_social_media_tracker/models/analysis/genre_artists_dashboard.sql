{{ config(materialized='view') }}

WITH exploded_data AS (
    SELECT
        ee.original_text,
        ee.source_platform,
        ee.confidence_score,
        ee.extraction_date,
        TRIM(jsonb_array_elements_text(ee.entities_genres)) as raw_genre,
        TRIM(jsonb_array_elements_text(ee.entities_artists)) as artist_name,
        sa.sentiment_strength
    FROM {{ source('analytics', 'entity_extraction') }} ee
    LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa
        ON ee.original_text = sa.original_text
    WHERE ee.entities_genres IS NOT NULL
        AND jsonb_array_length(ee.entities_genres) > 0
        AND ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
normalized_genre_artists AS (
    SELECT
        -- Apply the same normalization logic as other genre models
        CASE 
            WHEN LOWER(TRIM(raw_genre)) IN ('pop', 'j-pop', 'jpop', 'j pop') THEN 'J-Pop'
            WHEN LOWER(TRIM(raw_genre)) IN ('rock', 'j-rock', 'jrock', 'j rock') THEN 'J-Rock'
            WHEN LOWER(TRIM(raw_genre)) IN ('metal', 'j-metal', 'jmetal') THEN 'Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('hip hop', 'hip-hop', 'hiphop', 'rap') THEN 'Hip-Hop'
            WHEN LOWER(TRIM(raw_genre)) IN ('electronic', 'electro', 'edm') THEN 'Electronic'
            WHEN LOWER(TRIM(raw_genre)) IN ('indie', 'independent') THEN 'Indie'
            WHEN LOWER(TRIM(raw_genre)) IN ('alternative', 'alt') THEN 'Alternative'
            WHEN LOWER(TRIM(raw_genre)) IN ('punk', 'j-punk', 'jpunk') THEN 'Punk'
            WHEN LOWER(TRIM(raw_genre)) IN ('folk', 'j-folk', 'jfolk') THEN 'Folk'
            WHEN LOWER(TRIM(raw_genre)) IN ('jazz', 'j-jazz', 'jjazz') THEN 'Jazz'
            WHEN LOWER(TRIM(raw_genre)) IN ('classical', 'classic') THEN 'Classical'
            WHEN LOWER(TRIM(raw_genre)) IN ('blues', 'j-blues', 'jblues') THEN 'Blues'
            WHEN LOWER(TRIM(raw_genre)) IN ('country', 'j-country', 'jcountry') THEN 'Country'
            WHEN LOWER(TRIM(raw_genre)) IN ('reggae', 'j-reggae', 'jreggae') THEN 'Reggae'
            WHEN LOWER(TRIM(raw_genre)) IN ('funk', 'j-funk', 'jfunk') THEN 'Funk'
            WHEN LOWER(TRIM(raw_genre)) IN ('soul', 'j-soul', 'jsoul') THEN 'Soul'
            WHEN LOWER(TRIM(raw_genre)) IN ('r&b', 'rnb', 'r and b', 'rhythm and blues') THEN 'R&B'
            WHEN LOWER(TRIM(raw_genre)) IN ('vocal', 'vocals') THEN 'Vocal'
            WHEN LOWER(TRIM(raw_genre)) IN ('instrumental', 'instru') THEN 'Instrumental'
            WHEN LOWER(TRIM(raw_genre)) IN ('acoustic', 'unplugged') THEN 'Acoustic'
            WHEN LOWER(TRIM(raw_genre)) IN ('experimental', 'avant-garde') THEN 'Experimental'
            WHEN LOWER(TRIM(raw_genre)) IN ('progressive', 'prog') THEN 'Progressive'
            WHEN LOWER(TRIM(raw_genre)) IN ('symphonic', 'orchestra', 'orchestral') THEN 'Symphonic'
            WHEN LOWER(TRIM(raw_genre)) IN ('ambient', 'chillout', 'chill') THEN 'Ambient'
            WHEN LOWER(TRIM(raw_genre)) IN ('dance', 'dancefloor') THEN 'Dance'
            WHEN LOWER(TRIM(raw_genre)) IN ('house', 'tech house') THEN 'House'
            WHEN LOWER(TRIM(raw_genre)) IN ('techno', 'tech') THEN 'Techno'
            WHEN LOWER(TRIM(raw_genre)) IN ('trance', 'psytrance') THEN 'Trance'
            WHEN LOWER(TRIM(raw_genre)) IN ('dubstep', 'dub step') THEN 'Dubstep'
            WHEN LOWER(TRIM(raw_genre)) IN ('garage', 'uk garage') THEN 'Garage'
            WHEN LOWER(TRIM(raw_genre)) IN ('drum and bass', 'dnb', 'd&b', 'drum&bass') THEN 'Drum & Bass'
            WHEN LOWER(TRIM(raw_genre)) IN ('breakbeat', 'break beat') THEN 'Breakbeat'
            WHEN LOWER(TRIM(raw_genre)) IN ('hardcore', 'hard core') THEN 'Hardcore'
            WHEN LOWER(TRIM(raw_genre)) IN ('hardstyle', 'hard style') THEN 'Hardstyle'
            WHEN LOWER(TRIM(raw_genre)) IN ('new wave', 'newwave') THEN 'New Wave'
            WHEN LOWER(TRIM(raw_genre)) IN ('post rock', 'post-rock', 'postrock') THEN 'Post-Rock'
            WHEN LOWER(TRIM(raw_genre)) IN ('post punk', 'post-punk', 'postpunk') THEN 'Post-Punk'
            WHEN LOWER(TRIM(raw_genre)) IN ('shoegaze', 'shoe gaze') THEN 'Shoegaze'
            WHEN LOWER(TRIM(raw_genre)) IN ('grunge', 'grung') THEN 'Grunge'
            WHEN LOWER(TRIM(raw_genre)) IN ('emo', 'emotional') THEN 'Emo'
            WHEN LOWER(TRIM(raw_genre)) IN ('screamo', 'scream') THEN 'Screamo'
            WHEN LOWER(TRIM(raw_genre)) IN ('metalcore', 'metal core') THEN 'Metalcore'
            WHEN LOWER(TRIM(raw_genre)) IN ('deathcore', 'death core') THEN 'Deathcore'
            WHEN LOWER(TRIM(raw_genre)) IN ('black metal', 'blackmetal') THEN 'Black Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('death metal', 'deathmetal') THEN 'Death Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('power metal', 'powermetal') THEN 'Power Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('heavy metal', 'heavymetal') THEN 'Heavy Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('thrash metal', 'thrashmetal', 'thrash') THEN 'Thrash Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('speed metal', 'speedmetal') THEN 'Speed Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('doom metal', 'doommetal', 'doom') THEN 'Doom Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('sludge metal', 'sludgemetal', 'sludge') THEN 'Sludge Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('stoner metal', 'stonermetal', 'stoner') THEN 'Stoner Metal'
            WHEN LOWER(TRIM(raw_genre)) IN ('nu metal', 'numetal', 'nu-metal') THEN 'Nu Metal'
            -- Default: Use proper title case for other genres
            ELSE INITCAP(LOWER(TRIM(raw_genre)))
        END as normalized_genre,
        artist_name,
        confidence_score,
        sentiment_strength,
        source_platform,
        extraction_date
    FROM exploded_data
    WHERE raw_genre IS NOT NULL
        AND TRIM(raw_genre) != ''
        AND artist_name IS NOT NULL
        AND TRIM(artist_name) != ''
        AND LENGTH(TRIM(artist_name)) > 2
),
genre_artist_stats AS (
    SELECT
        normalized_genre as genre_name,
        -- Normalize artist names to handle duplicates like "BABYMETAL", "Babymetal", "BabyMetal"
        CASE 
            WHEN LOWER(TRIM(artist_name)) = 'babymetal' THEN 'BABYMETAL'
            WHEN LOWER(TRIM(artist_name)) = 'one ok rock' THEN 'ONE OK ROCK'
            WHEN LOWER(TRIM(artist_name)) = 'yui' THEN 'YUI'
            WHEN LOWER(TRIM(artist_name)) = 'ado' THEN 'Ado'
            WHEN LOWER(TRIM(artist_name)) = 'yoasobi' THEN 'YOASOBI'
            WHEN LOWER(TRIM(artist_name)) = 'lisa' THEN 'LiSA'
            WHEN LOWER(TRIM(artist_name)) = 'king gnu' THEN 'King Gnu'
            WHEN LOWER(TRIM(artist_name)) = 'mrs. green apple' THEN 'Mrs. GREEN APPLE'
            WHEN LOWER(TRIM(artist_name)) = 'eve' THEN 'Eve'
            WHEN LOWER(TRIM(artist_name)) = 'fujii kaze' THEN 'Fujii Kaze'
            WHEN LOWER(TRIM(artist_name)) = 'aimer' THEN 'Aimer'
            WHEN LOWER(TRIM(artist_name)) = 'perfume' THEN 'Perfume'
            WHEN LOWER(TRIM(artist_name)) = 'scandal' THEN 'SCANDAL'
            WHEN LOWER(TRIM(artist_name)) = 'radwimps' THEN 'RADWIMPS'
            WHEN LOWER(TRIM(artist_name)) = 'bump of chicken' THEN 'BUMP OF CHICKEN'
            WHEN LOWER(TRIM(artist_name)) = 'asian kung-fu generation' THEN 'ASIAN KUNG-FU GENERATION'
            WHEN LOWER(TRIM(artist_name)) = 'official hige dandism' THEN 'Official髭男dism'
            WHEN LOWER(TRIM(artist_name)) = 'yorushika' THEN 'ヨルシカ'
            WHEN LOWER(TRIM(artist_name)) = 'kenshi yonezu' THEN 'Kenshi Yonezu'
            WHEN LOWER(TRIM(artist_name)) = 'yonezu kenshi' THEN 'Kenshi Yonezu'
            -- For other artists, use proper title case
            ELSE INITCAP(LOWER(TRIM(artist_name)))
        END as normalized_artist_name,
        COUNT(DISTINCT CONCAT(source_platform, '||', extraction_date)) as mention_count,
        AVG(confidence_score) as avg_confidence,
        AVG(COALESCE(sentiment_strength, 5.0)) as sentiment_score,
        COUNT(DISTINCT source_platform) as platform_count
    FROM normalized_genre_artists
    WHERE normalized_genre IS NOT NULL
        AND TRIM(normalized_genre) != ''
        AND artist_name IS NOT NULL
        AND TRIM(artist_name) != ''
        AND LENGTH(TRIM(artist_name)) > 2
    GROUP BY normalized_genre, 
        CASE 
            WHEN LOWER(TRIM(artist_name)) = 'babymetal' THEN 'BABYMETAL'
            WHEN LOWER(TRIM(artist_name)) = 'one ok rock' THEN 'ONE OK ROCK'
            WHEN LOWER(TRIM(artist_name)) = 'yui' THEN 'YUI'
            WHEN LOWER(TRIM(artist_name)) = 'ado' THEN 'Ado'
            WHEN LOWER(TRIM(artist_name)) = 'yoasobi' THEN 'YOASOBI'
            WHEN LOWER(TRIM(artist_name)) = 'lisa' THEN 'LiSA'
            WHEN LOWER(TRIM(artist_name)) = 'king gnu' THEN 'King Gnu'
            WHEN LOWER(TRIM(artist_name)) = 'mrs. green apple' THEN 'Mrs. GREEN APPLE'
            WHEN LOWER(TRIM(artist_name)) = 'eve' THEN 'Eve'
            WHEN LOWER(TRIM(artist_name)) = 'fujii kaze' THEN 'Fujii Kaze'
            WHEN LOWER(TRIM(artist_name)) = 'aimer' THEN 'Aimer'
            WHEN LOWER(TRIM(artist_name)) = 'perfume' THEN 'Perfume'
            WHEN LOWER(TRIM(artist_name)) = 'scandal' THEN 'SCANDAL'
            WHEN LOWER(TRIM(artist_name)) = 'radwimps' THEN 'RADWIMPS'
            WHEN LOWER(TRIM(artist_name)) = 'bump of chicken' THEN 'BUMP OF CHICKEN'
            WHEN LOWER(TRIM(artist_name)) = 'asian kung-fu generation' THEN 'ASIAN KUNG-FU GENERATION'
            WHEN LOWER(TRIM(artist_name)) = 'official hige dandism' THEN 'Official髭男dism'
            WHEN LOWER(TRIM(artist_name)) = 'yorushika' THEN 'ヨルシカ'
            WHEN LOWER(TRIM(artist_name)) = 'kenshi yonezu' THEN 'Kenshi Yonezu'
            WHEN LOWER(TRIM(artist_name)) = 'yonezu kenshi' THEN 'Kenshi Yonezu'
            -- For other artists, use proper title case
            ELSE INITCAP(LOWER(TRIM(artist_name)))
        END
    HAVING COUNT(DISTINCT CONCAT(source_platform, '||', extraction_date)) >= 2
)
SELECT
    genre_name,
    normalized_artist_name as artist_name,
    mention_count,
    avg_confidence,
    sentiment_score,
    platform_count,
    -- Rank artists within each genre by mention count
    ROW_NUMBER() OVER (PARTITION BY genre_name ORDER BY mention_count DESC) as artist_rank
FROM genre_artist_stats
ORDER BY genre_name, mention_count DESC
