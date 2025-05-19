-- reddit
CREATE INDEX IF NOT EXISTS idx_reddit_posts_url ON raw.reddit_posts (url);
CREATE INDEX IF NOT EXISTS idx_reddit_comments_post_url ON raw.reddit_comments (post_url);
-- Index on author for author-based queries
CREATE INDEX IF NOT EXISTS idx_reddit_posts_author ON raw.reddit_posts (author);

-- Index on created_utc for time-based filtering/sorting
CREATE INDEX IF NOT EXISTS idx_reddit_posts_created_utc ON raw.reddit_posts (created_utc);

-- Index on fetch_date for ingestion period filtering
CREATE INDEX IF NOT EXISTS idx_reddit_posts_fetch_date ON raw.reddit_posts (fetch_date);

-- If you often filter by title (rare, but possible for deduplication)
CREATE INDEX IF NOT EXISTS idx_reddit_posts_title ON raw.reddit_posts (title);


-- Index on author for author-based queries
CREATE INDEX IF NOT EXISTS idx_reddit_comments_author ON raw.reddit_comments (author);

-- Index on created_utc for time-based filtering/sorting
CREATE INDEX IF NOT EXISTS idx_reddit_comments_created_utc ON raw.reddit_comments (created_utc);

-- Index on fetch_date for ingestion period filtering
CREATE INDEX IF NOT EXISTS idx_reddit_comments_fetch_date ON raw.reddit_comments (fetch_date);

-- If you often filter by post_title (less common, but useful for QA/debugging)
CREATE INDEX IF NOT EXISTS idx_reddit_comments_post_title ON raw.reddit_comments (post_title);


-- youtube
CREATE INDEX IF NOT EXISTS idx_youtube_videos_video_id ON raw.youtube_videos (video_id);
CREATE INDEX IF NOT EXISTS idx_youtube_videos_fetch_date ON raw.youtube_videos (fetch_date);
CREATE INDEX IF NOT EXISTS idx_youtube_videos_keyword ON raw.youtube_videos (keyword);
CREATE INDEX IF NOT EXISTS idx_youtube_comments_video_id ON raw.youtube_comments (video_id);
CREATE INDEX IF NOT EXISTS idx_youtube_comments_comment_id ON raw.youtube_comments (comment_id);
CREATE INDEX IF NOT EXISTS idx_youtube_comments_author ON raw.youtube_comments (author);
CREATE INDEX IF NOT EXISTS idx_youtube_comments_fetch_date ON raw.youtube_comments (fetch_date);
CREATE INDEX IF NOT EXISTS idx_youtube_comments_keyword ON raw.youtube_comments (keyword);
