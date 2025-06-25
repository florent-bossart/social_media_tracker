-- Intermediate model to extract and normalize artist data with improved filtering
{{ config(materialized='table') }}

WITH deduplicated_extractions AS (
    SELECT DISTINCT ON (ee.original_text, ee.source_platform)
        ee.original_text,
        ee.source_platform,
        ee.entities_artists,
        ee.entities_genres,
        ee.confidence_score,
        sa.overall_sentiment,
        sa.sentiment_strength
    FROM {{ source('analytics', 'entity_extraction') }} ee
    LEFT JOIN {{ source('analytics', 'sentiment_analysis') }} sa
        ON ee.original_text = sa.original_text
    WHERE ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
),
extracted_artists AS (
    SELECT
        original_text,
        source_platform,
        LOWER(TRIM(jsonb_array_elements_text(entities_artists))) as artist_name_lower,
        CASE
            WHEN entities_genres IS NOT NULL
                AND jsonb_array_length(entities_genres) > 0
            THEN 1
            ELSE 0
        END as has_genre,
        confidence_score,
        overall_sentiment,
        sentiment_strength
    FROM deduplicated_extractions
),
-- Define exclusion lists
excluded_terms AS (
    SELECT unnest(ARRAY[
        -- Pronouns
        'you', 'they', 'her', 'him', 'i', 'we', 'me', 'us', 'it', 'he', 'she',
        -- Generic/Unknown indicators
        'none', 'unknown', 'null', 'n/a', 'na', 'tbd', 'tba',
        -- Common words that might be misidentified
        'this', 'that', 'yes', 'no', 'ok', 'okay', 'well', 'so', 'but', 'and', 'or',
        -- Numbers and single characters
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e',
        -- Known noise terms
        'moa', 'lol', 'wow', 'omg', 'wtf', 'tbh', 'imo', 'imho',
        -- Common misidentifications from previous analysis
        'tv', 'cd', 'dj', 'mc', 'mr', 'ms', 'dr',
        -- English articles and prepositions
        'the', 'a', 'an', 'in', 'on', 'at', 'by', 'for', 'with', 'to', 'of', 'from',
        -- Common contractions
        'don''t', 'can''t', 'won''t', 'isn''t', 'aren''t', 'wasn''t', 'weren''t'
    ]) as excluded_term
)
SELECT
    original_text,
    source_platform,
    artist_name_lower,
    INITCAP(artist_name_lower) as artist_name,
    has_genre,
    confidence_score,
    overall_sentiment,
    sentiment_strength
FROM extracted_artists
WHERE artist_name_lower != ''
    AND artist_name_lower IS NOT NULL
    -- Exclude terms from exclusion list
    AND artist_name_lower NOT IN (SELECT excluded_term FROM excluded_terms)
    -- Length-based filtering: exclude very short names (< 2 chars) unless they're known valid artists
    AND (
        LENGTH(artist_name_lower) >= 2
        OR artist_name_lower IN ('iu', 'cl', 'xg', 'su', 'ai', 'gd', 'bm')  -- Known valid short artist names
    )
    -- Additional pattern-based exclusions
    AND artist_name_lower NOT LIKE '%http%'  -- URLs
    AND artist_name_lower NOT LIKE '%www.%'  -- URLs
    AND artist_name_lower NOT LIKE '%.com%'  -- URLs
    AND artist_name_lower !~ '^[0-9]+$'      -- Pure numbers
