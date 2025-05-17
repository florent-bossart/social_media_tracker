CREATE TABLE reddit_posts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    author TEXT,
    url TEXT,
    selftext TEXT,
    created_utc DOUBLE PRECISION,
    source TEXT,         -- subreddit
    fetch_date DATE,
    loaded_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE reddit_comments (
    id SERIAL PRIMARY KEY,
    post_title TEXT,
    post_url TEXT,
    author TEXT,
    body TEXT,
    created_utc DOUBLE PRECISION,
    source TEXT,         -- subreddit
    fetch_date DATE,
    loaded_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE youtube_videos (
    id SERIAL PRIMARY KEY,
    video_id TEXT,
    title TEXT,
    channel_title TEXT,
    published_at TIMESTAMPTZ,
    view_count INT,
    like_count INT,
    comment_count INT,
    duration_seconds INT,
    keyword TEXT,
    fetch_date DATE,
    loaded_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE youtube_comments (
    id SERIAL PRIMARY KEY,
    video_id TEXT,
    comment_id TEXT,
    text TEXT,
    author TEXT,
    published_at TIMESTAMPTZ,
    keyword TEXT,
    fetch_date DATE,
    loaded_at TIMESTAMPTZ DEFAULT now()
);
