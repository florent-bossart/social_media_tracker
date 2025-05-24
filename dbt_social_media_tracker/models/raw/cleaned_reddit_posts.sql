{{ config(materialized='table',
schema='intermediate',
post_hook=[
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_post_id ON {{ this }} (post_id)",
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_post_url ON {{ this }} (post_url)"
    ]
)}}

SELECT
    id AS post_id,
    url AS post_url,
    LOWER(TRIM(title)) AS title_clean,
    LOWER(TRIM(author)) AS author_clean,
    selftext,
    REGEXP_REPLACE(
        LOWER(selftext),
        '(https?:\/\/\S+)|[^a-zA-Z0-9\s]',
        '',
        'g'
    ) AS selftext_clean,
    COALESCE(
        ARRAY(
            SELECT unnest(REGEXP_MATCHES(selftext, '(https?:\/\/\S+)', 'g'))
        ),
        ARRAY[NULL]::text[]
    ) AS selftext_urls_array,
    ARRAY_TO_STRING(
        COALESCE(
            ARRAY(
                SELECT unnest(REGEXP_MATCHES(selftext, '(https?:\/\/\S+)', 'g'))
            ),
            ARRAY[NULL]::text[]
        ),
        ','
    ) AS selftext_urls_csv,
    TO_CHAR(TO_TIMESTAMP(created_utc), 'YYYY-MM-DD HH24:MI:SS') AS created_utc_fmt,
    fetch_date
FROM
    {{ source('raw', 'reddit_posts') }}
