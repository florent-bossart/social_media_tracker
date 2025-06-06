-- models/aggregates/agg_subreddit_activity_daily.sql
-- This model aggregates Reddit post counts and sums of comments on posts
-- by subreddit and day.

WITH source_reddit_posts AS (
    -- Using 'cleaned_reddit_posts' as the source model for Reddit posts.
    SELECT
        post_id,
        source AS subreddit, -- Assuming 'source' is in cleaned_reddit_posts
        TO_CHAR(TO_TIMESTAMP(created_utc_fmt, 'YYYY-MM-DD HH24:MI:SS'), 'YYYYMMDD') AS post_creation_date_yyyymmdd
    FROM {{ ref('cleaned_reddit_posts') }}
),
post_comment_counts AS (
    -- Using 'int_post_comment_counts_daily' for daily comment counts per post.
    SELECT
        post_id,
        comment_creation_date_yyyymmdd,
        daily_comments_on_post
    FROM {{ ref('int_post_comment_counts_daily') }}
)
SELECT
    srp.subreddit,
    srp.post_creation_date_yyyymmdd AS activity_date_yyyymmdd, -- Date of activity (post or comment)
    COUNT(DISTINCT srp.post_id) AS total_posts,
    SUM(COALESCE(pcc.daily_comments_on_post, 0)) AS total_comments
FROM source_reddit_posts srp
LEFT JOIN post_comment_counts pcc ON srp.post_id = pcc.post_id AND srp.post_creation_date_yyyymmdd = pcc.comment_creation_date_yyyymmdd -- Aligning by date
GROUP BY
    srp.subreddit,
    srp.post_creation_date_yyyymmdd
ORDER BY
    activity_date_yyyymmdd DESC,
    srp.subreddit
