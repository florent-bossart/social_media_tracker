-- =============================================
-- Supabase Complete DDL - Tables and Views
-- This file contains table definitions and view definitions for Supabase
-- Based on the actual schema from the local PostgreSQL database
-- =============================================

-- Create schemas
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS intermediate;

-- =============================================
-- CORE ANALYTICS TABLES
-- =============================================

-- Table: analytics.int_extracted_artists
CREATE TABLE analytics.int_extracted_artists (
    original_text text,
    source_platform character varying,
    artist_name_lower text,
    artist_name text,
    has_genre integer,
    confidence_score double precision,
    overall_sentiment character varying,
    sentiment_strength double precision
);

-- Table: analytics.entity_extraction
CREATE TABLE analytics.entity_extraction (
    id integer NOT NULL,
    source_platform character varying,
    original_text text,
    extraction_date date,
    source_date timestamp without time zone,
    confidence_score double precision,
    entities_artists jsonb,
    entities_artists_count integer,
    entities_songs jsonb,
    entities_songs_count integer,
    entities_genres jsonb,
    entities_genres_count integer,
    entities_song_indicators jsonb,
    entities_song_indicators_count integer,
    entities_sentiment_indicators jsonb,
    entities_sentiment_indicators_count integer,
    entities_music_events jsonb,
    entities_music_events_count integer,
    entities_temporal_references jsonb,
    entities_temporal_references_count integer,
    entities_other_entities jsonb,
    entities_other_entities_count integer
);

-- Create sequence for entity_extraction
CREATE SEQUENCE analytics.entity_extraction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.entity_extraction_id_seq OWNED BY analytics.entity_extraction.id;
ALTER TABLE ONLY analytics.entity_extraction ALTER COLUMN id SET DEFAULT nextval('analytics.entity_extraction_id_seq'::regclass);
ALTER TABLE ONLY analytics.entity_extraction ADD CONSTRAINT entity_extraction_pkey PRIMARY KEY (id);

-- Table: analytics.sentiment_analysis
CREATE TABLE analytics.sentiment_analysis (
    id integer NOT NULL,
    source_platform character varying,
    original_text text,
    analysis_date date,
    overall_sentiment character varying,
    sentiment_strength double precision,
    confidence_score double precision,
    sentiment_reasoning text,
    artist_sentiment jsonb,
    music_quality_sentiment character varying,
    performance_sentiment character varying,
    personal_experience_sentiment character varying,
    emotional_indicators jsonb,
    emotional_indicators_count integer,
    has_comparison boolean,
    comparison_type character varying,
    favorable_entities jsonb,
    unfavorable_entities jsonb,
    comparison_sentiment character varying
);

-- Create sequence for sentiment_analysis
CREATE SEQUENCE analytics.sentiment_analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.sentiment_analysis_id_seq OWNED BY analytics.sentiment_analysis.id;
ALTER TABLE ONLY analytics.sentiment_analysis ALTER COLUMN id SET DEFAULT nextval('analytics.sentiment_analysis_id_seq'::regclass);
ALTER TABLE ONLY analytics.sentiment_analysis ADD CONSTRAINT sentiment_analysis_pkey PRIMARY KEY (id);

-- Table: analytics.artist_trends
CREATE TABLE analytics.artist_trends (
    id integer NOT NULL,
    entity_type character varying,
    entity_name character varying,
    mention_count integer,
    sentiment_score double precision,
    sentiment_consistency double precision,
    growth_rate double precision,
    engagement_level character varying,
    trend_strength double precision,
    trend_direction character varying,
    first_seen date,
    last_seen date,
    platforms jsonb,
    peak_sentiment double precision,
    sentiment_volatility double precision
);

-- Create sequence for artist_trends
CREATE SEQUENCE analytics.artist_trends_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.artist_trends_id_seq OWNED BY analytics.artist_trends.id;
ALTER TABLE ONLY analytics.artist_trends ALTER COLUMN id SET DEFAULT nextval('analytics.artist_trends_id_seq'::regclass);
ALTER TABLE ONLY analytics.artist_trends ADD CONSTRAINT artist_trends_pkey PRIMARY KEY (id);

-- Table: analytics.genre_trends
CREATE TABLE analytics.genre_trends (
    id integer NOT NULL,
    genre character varying,
    popularity_score double precision,
    sentiment_trend character varying,
    artist_diversity integer,
    cross_platform_presence integer,
    emotional_associations jsonb,
    trend_momentum double precision
);

-- Create sequence for genre_trends
CREATE SEQUENCE analytics.genre_trends_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.genre_trends_id_seq OWNED BY analytics.genre_trends.id;
ALTER TABLE ONLY analytics.genre_trends ALTER COLUMN id SET DEFAULT nextval('analytics.genre_trends_id_seq'::regclass);
ALTER TABLE ONLY analytics.genre_trends ADD CONSTRAINT genre_trends_pkey PRIMARY KEY (id);

-- Table: analytics.temporal_trends
CREATE TABLE analytics.temporal_trends (
    id integer NOT NULL,
    time_period character varying,
    dominant_artists jsonb,
    dominant_genres jsonb,
    sentiment_shift double precision,
    engagement_pattern character varying,
    notable_events jsonb
);

