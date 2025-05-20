{{ config(
    materialized='table',
    schema='intermediate',
    post_hook=[
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_video_id ON {{ this }} (video_id)",
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_fetch_date ON {{ this }} (fetch_date)"
    ]
) }}

SELECT
    id AS video_pk,
    video_id,
    LOWER(TRIM(title)) AS title_clean,
    LOWER(TRIM(channel_title)) AS channel_title_clean,
    published_at,
    view_count,
    like_count,
    comment_count,
    duration_seconds,
    LOWER(TRIM(keyword)) AS keyword_clean,
    fetch_date
FROM
    {{ source('raw', 'youtube_videos') }}
