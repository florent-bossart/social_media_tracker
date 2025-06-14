{{ config(materialized='view') }}

WITH deduplicated_data AS (
    SELECT DISTINCT ON (ee.original_text, ee.source_platform)
        ee.original_text,
        ee.source_platform,
        ee.entities_genres,
        ee.confidence_score,
        sa.sentiment_strength,
        sa.overall_sentiment,
        ee.extraction_date
    FROM {{ source('analytics', 'entity_extraction') }} ee
    LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa
        ON ee.original_text = sa.original_text
    WHERE ee.entities_genres IS NOT NULL
        AND jsonb_array_length(ee.entities_genres) > 0
),
genre_text_pairs AS (
    SELECT DISTINCT
        LOWER(jsonb_array_elements_text(dd.entities_genres)) as genre_lower,
        dd.original_text,
        dd.source_platform,
        dd.confidence_score,
        dd.sentiment_strength,
        dd.extraction_date
    FROM deduplicated_data dd
    WHERE dd.entities_genres IS NOT NULL
        AND jsonb_array_length(dd.entities_genres) > 0
),
genre_stats AS (
    SELECT
        genre_lower,
        COUNT(DISTINCT CONCAT(original_text, '||', source_platform)) as mention_count,
        AVG(confidence_score) as trend_strength,
        AVG(COALESCE(sentiment_strength, 5.0)) as sentiment_score
    FROM genre_text_pairs
    GROUP BY genre_lower
    HAVING COUNT(DISTINCT CONCAT(original_text, '||', source_platform)) >= 5
),
normalized_genres AS (
    SELECT
        -- Normalize common genre variations with proper casing
        CASE 
            WHEN genre_lower IN ('pop', 'j-pop', 'jpop', 'j pop') THEN 'J-Pop'
            WHEN genre_lower IN ('rock', 'j-rock', 'jrock', 'j rock') THEN 'J-Rock'
            WHEN genre_lower IN ('metal', 'j-metal', 'jmetal') THEN 'Metal'
            WHEN genre_lower IN ('hip hop', 'hip-hop', 'hiphop', 'rap') THEN 'Hip-Hop'
            WHEN genre_lower IN ('electronic', 'electro', 'edm') THEN 'Electronic'
            WHEN genre_lower IN ('indie', 'independent') THEN 'Indie'
            WHEN genre_lower IN ('alternative', 'alt') THEN 'Alternative'
            WHEN genre_lower IN ('punk', 'j-punk', 'jpunk') THEN 'Punk'
            WHEN genre_lower IN ('folk', 'j-folk', 'jfolk') THEN 'Folk'
            WHEN genre_lower IN ('jazz', 'j-jazz', 'jjazz') THEN 'Jazz'
            WHEN genre_lower IN ('classical', 'classic') THEN 'Classical'
            WHEN genre_lower IN ('blues', 'j-blues', 'jblues') THEN 'Blues'
            WHEN genre_lower IN ('country', 'j-country', 'jcountry') THEN 'Country'
            WHEN genre_lower IN ('reggae', 'j-reggae', 'jreggae') THEN 'Reggae'
            WHEN genre_lower IN ('funk', 'j-funk', 'jfunk') THEN 'Funk'
            WHEN genre_lower IN ('soul', 'j-soul', 'jsoul') THEN 'Soul'
            WHEN genre_lower IN ('r&b', 'rnb', 'r and b', 'rhythm and blues') THEN 'R&B'
            WHEN genre_lower IN ('vocal', 'vocals') THEN 'Vocal'
            WHEN genre_lower IN ('instrumental', 'instru') THEN 'Instrumental'
            WHEN genre_lower IN ('acoustic', 'unplugged') THEN 'Acoustic'
            WHEN genre_lower IN ('experimental', 'avant-garde') THEN 'Experimental'
            WHEN genre_lower IN ('progressive', 'prog') THEN 'Progressive'
            WHEN genre_lower IN ('symphonic', 'orchestra', 'orchestral') THEN 'Symphonic'
            WHEN genre_lower IN ('ambient', 'chillout', 'chill') THEN 'Ambient'
            WHEN genre_lower IN ('dance', 'dancefloor') THEN 'Dance'
            WHEN genre_lower IN ('house', 'tech house') THEN 'House'
            WHEN genre_lower IN ('techno', 'tech') THEN 'Techno'
            WHEN genre_lower IN ('trance', 'psytrance') THEN 'Trance'
            WHEN genre_lower IN ('dubstep', 'dub step') THEN 'Dubstep'
            WHEN genre_lower IN ('garage', 'uk garage') THEN 'Garage'
            WHEN genre_lower IN ('drum and bass', 'dnb', 'd&b', 'drum&bass') THEN 'Drum & Bass'
            WHEN genre_lower IN ('breakbeat', 'break beat') THEN 'Breakbeat'
            WHEN genre_lower IN ('hardcore', 'hard core') THEN 'Hardcore'
            WHEN genre_lower IN ('hardstyle', 'hard style') THEN 'Hardstyle'
            WHEN genre_lower IN ('new wave', 'newwave') THEN 'New Wave'
            WHEN genre_lower IN ('post rock', 'post-rock', 'postrock') THEN 'Post-Rock'
            WHEN genre_lower IN ('post punk', 'post-punk', 'postpunk') THEN 'Post-Punk'
            WHEN genre_lower IN ('shoegaze', 'shoe gaze') THEN 'Shoegaze'
            WHEN genre_lower IN ('grunge', 'grung') THEN 'Grunge'
            WHEN genre_lower IN ('emo', 'emotional') THEN 'Emo'
            WHEN genre_lower IN ('screamo', 'scream') THEN 'Screamo'
            WHEN genre_lower IN ('metalcore', 'metal core') THEN 'Metalcore'
            WHEN genre_lower IN ('deathcore', 'death core') THEN 'Deathcore'
            WHEN genre_lower IN ('black metal', 'blackmetal') THEN 'Black Metal'
            WHEN genre_lower IN ('death metal', 'deathmetal') THEN 'Death Metal'
            WHEN genre_lower IN ('power metal', 'powermetal') THEN 'Power Metal'
            WHEN genre_lower IN ('heavy metal', 'heavymetal') THEN 'Heavy Metal'
            WHEN genre_lower IN ('thrash metal', 'thrashmetal', 'thrash') THEN 'Thrash Metal'
            WHEN genre_lower IN ('speed metal', 'speedmetal') THEN 'Speed Metal'
            WHEN genre_lower IN ('doom metal', 'doommetal', 'doom') THEN 'Doom Metal'
            WHEN genre_lower IN ('sludge metal', 'sludgemetal', 'sludge') THEN 'Sludge Metal'
            WHEN genre_lower IN ('stoner metal', 'stonermetal', 'stoner') THEN 'Stoner Metal'
            WHEN genre_lower IN ('nu metal', 'numetal', 'nu-metal') THEN 'Nu Metal'
            -- Default: Use proper title case for other genres
            ELSE INITCAP(genre_lower)
        END as normalized_genre,
        mention_count,
        sentiment_score,
        trend_strength
    FROM genre_stats
)
SELECT
    normalized_genre as genre,
    SUM(mention_count) as mention_count,
    AVG(sentiment_score) as sentiment_score,
    AVG(trend_strength) as trend_strength,
    AVG(trend_strength) as popularity_score
FROM normalized_genres
WHERE normalized_genre != 'Babymetal'
    AND normalized_genre != 'Momometal'
    AND normalized_genre != 'None'
    AND LENGTH(normalized_genre) > 2
GROUP BY normalized_genre
ORDER BY SUM(mention_count) DESC
