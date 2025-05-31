import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime
import csv

# Remove dotenv in Docker-based Airflow
# from dotenv import load_dotenv
# load_dotenv()

PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
# PG_HOST = 'localhost'   # for local test only
# PG_PORT = "5434"         # for local test only
PG_HOST = os.getenv("WAREHOUSE_HOST")
PG_PORT = os.getenv("WAREHOUSE_PORT", "5432")
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(DATABASE_URL)

def extract_to_csv(sql, outfile):
    extraction_date = datetime.now().strftime("%Y%m%d")
    output_dir = "data/intermediate"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{extraction_date}_full_{outfile}"
    output_path = os.path.join(output_dir, filename)
    print(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(result.fetchone())
        df = pd.read_sql(sql, conn)
    df.to_csv(output_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"Wrote {len(df)} rows to {output_path}")

if __name__ == "__main__":
    # Extract cleaned Reddit comments
    reddit_sql = """
     select
        -- post
        posts.post_id,
        posts.post_url,
        posts.title_clean as post_title,
        posts.author_clean as post_author,
        posts.selftext_clean as post_text,
        posts.selftext_urls_array as post_URLs,
        posts.created_utc_fmt as post_creation_date,
        posts.fetch_date as post_fetch_date,
        -- comments
        comments.comment_id,
        comments.post_id,
        comments.author_clean,
        comments.body_clean,
        comments.created_utc_fmt,
        comments.fetch_date_fmt
    FROM intermediate.cleaned_reddit_posts posts
    	left join intermediate.cleaned_reddit_comments comments
    		on posts.post_id=comments.post_id
    """
    extract_to_csv(reddit_sql, "reddit_comments_cleaned.csv")

    # Extract cleaned YouTube comments
    youtube_sql = """
      select
    --video
        videos.video_id,
        videos.video_pk,
        videos.title_clean as video_title,
        videos.channel_title_clean as channel_title,
        videos.published_at as video_published_at,
        videos.view_count as video_view_count,
        videos.like_count as video_like_count,
        videos.comment_count as video_comment_count,
        videos.duration_seconds as video_duration,
        videos.keyword_clean as video_search_keyword,
        videos.fetch_date as video_fetch_date,
    --comments
        comments.comment_pk,
        comments.comment_id,
        comments.text_clean as comment_text,
        comments.author_clean as comment_author,
        comments.published_at as comment_published_at,
        comments.keyword_clean as comment_search_keyword,
        comments.fetch_date as comment_fetch_date
    FROM intermediate.cleaned_youtube_videos videos
    	LEFT JOIN intermediate.cleaned_youtube_comments comments
    		on  videos.video_id = comments.video_id;
    """
    extract_to_csv(youtube_sql, "youtube_comments_cleaned.csv")