-- Create sequence for temporal_trends
CREATE SEQUENCE analytics.temporal_trends_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.temporal_trends_id_seq OWNED BY analytics.temporal_trends.id;
ALTER TABLE ONLY analytics.temporal_trends ALTER COLUMN id SET DEFAULT nextval('analytics.temporal_trends_id_seq'::regclass);
ALTER TABLE ONLY analytics.temporal_trends ADD CONSTRAINT temporal_trends_pkey PRIMARY KEY (id);

-- Table: analytics.wordcloud_data
CREATE TABLE analytics.wordcloud_data (
    id integer NOT NULL,
    word character varying NOT NULL,
    frequency integer,
    source_platform character varying,
    generation_date date,
    source_file character varying
);

-- Create sequence for wordcloud_data
CREATE SEQUENCE analytics.wordcloud_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.wordcloud_data_id_seq OWNED BY analytics.wordcloud_data.id;
ALTER TABLE ONLY analytics.wordcloud_data ALTER COLUMN id SET DEFAULT nextval('analytics.wordcloud_data_id_seq'::regclass);
ALTER TABLE ONLY analytics.wordcloud_data ADD CONSTRAINT wordcloud_data_pkey PRIMARY KEY (id);

-- =============================================
-- INTERMEDIATE TABLES (for complex views)
-- =============================================

-- Table: intermediate.cleaned_youtube_comments
CREATE TABLE intermediate.cleaned_youtube_comments (
    video_id character varying,
    comment_id character varying,
    author_clean character varying,
    text_clean text,
    published_at timestamp without time zone,
    keyword_clean character varying
);

-- Table: intermediate.cleaned_youtube_videos
CREATE TABLE intermediate.cleaned_youtube_videos (
    video_id character varying,
    title_clean character varying,
    channel_title_clean character varying,
    view_count integer,
    like_count integer,
    comment_count integer,
    duration_seconds integer
);

-- Table: intermediate.cleaned_reddit_comments
CREATE TABLE intermediate.cleaned_reddit_comments (
    comment_id character varying,
    post_id character varying,
    author_clean character varying,
    body_clean text,
    body_urls text[],
    created_utc_fmt timestamp without time zone
);

-- Table: intermediate.cleaned_reddit_posts
CREATE TABLE intermediate.cleaned_reddit_posts (
    post_id character varying,
    title_clean character varying,
    author_clean character varying,
    source character varying,
    selftext_urls_array text[]
);

-- =============================================
-- ADDITIONAL TABLES (for dashboard compatibility)
-- =============================================

-- Table: analytics.insights_summary_overview
CREATE TABLE analytics.insights_summary_overview (
    id integer NOT NULL,
    analysis_timestamp timestamp without time zone,
    total_insights integer,
    key_artists text[],
    trending_genres text[],
    source_file character varying
);

-- Create sequence for insights_summary_overview
CREATE SEQUENCE analytics.insights_summary_overview_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.insights_summary_overview_id_seq OWNED BY analytics.insights_summary_overview.id;
ALTER TABLE ONLY analytics.insights_summary_overview ALTER COLUMN id SET DEFAULT nextval('analytics.insights_summary_overview_id_seq'::regclass);
ALTER TABLE ONLY analytics.insights_summary_overview ADD CONSTRAINT insights_summary_overview_pkey PRIMARY KEY (id);

-- Table: analytics.insights_summary_key_findings
CREATE TABLE analytics.insights_summary_key_findings (
    id integer NOT NULL,
    analysis_timestamp timestamp without time zone,
    finding_text text,
    confidence_score double precision,
    source_file character varying
);

-- Create sequence for insights_summary_key_findings
CREATE SEQUENCE analytics.insights_summary_key_findings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.insights_summary_key_findings_id_seq OWNED BY analytics.insights_summary_key_findings.id;
ALTER TABLE ONLY analytics.insights_summary_key_findings ALTER COLUMN id SET DEFAULT nextval('analytics.insights_summary_key_findings_id_seq'::regclass);
ALTER TABLE ONLY analytics.insights_summary_key_findings ADD CONSTRAINT insights_summary_key_findings_pkey PRIMARY KEY (id);

-- Table: analytics.insights_summary_artist_insights
CREATE TABLE analytics.insights_summary_artist_insights (
    id integer NOT NULL,
    analysis_timestamp timestamp without time zone,
    artist_name character varying,
    insight_text text,
    source_file character varying
);

-- Create sequence for insights_summary_artist_insights
CREATE SEQUENCE analytics.insights_summary_artist_insights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.insights_summary_artist_insights_id_seq OWNED BY analytics.insights_summary_artist_insights.id;
ALTER TABLE ONLY analytics.insights_summary_artist_insights ALTER COLUMN id SET DEFAULT nextval('analytics.insights_summary_artist_insights_id_seq'::regclass);
ALTER TABLE ONLY analytics.insights_summary_artist_insights ADD CONSTRAINT insights_summary_artist_insights_pkey PRIMARY KEY (id);

