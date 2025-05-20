{{ config(materialized='table',
schema='intermediate',
post_hook=[
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_post_id ON {{ this }} (post_id)",
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_url_canonical ON {{ this }} (url_canonical)"
    ]
)}}

SELECT
    id as post_id,
    LOWER(TRIM(url)) AS url_canonical,
    LOWER(TRIM(title)) AS title_clean,
    LOWER(TRIM(author)) AS author_clean,
    selftext,  -- keep original, with URLs
    -- Cleaned version for LLM/AI (removes URLs and special chars)
    REGEXP_REPLACE(
        LOWER(selftext),
        '(https?:\/\/\S+)|[^a-zA-Z0-9\s]',
        '',
        'g'
    ) AS selftext_clean,
    -- Extract URLs as array
    REGEXP_MATCHES(selftext, '(https?:\/\/\S+)', 'g') AS selftext_urls,
    -- (Optional) URLs as a comma-separated string
    ARRAY_TO_STRING(REGEXP_MATCHES(selftext, '(https?:\/\/\S+)', 'g'), ',') AS selftext_urls_csv,
    TO_CHAR(TO_TIMESTAMP(created_utc), 'YYYY-MM-DD HH24:MI:SS') AS created_utc_fmt,
    fetch_date
FROM
    {{ source('raw', 'reddit_posts') }}
