{% macro filter_valid_artists(artist_name_column) %}
(
    {{ artist_name_column }} != ''
    AND {{ artist_name_column }} IS NOT NULL
    -- Exclude pronouns
    AND LOWER(TRIM({{ artist_name_column }})) NOT IN (
        'you', 'they', 'her', 'him', 'i', 'we', 'me', 'us', 'it', 'he', 'she'
    )
    -- Exclude generic/unknown indicators
    AND LOWER(TRIM({{ artist_name_column }})) NOT IN (
        'none', 'unknown', 'null', 'n/a', 'na', 'tbd', 'tba'
    )
    -- Exclude common misidentified words
    AND LOWER(TRIM({{ artist_name_column }})) NOT IN (
        'this', 'that', 'yes', 'no', 'ok', 'okay', 'well', 'so', 'but', 'and', 'or',
        'moa', 'lol', 'wow', 'omg', 'wtf', 'tbh', 'imo', 'imho',
        'tv', 'cd', 'dj', 'mc', 'mr', 'ms', 'dr',
        'the', 'a', 'an', 'in', 'on', 'at', 'by', 'for', 'with', 'to', 'of', 'from'
    )
    -- Exclude single characters and pure numbers
    AND LOWER(TRIM({{ artist_name_column }})) !~ '^[0-9a-e]$'
    -- Length-based filtering with known valid short artists
    AND (
        LENGTH(LOWER(TRIM({{ artist_name_column }}))) >= 2
        OR LOWER(TRIM({{ artist_name_column }})) IN ('iu', 'cl', 'xg', 'su', 'ai', 'gd', 'bm')
    )
    -- Exclude URLs and pure numbers
    AND LOWER(TRIM({{ artist_name_column }})) NOT LIKE '%http%'
    AND LOWER(TRIM({{ artist_name_column }})) NOT LIKE '%www.%'
    AND LOWER(TRIM({{ artist_name_column }})) NOT LIKE '%.com%'
    AND LOWER(TRIM({{ artist_name_column }})) !~ '^[0-9]+$'
)
{% endmacro %}