-- Table: analytics.trend_summary_overview
CREATE TABLE analytics.trend_summary_overview (
    id integer NOT NULL,
    analysis_date date,
    total_comments integer,
    unique_artists integer,
    avg_sentiment_score double precision,
    platforms_count integer,
    positive_comments integer,
    negative_comments integer,
    neutral_comments integer
);

-- Create sequence for trend_summary_overview
CREATE SEQUENCE analytics.trend_summary_overview_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.trend_summary_overview_id_seq OWNED BY analytics.trend_summary_overview.id;
ALTER TABLE ONLY analytics.trend_summary_overview ALTER COLUMN id SET DEFAULT nextval('analytics.trend_summary_overview_id_seq'::regclass);
ALTER TABLE ONLY analytics.trend_summary_overview ADD CONSTRAINT trend_summary_overview_pkey PRIMARY KEY (id);

-- Table: analytics.trend_summary_top_artists
CREATE TABLE analytics.trend_summary_top_artists (
    id integer NOT NULL,
    artist_name character varying,
    mention_count integer,
    sentiment_score double precision,
    sentiment_consistency double precision,
    growth_rate double precision,
    engagement_level character varying,
    trend_strength double precision,
    trend_direction character varying,
    platforms text[]
);

-- Create sequence for trend_summary_top_artists
CREATE SEQUENCE analytics.trend_summary_top_artists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.trend_summary_top_artists_id_seq OWNED BY analytics.trend_summary_top_artists.id;
ALTER TABLE ONLY analytics.trend_summary_top_artists ALTER COLUMN id SET DEFAULT nextval('analytics.trend_summary_top_artists_id_seq'::regclass);
ALTER TABLE ONLY analytics.trend_summary_top_artists ADD CONSTRAINT trend_summary_top_artists_pkey PRIMARY KEY (id);

-- Table: analytics.trend_summary_top_genres
CREATE TABLE analytics.trend_summary_top_genres (
    id integer NOT NULL,
    genre_name character varying,
    mention_count integer,
    avg_sentiment double precision,
    growth_rate double precision,
    artist_count integer,
    platforms text[],
    first_seen date,
    last_seen date
);

-- Create sequence for trend_summary_top_genres
CREATE SEQUENCE analytics.trend_summary_top_genres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.trend_summary_top_genres_id_seq OWNED BY analytics.trend_summary_top_genres.id;
ALTER TABLE ONLY analytics.trend_summary_top_genres ALTER COLUMN id SET DEFAULT nextval('analytics.trend_summary_top_genres_id_seq'::regclass);
ALTER TABLE ONLY analytics.trend_summary_top_genres ADD CONSTRAINT trend_summary_top_genres_pkey PRIMARY KEY (id);

-- Table: analytics.trend_summary_engagement_levels
CREATE TABLE analytics.trend_summary_engagement_levels (
    id integer NOT NULL,
    engagement_level character varying,
    artist_count integer,
    avg_sentiment double precision,
    avg_mentions integer,
    avg_trend_strength double precision
);

-- Create sequence for trend_summary_engagement_levels
CREATE SEQUENCE analytics.trend_summary_engagement_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.trend_summary_engagement_levels_id_seq OWNED BY analytics.trend_summary_engagement_levels.id;
ALTER TABLE ONLY analytics.trend_summary_engagement_levels ALTER COLUMN id SET DEFAULT nextval('analytics.trend_summary_engagement_levels_id_seq'::regclass);
ALTER TABLE ONLY analytics.trend_summary_engagement_levels ADD CONSTRAINT trend_summary_engagement_levels_pkey PRIMARY KEY (id);

-- Table: analytics.trend_summary_sentiment_patterns
CREATE TABLE analytics.trend_summary_sentiment_patterns (
    id integer NOT NULL,
    sentiment_category character varying,
    artist_count integer,
    avg_mentions integer,
    min_sentiment double precision,
    max_sentiment double precision,
    avg_sentiment double precision
);

-- Create sequence for trend_summary_sentiment_patterns
CREATE SEQUENCE analytics.trend_summary_sentiment_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE analytics.trend_summary_sentiment_patterns_id_seq OWNED BY analytics.trend_summary_sentiment_patterns.id;
ALTER TABLE ONLY analytics.trend_summary_sentiment_patterns ALTER COLUMN id SET DEFAULT nextval('analytics.trend_summary_sentiment_patterns_id_seq'::regclass);
ALTER TABLE ONLY analytics.trend_summary_sentiment_patterns ADD CONSTRAINT trend_summary_sentiment_patterns_pkey PRIMARY KEY (id);

-- =============================================
-- VIEWS
-- =============================================

-- Artist Sentiment Dashboard View
CREATE OR REPLACE VIEW analytics.artist_sentiment_dashboard AS
SELECT int_extracted_artists.artist_name,
    int_extracted_artists.overall_sentiment,
    avg(int_extracted_artists.sentiment_strength) AS avg_sentiment_score,
    CASE
        WHEN (int_extracted_artists.artist_name_lower = 'babymetal'::text) THEN ((((count(*))::numeric * 0.2))::integer)::bigint
        ELSE count(*)
    END AS mention_count
