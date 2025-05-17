import os
import json
import re
from pathlib import Path
from sqlalchemy import create_engine, Table, Column, Integer, Text, Date, TIMESTAMP, MetaData, Float, text as sql_text
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
PG_HOST = os.getenv("WAREHOUSE_HOST")
PG_PORT = os.getenv("WAREHOUSE_PORT", "5432")
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

reddit_posts = Table(
    "reddit_posts", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", Text),
    Column("author", Text),
    Column("url", Text),
    Column("selftext", Text),
    Column("created_utc", Float(precision=53)),
    Column("source", Text),
    Column("fetch_date", Date),
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()"))
)

reddit_comments = Table(
    "reddit_comments", metadata,
    Column("id", Integer, primary_key=True),
    Column("post_title", Text),
    Column("post_url", Text),
    Column("author", Text),
    Column("body", Text),
    Column("created_utc", Float(precision=53)),
    Column("source", Text),
    Column("fetch_date", Date),
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()"))
)

youtube_videos = Table(
    "youtube_videos", metadata,
    Column("id", Integer, primary_key=True),
    Column("video_id", Text),
    Column("title", Text),
    Column("channel_title", Text),
    Column("published_at", PG_TIMESTAMP),
    Column("view_count", Integer),
    Column("like_count", Integer),
    Column("comment_count", Integer),
    Column("duration_seconds", Integer),
    Column("keyword", Text),
    Column("fetch_date", Date),
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()"))
)

youtube_comments = Table(
    "youtube_comments", metadata,
    Column("id", Integer, primary_key=True),
    Column("video_id", Text),
    Column("comment_id", Text),
    Column("text", Text),
    Column("author", Text),
    Column("published_at", PG_TIMESTAMP),
    Column("keyword", Text),
    Column("fetch_date", Date),
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()"))
)

def parse_fetch_date_from_path(path):
    # Looks for yyyy-mm-dd in path
    m = re.search(r"\d{4}-\d{2}-\d{2}", str(path))
    if m:
        return m.group(0)
    return None

def parse_subreddit_from_filename(filename):
    # e.g. full_subredditname_date.json or daily_subredditname_date.json
    m = re.match(r"(full|daily)_(.+?)_\d{4}-\d{2}-\d{2}\.json", filename)
    if m:
        return m.group(2)
    return None

def parse_keyword_from_filename(filename):
    # e.g. videos_keyword.json or comments_keyword.json
    m = re.match(r"(videos|comments)_(.+)\.json", filename)
    if m:
        return m.group(2)
    return None

def load_reddit_files(base_dir, conn):
    for day_dir in Path(base_dir).iterdir():
        if not day_dir.is_dir():
            continue
        fetch_date = parse_fetch_date_from_path(day_dir)
        for file in day_dir.glob("*.json"):
            subreddit = parse_subreddit_from_filename(file.name)
            if not subreddit or not fetch_date:
                continue
            with open(file, "r", encoding="utf-8") as f:
                posts = json.load(f)
                for post in posts:
                    # Insert post
                    post_data = dict(
                        title=post.get("title"),
                        author=post.get("author"),
                        url=post.get("url"),
                        selftext=post.get("selftext"),
                        created_utc=post.get("created_utc"),
                        source=subreddit,
                        fetch_date=fetch_date
                    )
                    conn.execute(reddit_posts.insert().values(**post_data))
                    # Insert comments (flattened)
                    for c in post.get("comments", []):
                        comment_data = dict(
                            post_title=post.get("title"),
                            post_url=post.get("url"),
                            author=c.get("author"),
                            body=c.get("body"),
                            created_utc=c.get("created_utc"),
                            source=subreddit,
                            fetch_date=fetch_date
                        )
                        conn.execute(reddit_comments.insert().values(**comment_data))
            print(f"Loaded reddit file {file}")

def load_youtube_files(base_dir, conn):
    for day_dir in Path(base_dir).iterdir():
        if not day_dir.is_dir():
            continue
        fetch_date = parse_fetch_date_from_path(day_dir)
        for file in day_dir.glob("*.json"):
            keyword = parse_keyword_from_filename(file.name)
            if not keyword or not fetch_date:
                continue
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if file.name.startswith("videos_"):
                    for vid in data:
                        video_data = dict(
                            video_id=vid.get("video_id"),
                            title=vid.get("title"),
                            channel_title=vid.get("channel_title"),
                            published_at=vid.get("published_at"),
                            view_count=vid.get("view_count"),
                            like_count=vid.get("like_count"),
                            comment_count=vid.get("comment_count"),
                            duration_seconds=vid.get("duration_seconds"),
                            keyword=keyword,
                            fetch_date=fetch_date
                        )
                        conn.execute(youtube_videos.insert().values(**video_data))
                elif file.name.startswith("comments_"):
                    for com in data:
                        comment_data = dict(
                            video_id=com.get("video_id"),
                            comment_id=com.get("id"),
                            text=com.get("text"),
                            author=com.get("author"),
                            published_at=com.get("published_at"),
                            keyword=keyword,
                            fetch_date=fetch_date
                        )
                        conn.execute(youtube_comments.insert().values(**comment_data))
            print(f"Loaded youtube file {file}")


def load_all_files(conn):
    load_reddit_files("data/reddit", conn)
    load_youtube_files("data/youtube", conn)

if __name__ == "__main__":
    with engine.begin() as conn:
        load_reddit_files("data/reddit", conn)
        load_youtube_files("data/youtube", conn)
        print("All files loaded.")
