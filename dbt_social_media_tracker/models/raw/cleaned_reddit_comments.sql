{{ config(materialized='table',
 schema='intermediate',
 post_hook=[
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_post_id ON {{ this }} (post_id)",
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_comment_id ON {{ this }} (comment_id)"
    ]
 ) }}

WITH posts AS (
    SELECT
        post_id,
        post_url
    FROM {{ ref('cleaned_reddit_posts') }}
)

SELECT
    c.id AS comment_id,
    p.post_id,  -- assigned post ID
    LOWER(TRIM(c.author)) AS author_clean,
    LOWER(TRIM(c.body)) AS body_clean,
    REGEXP_MATCHES(c.body, '(https?:\/\/\S+)', 'g') AS body_urls,
    TO_CHAR(TO_TIMESTAMP(c.created_utc), 'YYYY-MM-DD HH24:MI:SS') AS created_utc_fmt,
    TO_CHAR(c.fetch_date, 'YYYY-MM-DD') AS fetch_date_fmt
FROM {{ source('raw', 'reddit_comments') }} c
LEFT JOIN posts p
    ON c.post_url = p.post_url
WHERE
  1=1
  AND c.body IS NOT NULL
  AND TRIM(c.body) != ''
  AND c.body NOT LIKE '%[deleted]%'
  AND c.body NOT LIKE '%[removed]%'