FROM analytics.int_extracted_artists
WHERE ((int_extracted_artists.overall_sentiment IS NOT NULL) AND (int_extracted_artists.artist_name_lower <> ALL (ARRAY['moa'::text, 'momo'::text, 'su-metal'::text, 'unknown'::text])) AND (length(int_extracted_artists.artist_name_lower) > 2))
GROUP BY int_extracted_artists.artist_name, int_extracted_artists.artist_name_lower, int_extracted_artists.overall_sentiment
HAVING (count(*) >= 3)
ORDER BY
    CASE
        WHEN (int_extracted_artists.artist_name_lower = 'babymetal'::text) THEN ((((count(*))::numeric * 0.2))::integer)::bigint
        ELSE count(*)
    END DESC;

-- Artist Trends Dashboard View
CREATE OR REPLACE VIEW analytics.artist_trends_dashboard AS
WITH artist_stats AS (
    SELECT int_extracted_artists.artist_name_lower,
        int_extracted_artists.artist_name,
        count(*) AS mention_count,
        avg(int_extracted_artists.confidence_score) AS avg_confidence,
        count(DISTINCT int_extracted_artists.source_platform) AS platform_count,
        avg(COALESCE(int_extracted_artists.sentiment_strength, (5.0)::double precision)) AS sentiment_score
    FROM analytics.int_extracted_artists
    GROUP BY int_extracted_artists.artist_name_lower, int_extracted_artists.artist_name
    HAVING (count(*) >= 3)
), filtered_artists AS (
    SELECT artist_stats.artist_name_lower,
        artist_stats.artist_name,
        artist_stats.mention_count,
        artist_stats.avg_confidence,
        artist_stats.platform_count,
        artist_stats.sentiment_score
    FROM artist_stats
    WHERE ((artist_stats.artist_name_lower <> ALL (ARRAY['moa'::text, 'momo'::text, 'su-metal'::text, 'unknown'::text])) AND (artist_stats.artist_name_lower !~~* 'hall of%'::text) AND (artist_stats.artist_name_lower !~~* '%playlist%'::text) AND (length(artist_stats.artist_name_lower) > 2))
)
SELECT filtered_artists.artist_name,
    CASE
        WHEN (filtered_artists.artist_name_lower = 'babymetal'::text) THEN ((((filtered_artists.mention_count)::numeric * 0.2))::integer)::bigint
        ELSE filtered_artists.mention_count
    END AS mention_count,
    filtered_artists.sentiment_score,
    filtered_artists.avg_confidence AS trend_strength,
    CASE
        WHEN (filtered_artists.sentiment_score >= (7)::double precision) THEN 'positive'::text
        WHEN (filtered_artists.sentiment_score <= (4)::double precision) THEN 'negative'::text
        ELSE 'neutral'::text
    END AS trend_direction,
    CASE
        WHEN (filtered_artists.mention_count >= 50) THEN 'high'::text
        WHEN (filtered_artists.mention_count >= 20) THEN 'medium'::text
        ELSE 'low'::text
    END AS engagement_level,
    filtered_artists.platform_count
FROM filtered_artists
ORDER BY
    CASE
        WHEN (filtered_artists.artist_name_lower = 'babymetal'::text) THEN ((((filtered_artists.mention_count)::numeric * 0.2))::integer)::bigint
        ELSE filtered_artists.mention_count
    END DESC;

-- Overall Stats Dashboard View
CREATE OR REPLACE VIEW analytics.overall_stats_dashboard AS
SELECT 
    (SELECT COUNT(*) FROM analytics.entity_extraction) AS total_extractions,
    (SELECT COUNT(*) FROM analytics.sentiment_analysis) AS total_sentiments,
    (SELECT COUNT(*) FROM analytics.artist_trends WHERE trend_direction = 'positive') AS trending_up_count,
    COALESCE((SELECT ROUND(AVG(sentiment_strength)::numeric, 2) FROM analytics.sentiment_analysis), 5.0) AS avg_sentiment,
    COALESCE((SELECT ROUND(AVG(confidence_score)::numeric, 2) FROM analytics.entity_extraction), 0.75) AS avg_confidence,
    (SELECT MAX(extraction_date) FROM analytics.entity_extraction) AS latest_analysis_date,
    CURRENT_DATE AS report_date;

-- Platform Data Dashboard View
CREATE OR REPLACE VIEW analytics.platform_data_dashboard AS
SELECT 
    source_platform,
    COUNT(*) AS total_posts,
    AVG(confidence_score) AS avg_confidence,
    MAX(extraction_date) AS last_updated
FROM analytics.entity_extraction
GROUP BY source_platform;

-- Genre Trends Dashboard View
CREATE OR REPLACE VIEW analytics.genre_trends_dashboard AS
SELECT 
    genre AS genre_name,
    COALESCE(SUM(popularity_score), 0) AS mention_count,
    COALESCE(AVG(CASE 
        WHEN sentiment_trend = 'positive' THEN 7.0
        WHEN sentiment_trend = 'negative' THEN 3.0
        ELSE 5.0
    END), 5.0) AS sentiment_score,
    COALESCE(AVG(trend_momentum), 0.5) AS trend_strength,
    COALESCE(AVG(popularity_score), 0) AS popularity_score
FROM analytics.genre_trends
WHERE genre IS NOT NULL
GROUP BY genre
ORDER BY COALESCE(SUM(popularity_score), 0) DESC;

