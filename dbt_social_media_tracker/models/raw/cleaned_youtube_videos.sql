{{ config(
    materialized='table',
    schema='intermediate',
    post_hook=[
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_video_id ON {{ this }} (video_id)",
      "CREATE INDEX IF NOT EXISTS idx_{{ this.name }}_fetch_date ON {{ this }} (fetch_date)"
    ]
) }}

SELECT distinct
    src.id AS video_pk,
    src.video_id,
    LOWER(TRIM(src.title)) AS title_clean,
    LOWER(TRIM(src.channel_title)) AS channel_title_clean,
    src.published_at,
    src.view_count,
    src.like_count,
    src.comment_count,
    src.duration_seconds,
    LOWER(TRIM(src.keyword)) AS keyword_clean,
    src.fetch_date
FROM
    {{ source('raw', 'youtube_videos') }} src
