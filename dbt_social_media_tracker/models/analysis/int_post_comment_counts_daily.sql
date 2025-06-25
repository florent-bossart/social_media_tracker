-- models/intermediate/int_post_comment_counts_daily.sql
-- This model counts comments per post per day from cleaned_reddit_comments

SELECT
    post_id,
    TO_CHAR(TO_TIMESTAMP(created_utc_fmt, 'YYYY-MM-DD HH24:MI:SS'), 'YYYYMMDD') AS comment_creation_date_yyyymmdd,
    COUNT(comment_id) AS daily_comments_on_post
FROM
    {{ ref('cleaned_reddit_comments') }}
GROUP BY
    post_id,
    TO_CHAR(TO_TIMESTAMP(created_utc_fmt, 'YYYY-MM-DD HH24:MI:SS'), 'YYYYMMDD')