-- Wordcloud Data Dashboard View
CREATE OR REPLACE VIEW analytics.wordcloud_data_dashboard AS
SELECT 
    word,
    frequency
FROM analytics.wordcloud_data
WHERE frequency >= 10
ORDER BY frequency DESC
LIMIT 500;

-- Temporal Data Dashboard View
CREATE OR REPLACE VIEW analytics.temporal_data_dashboard AS
SELECT
    time_period AS date,
    'combined' AS platform,
    COALESCE(jsonb_array_length(dominant_artists), 0) AS mention_count,
    sentiment_shift AS sentiment_shift,
    engagement_pattern,
    CASE
        WHEN ABS(COALESCE(sentiment_shift, 0) - 5.0) >= 2.0 THEN 0.8
        WHEN ABS(COALESCE(sentiment_shift, 0) - 5.0) >= 1.0 THEN 0.6
        WHEN ABS(COALESCE(sentiment_shift, 0) - 5.0) >= 0.5 THEN 0.4
        ELSE 0.2
    END AS trend_strength,
    COALESCE(jsonb_array_length(dominant_artists), 0) + COALESCE(jsonb_array_length(dominant_genres), 0) AS data_points,
    CURRENT_TIMESTAMP AS analysis_timestamp
FROM analytics.temporal_trends
ORDER BY id DESC;

-- Dashboard Summary View
CREATE OR REPLACE VIEW analytics.dashboard_summary AS
SELECT 
    CURRENT_DATE AS report_date,
    (SELECT COUNT(*) FROM analytics.entity_extraction) AS total_extractions,
    (SELECT COUNT(*) FROM analytics.sentiment_analysis) AS total_sentiments,
    (SELECT COUNT(*) FROM analytics.artist_trends WHERE trend_direction = 'positive') AS trending_up_count,
    (SELECT ROUND(AVG(sentiment_strength)::numeric, 2) FROM analytics.sentiment_analysis) AS avg_sentiment,
    (SELECT ROUND(AVG(confidence_score)::numeric, 2) FROM analytics.entity_extraction) AS avg_confidence,
    (SELECT MAX(extraction_date) FROM analytics.entity_extraction) AS latest_analysis_date;

-- Artists Without Genre Dashboard View
CREATE OR REPLACE VIEW analytics.artists_without_genre_dashboard AS
SELECT COUNT(DISTINCT artist_name_lower) AS artists_without_genre
FROM analytics.int_extracted_artists
WHERE COALESCE(has_genre, 0) = 0;

-- Daily Trends View
CREATE OR REPLACE VIEW analytics.daily_trends AS
SELECT 
    first_seen AS analysis_date,
    COUNT(DISTINCT entity_name) AS unique_entities,
    AVG(sentiment_score) AS avg_sentiment,
    AVG(trend_strength) AS avg_trend_strength,
    COUNT(CASE WHEN trend_direction = 'positive' THEN 1 END) AS trending_up,
    COUNT(CASE WHEN trend_direction = 'negative' THEN 1 END) AS trending_down,
    COUNT(CASE WHEN trend_direction = 'neutral' THEN 1 END) AS trending_neutral
FROM analytics.artist_trends
GROUP BY first_seen
ORDER BY first_seen DESC;

-- Genre Artist Diversity Dashboard View
CREATE OR REPLACE VIEW analytics.genre_artist_diversity_dashboard AS
WITH normalized_genre_data AS (
    SELECT
        CASE
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['pop'::text, 'j-pop'::text, 'jpop'::text, 'j pop'::text])) THEN 'J-Pop'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['rock'::text, 'j-rock'::text, 'jrock'::text, 'j rock'::text])) THEN 'J-Rock'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['metal'::text, 'j-metal'::text, 'jmetal'::text])) THEN 'Metal'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['hip hop'::text, 'hip-hop'::text, 'hiphop'::text, 'rap'::text])) THEN 'Hip-Hop'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['electronic'::text, 'electro'::text, 'edm'::text])) THEN 'Electronic'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['indie'::text, 'independent'::text])) THEN 'Indie'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['alternative'::text, 'alt'::text])) THEN 'Alternative'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['punk'::text, 'j-punk'::text, 'jpunk'::text])) THEN 'Punk'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['folk'::text, 'j-folk'::text, 'jfolk'::text])) THEN 'Folk'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['jazz'::text, 'j-jazz'::text, 'jjazz'::text])) THEN 'Jazz'::text
            WHEN (lower((genre_trends.genre)::text) = ANY (ARRAY['classical'::text, 'classic'::text])) THEN 'Classical'::text
            ELSE initcap(lower((genre_trends.genre)::text))
        END AS normalized_genre,
        genre_trends.artist_diversity,
        genre_trends.popularity_score
    FROM analytics.genre_trends
    WHERE ((genre_trends.genre IS NOT NULL) AND (TRIM(BOTH FROM genre_trends.genre) <> ''::text))
)
SELECT normalized_genre_data.normalized_genre AS genre,
    sum(normalized_genre_data.artist_diversity) AS artist_diversity,
    sum(normalized_genre_data.popularity_score) AS popularity_score
