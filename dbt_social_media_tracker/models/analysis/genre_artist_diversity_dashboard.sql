{{ config(materialized='view') }}

WITH normalized_genre_data AS (
    SELECT
        -- Apply the same normalization logic as genre_trends_dashboard
        CASE
            WHEN LOWER(genre) IN ('pop', 'j-pop', 'jpop', 'j pop') THEN 'J-Pop'
            WHEN LOWER(genre) IN ('rock', 'j-rock', 'jrock', 'j rock') THEN 'J-Rock'
            WHEN LOWER(genre) IN ('metal', 'j-metal', 'jmetal') THEN 'Metal'
            WHEN LOWER(genre) IN ('hip hop', 'hip-hop', 'hiphop', 'rap') THEN 'Hip-Hop'
            WHEN LOWER(genre) IN ('electronic', 'electro', 'edm') THEN 'Electronic'
            WHEN LOWER(genre) IN ('indie', 'independent') THEN 'Indie'
            WHEN LOWER(genre) IN ('alternative', 'alt') THEN 'Alternative'
            WHEN LOWER(genre) IN ('punk', 'j-punk', 'jpunk') THEN 'Punk'
            WHEN LOWER(genre) IN ('folk', 'j-folk', 'jfolk') THEN 'Folk'
            WHEN LOWER(genre) IN ('jazz', 'j-jazz', 'jjazz') THEN 'Jazz'
            WHEN LOWER(genre) IN ('classical', 'classic') THEN 'Classical'
            WHEN LOWER(genre) IN ('blues', 'j-blues', 'jblues') THEN 'Blues'
            WHEN LOWER(genre) IN ('country', 'j-country', 'jcountry') THEN 'Country'
            WHEN LOWER(genre) IN ('reggae', 'j-reggae', 'jreggae') THEN 'Reggae'
            WHEN LOWER(genre) IN ('funk', 'j-funk', 'jfunk') THEN 'Funk'
            WHEN LOWER(genre) IN ('soul', 'j-soul', 'jsoul') THEN 'Soul'
            WHEN LOWER(genre) IN ('r&b', 'rnb', 'r and b', 'rhythm and blues') THEN 'R&B'
            WHEN LOWER(genre) IN ('vocal', 'vocals') THEN 'Vocal'
            WHEN LOWER(genre) IN ('instrumental', 'instru') THEN 'Instrumental'
            WHEN LOWER(genre) IN ('acoustic', 'unplugged') THEN 'Acoustic'
            WHEN LOWER(genre) IN ('experimental', 'avant-garde') THEN 'Experimental'
            WHEN LOWER(genre) IN ('progressive', 'prog') THEN 'Progressive'
            WHEN LOWER(genre) IN ('symphonic', 'orchestra', 'orchestral') THEN 'Symphonic'
            WHEN LOWER(genre) IN ('ambient', 'chillout', 'chill') THEN 'Ambient'
            WHEN LOWER(genre) IN ('dance', 'dancefloor') THEN 'Dance'
            WHEN LOWER(genre) IN ('house', 'tech house') THEN 'House'
            WHEN LOWER(genre) IN ('techno', 'tech') THEN 'Techno'
            WHEN LOWER(genre) IN ('trance', 'psytrance') THEN 'Trance'
            WHEN LOWER(genre) IN ('dubstep', 'dub step') THEN 'Dubstep'
            WHEN LOWER(genre) IN ('garage', 'uk garage') THEN 'Garage'
            WHEN LOWER(genre) IN ('drum and bass', 'dnb', 'd&b', 'drum&bass') THEN 'Drum & Bass'
            WHEN LOWER(genre) IN ('breakbeat', 'break beat') THEN 'Breakbeat'
            WHEN LOWER(genre) IN ('hardcore', 'hard core') THEN 'Hardcore'
            WHEN LOWER(genre) IN ('hardstyle', 'hard style') THEN 'Hardstyle'
            WHEN LOWER(genre) IN ('new wave', 'newwave') THEN 'New Wave'
            WHEN LOWER(genre) IN ('post rock', 'post-rock', 'postrock') THEN 'Post-Rock'
            WHEN LOWER(genre) IN ('post punk', 'post-punk', 'postpunk') THEN 'Post-Punk'
            WHEN LOWER(genre) IN ('shoegaze', 'shoe gaze') THEN 'Shoegaze'
            WHEN LOWER(genre) IN ('grunge', 'grung') THEN 'Grunge'
            WHEN LOWER(genre) IN ('emo', 'emotional') THEN 'Emo'
            WHEN LOWER(genre) IN ('screamo', 'scream') THEN 'Screamo'
            WHEN LOWER(genre) IN ('metalcore', 'metal core') THEN 'Metalcore'
            WHEN LOWER(genre) IN ('deathcore', 'death core') THEN 'Deathcore'
            WHEN LOWER(genre) IN ('black metal', 'blackmetal') THEN 'Black Metal'
            WHEN LOWER(genre) IN ('death metal', 'deathmetal') THEN 'Death Metal'
            WHEN LOWER(genre) IN ('power metal', 'powermetal') THEN 'Power Metal'
            WHEN LOWER(genre) IN ('heavy metal', 'heavymetal') THEN 'Heavy Metal'
            WHEN LOWER(genre) IN ('thrash metal', 'thrashmetal', 'thrash') THEN 'Thrash Metal'
            WHEN LOWER(genre) IN ('speed metal', 'speedmetal') THEN 'Speed Metal'
            WHEN LOWER(genre) IN ('doom metal', 'doommetal', 'doom') THEN 'Doom Metal'
            WHEN LOWER(genre) IN ('sludge metal', 'sludgemetal', 'sludge') THEN 'Sludge Metal'
            WHEN LOWER(genre) IN ('stoner metal', 'stonermetal', 'stoner') THEN 'Stoner Metal'
            WHEN LOWER(genre) IN ('nu metal', 'numetal', 'nu-metal') THEN 'Nu Metal'
            -- Default: Use proper title case for other genres
            ELSE INITCAP(LOWER(genre))
        END as normalized_genre,
        artist_diversity,
        popularity_score
    FROM {{ source('analytics', 'genre_trends') }}
    WHERE genre IS NOT NULL
        AND TRIM(genre) != ''  -- Filter out empty genres
)
SELECT
    normalized_genre as genre,
    SUM(artist_diversity) as artist_diversity,  -- Sum values for same genre
    SUM(popularity_score) as popularity_score   -- Sum popularity scores
FROM normalized_genre_data
WHERE normalized_genre IS NOT NULL
GROUP BY normalized_genre  -- Group by normalized genre
ORDER BY SUM(artist_diversity) DESC NULLS LAST, SUM(popularity_score) DESC
