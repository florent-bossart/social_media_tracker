{{ config(
    materialized='table',
    schema='intermediate',
    post_hook=[
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_video_id ON {{ this }} (video_id)",
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_comment_id ON {{ this }} (comment_id)"
    ]
) }}

SELECT
    id AS comment_pk,
    video_id,
    comment_id,
    LOWER(TRIM(text)) AS text_clean,
    LOWER(TRIM(author)) AS author_clean,
    published_at,
    LOWER(TRIM(keyword)) AS keyword_clean,
    fetch_date
FROM
    {{ source('raw', 'youtube_comments') }}