FROM normalized_genre_data
WHERE (normalized_genre_data.normalized_genre IS NOT NULL)
GROUP BY normalized_genre_data.normalized_genre
ORDER BY (sum(normalized_genre_data.artist_diversity)) DESC NULLS LAST, (sum(normalized_genre_data.popularity_score)) DESC;

-- Trend Summary Views (for dashboard compatibility)
CREATE OR REPLACE VIEW analytics.trend_summary_artists_dashboard AS
SELECT 
    artist_name,
    mention_count,
    sentiment_score,
    sentiment_consistency,
    growth_rate,
    engagement_level,
    trend_strength,
    trend_direction,
    platforms
FROM analytics.trend_summary_top_artists
ORDER BY mention_count DESC;

CREATE OR REPLACE VIEW analytics.trend_summary_top_genres_normalized AS
SELECT 
    genre_name,
    mention_count,
    avg_sentiment,
    growth_rate,
    artist_count,
    platforms,
    first_seen,
    last_seen,
    CURRENT_TIMESTAMP AS analysis_timestamp
FROM analytics.trend_summary_top_genres
ORDER BY mention_count DESC;

-- Note: insights_summary tables are accessed directly by the dashboard
-- No views needed for: insights_summary_overview, insights_summary_key_findings, insights_summary_artist_insights

-- Artist Trends Enriched Dashboard (simplified version)
CREATE OR REPLACE VIEW analytics.artist_trends_enriched_dashboard AS
SELECT 
    artist_name,
    mention_count,
    0 AS youtube_mentions,
    0 AS reddit_mentions,
    0 AS unique_videos_mentioned,
    0 AS unique_channels,
    0 AS unique_posts_mentioned,
    0 AS unique_subreddits,
    0 AS mentions_with_urls,
    trend_strength,
    0.0 AS avg_video_views,
    50.0 AS youtube_percentage,
    50.0 AS reddit_percentage
FROM analytics.trend_summary_top_artists
ORDER BY mention_count DESC;

-- Video Context Dashboard View
CREATE OR REPLACE VIEW analytics.video_context_dashboard AS
WITH video_artist_mentions AS (
    SELECT cyv.video_id,
        cyv.title_clean AS video_title,
        cyv.channel_title_clean,
        cyv.published_at AS video_published_at,
        cyv.view_count,
        cyv.like_count,
        cyv.comment_count AS total_comments,
        cyv.duration_seconds,
        cyv.keyword_clean,
        cyv.fetch_date,
        TRIM(BOTH FROM artist_element.value) AS artist_name,
        TRIM(BOTH FROM genre_element.value) AS genre_name,
        ee.confidence_score,
        ee.extraction_date,
        cyc.comment_id,
        cyc.author_clean AS comment_author,
        cyc.published_at AS comment_published_at,
        ee.original_text AS comment_text
    FROM analytics.entity_extraction ee
        JOIN intermediate.cleaned_youtube_comments cyc ON ee.original_text = cyc.text_clean
        JOIN intermediate.cleaned_youtube_videos cyv ON cyc.video_id = cyv.video_id
        CROSS JOIN LATERAL jsonb_array_elements_text(ee.entities_artists) artist_element(value)
        CROSS JOIN LATERAL jsonb_array_elements_text(ee.entities_genres) genre_element(value)
    WHERE ee.source_platform::text = 'youtube'::text 
        AND ee.entities_artists IS NOT NULL 
        AND jsonb_array_length(ee.entities_artists) > 0 
        AND TRIM(BOTH FROM artist_element.value) <> ''::text 
        AND TRIM(BOTH FROM artist_element.value) IS NOT NULL 
        AND (lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) <> ALL (ARRAY['you'::text, 'they'::text, 'her'::text, 'him'::text, 'i'::text, 'we'::text, 'me'::text, 'us'::text, 'it'::text, 'he'::text, 'she'::text])) 
        AND (lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) <> ALL (ARRAY['none'::text, 'unknown'::text, 'null'::text, 'n/a'::text, 'na'::text, 'tbd'::text, 'tba'::text])) 
        AND (lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) <> ALL (ARRAY['this'::text, 'that'::text, 'yes'::text, 'no'::text, 'ok'::text, 'okay'::text, 'well'::text, 'so'::text, 'but'::text, 'and'::text, 'or'::text, 'moa'::text, 'lol'::text, 'wow'::text, 'omg'::text, 'wtf'::text, 'tbh'::text, 'imo'::text, 'imho'::text, 'tv'::text, 'cd'::text, 'dj'::text, 'mc'::text, 'mr'::text, 'ms'::text, 'dr'::text, 'the'::text, 'a'::text, 'an'::text, 'in'::text, 'on'::text, 'at'::text, 'by'::text, 'for'::text, 'with'::text, 'to'::text, 'of'::text, 'from'::text])) 
        AND lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) !~ '^[0-9a-e]$'::text 
        AND (length(lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value)))) >= 2 OR (lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) = ANY (ARRAY['iu'::text, 'cl'::text, 'xg'::text, 'su'::text, 'ai'::text, 'gd'::text, 'bm'::text]))) 
        AND lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) !~~ '%http%'::text 
        AND lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) !~~ '%www.%'::text 
        AND lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) !~~ '%.com%'::text 
        AND lower(TRIM(BOTH FROM TRIM(BOTH FROM artist_element.value))) !~ '^[0-9]+$'::text
), video_metrics AS (
    SELECT video_artist_mentions.video_id,
        video_artist_mentions.video_title,
        video_artist_mentions.channel_title_clean,
        video_artist_mentions.video_published_at,
        video_artist_mentions.view_count,
        video_artist_mentions.like_count,
        video_artist_mentions.total_comments,
        video_artist_mentions.duration_seconds,
        video_artist_mentions.keyword_clean,
        count(DISTINCT video_artist_mentions.artist_name) AS unique_artists_mentioned,
        count(DISTINCT video_artist_mentions.genre_name) AS unique_genres_mentioned,
        count(*) AS total_artist_mentions,
        count(DISTINCT video_artist_mentions.comment_author) AS unique_commenters,
        avg(video_artist_mentions.confidence_score) AS avg_confidence,
        array_agg(DISTINCT video_artist_mentions.artist_name ORDER BY video_artist_mentions.artist_name) FILTER (WHERE video_artist_mentions.artist_name IS NOT NULL) AS artists_mentioned,
        array_agg(DISTINCT video_artist_mentions.genre_name ORDER BY video_artist_mentions.genre_name) FILTER (WHERE video_artist_mentions.genre_name IS NOT NULL) AS genres_mentioned,
        round((count(*)::double precision / NULLIF(video_artist_mentions.total_comments, 0)::double precision * 100::double precision)::numeric, 2) AS artist_mention_percentage,
        min(video_artist_mentions.comment_published_at) AS first_artist_mention,
        max(video_artist_mentions.comment_published_at) AS latest_artist_mention
    FROM video_artist_mentions
    GROUP BY video_artist_mentions.video_id, video_artist_mentions.video_title, video_artist_mentions.channel_title_clean, video_artist_mentions.video_published_at, video_artist_mentions.view_count, video_artist_mentions.like_count, video_artist_mentions.total_comments, video_artist_mentions.duration_seconds, video_artist_mentions.keyword_clean
)
SELECT video_metrics.video_id,
    video_metrics.video_title,
    'https://www.youtube.com/watch?v='::text || video_metrics.video_id AS video_url,
    video_metrics.channel_title_clean,
    video_metrics.video_published_at,
    video_metrics.view_count,
    video_metrics.like_count,
    video_metrics.total_comments,
    round(video_metrics.duration_seconds::numeric / 60.0, 1) AS duration_minutes,
    video_metrics.keyword_clean,
    video_metrics.unique_artists_mentioned,
    video_metrics.unique_genres_mentioned,
    video_metrics.total_artist_mentions,
    video_metrics.unique_commenters,
    video_metrics.avg_confidence,
    video_metrics.artist_mention_percentage,
    video_metrics.artists_mentioned,
    video_metrics.genres_mentioned,
    video_metrics.first_artist_mention,
    video_metrics.latest_artist_mention,
    CASE
        WHEN video_metrics.artist_mention_percentage >= 10::numeric THEN 'High'::text
        WHEN video_metrics.artist_mention_percentage >= 5::numeric THEN 'Medium'::text
        ELSE 'Low'::text
    END AS artist_engagement_level,
    CASE
        WHEN video_metrics.keyword_clean ~~* '%music%'::text OR video_metrics.video_title ~~* '%music%'::text OR video_metrics.video_title ~~* '%song%'::text OR video_metrics.video_title ~~* '%album%'::text OR video_metrics.video_title ~~* '%mv%'::text OR video_metrics.video_title ~~* '%official%'::text THEN true
        ELSE false
    END AS is_music_content,
    CASE
        WHEN video_metrics.video_published_at >= (CURRENT_DATE - '30 days'::interval) THEN 'Recent'::text
        WHEN video_metrics.video_published_at >= (CURRENT_DATE - '90 days'::interval) THEN 'Moderate'::text
        ELSE 'Older'::text
    END AS video_age_category
FROM video_metrics
WHERE video_metrics.unique_artists_mentioned >= 1
ORDER BY video_metrics.total_artist_mentions DESC, video_metrics.avg_confidence DESC, video_metrics.view_count DESC;

-- Genre Artists Dashboard View (missing from previous schema)
CREATE OR REPLACE VIEW analytics.genre_artists_dashboard AS
SELECT 
    genre AS genre_name,
    artist_diversity AS unique_artists,
    popularity_score,
    sentiment_trend,
    cross_platform_presence,
    trend_momentum
FROM analytics.genre_trends
WHERE genre IS NOT NULL
ORDER BY artist_diversity DESC, popularity_score DESC;

-- Insights Summary Artist Insights Dashboard View (expected by dashboard)
CREATE OR REPLACE VIEW analytics.insights_summary_artist_insights_dashboard AS
SELECT 
    id,
    analysis_timestamp,
    artist_name,
    insight_text,
    source_file,
    CURRENT_TIMESTAMP AS last_updated
FROM analytics.insights_summary_artist_insights
ORDER BY analysis_timestamp DESC;

-- URL Analysis Dashboard View (placeholder - simplified)
CREATE OR REPLACE VIEW analytics.url_analysis_dashboard AS
SELECT 
    'youtube' AS platform,
    COUNT(*) AS total_urls,
    COUNT(DISTINCT cyc.video_id) AS unique_videos,
    AVG(cyv.view_count) AS avg_views,
    AVG(cyv.like_count) AS avg_likes,
    MAX(cyc.published_at) AS latest_comment_date
FROM intermediate.cleaned_youtube_comments cyc
JOIN intermediate.cleaned_youtube_videos cyv ON cyc.video_id = cyv.video_id
UNION ALL
SELECT 
    'reddit' AS platform,
    COUNT(*) AS total_urls,
    COUNT(DISTINCT crp.post_id) AS unique_posts,
    0 AS avg_views,
    0 AS avg_likes,
    MAX(crc.created_utc_fmt) AS latest_comment_date
FROM intermediate.cleaned_reddit_comments crc
JOIN intermediate.cleaned_reddit_posts crp ON crc.post_id = crp.post_id;

-- Author Influence Dashboard View (placeholder - simplified)
CREATE OR REPLACE VIEW analytics.author_influence_dashboard AS
WITH author_stats AS (
    SELECT 
        author_clean AS author_name,
        'youtube' AS platform,
        COUNT(*) AS total_comments,
        COUNT(DISTINCT video_id) AS unique_content,
        MIN(published_at) AS first_activity,
        MAX(published_at) AS latest_activity
    FROM intermediate.cleaned_youtube_comments
    WHERE author_clean IS NOT NULL
    GROUP BY author_clean
    UNION ALL
    SELECT 
        author_clean AS author_name,
        'reddit' AS platform,
        COUNT(*) AS total_comments,
        COUNT(DISTINCT post_id) AS unique_content,
        MIN(created_utc_fmt) AS first_activity,
        MAX(created_utc_fmt) AS latest_activity
    FROM intermediate.cleaned_reddit_comments
    WHERE author_clean IS NOT NULL
    GROUP BY author_clean
)
SELECT 
    author_name,
    platform,
    total_comments,
    unique_content,
    first_activity,
    latest_activity,
    CASE 
        WHEN total_comments >= 100 THEN 'High'
        WHEN total_comments >= 50 THEN 'Medium'
        ELSE 'Low'
    END AS influence_level,
    EXTRACT(DAYS FROM (latest_activity - first_activity)) AS activity_span_days
FROM author_stats
WHERE total_comments >= 5
ORDER BY total_comments DESC;

-- =============================================
-- COMPLETION MESSAGE
-- =============================================

DO $$
BEGIN
    RAISE NOTICE 'Supabase Schema Setup Completed Successfully!';
    RAISE NOTICE '=========================================';
    RAISE NOTICE 'Created schemas: analytics, intermediate';
    RAISE NOTICE 'Created tables: 16 analytics tables, 4 intermediate tables';
    RAISE NOTICE 'Created views: 16 dashboard views (all required views)';
    RAISE NOTICE '';
    RAISE NOTICE 'Core Dashboard views:';
    RAISE NOTICE '- artist_sentiment_dashboard';
    RAISE NOTICE '- artist_trends_dashboard';
    RAISE NOTICE '- overall_stats_dashboard';
    RAISE NOTICE '- platform_data_dashboard';
    RAISE NOTICE '- genre_trends_dashboard';
    RAISE NOTICE '- wordcloud_data_dashboard';
    RAISE NOTICE '- temporal_data_dashboard';
    RAISE NOTICE '- genre_artist_diversity_dashboard';
    RAISE NOTICE '';
    RAISE NOTICE 'Trend Summary views:';
    RAISE NOTICE '- trend_summary_artists_dashboard';
    RAISE NOTICE '- trend_summary_top_genres_normalized';
    RAISE NOTICE '';
    RAISE NOTICE 'Enhanced Dashboard views:';
    RAISE NOTICE '- artist_trends_enriched_dashboard';
    RAISE NOTICE '- video_context_dashboard';
    RAISE NOTICE '- genre_artists_dashboard';
    RAISE NOTICE '- insights_summary_artist_insights_dashboard';
    RAISE NOTICE '- url_analysis_dashboard';
    RAISE NOTICE '- author_influence_dashboard';
    RAISE NOTICE '';
    RAISE NOTICE 'Additional utility views:';
    RAISE NOTICE '- dashboard_summary';
    RAISE NOTICE '- artists_without_genre_dashboard';
    RAISE NOTICE '- daily_trends';
    RAISE NOTICE '';
    RAISE NOTICE 'Summary tables (accessed directly):';
    RAISE NOTICE '- insights_summary_overview';
    RAISE NOTICE '- insights_summary_key_findings';
    RAISE NOTICE '- insights_summary_artist_insights';
    RAISE NOTICE '- trend_summary_overview';
    RAISE NOTICE '- trend_summary_sentiment_patterns';
    RAISE NOTICE '- trend_summary_engagement_levels';
    RAISE NOTICE '';
    RAISE NOTICE 'To populate with data, use the backup restore scripts';
    RAISE NOTICE 'or run the ETL pipeline to generate fresh data.';
END $$;
