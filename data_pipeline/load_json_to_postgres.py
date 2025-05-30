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

def ensure_raw_schema(conn):
    conn.execute(sql_text("CREATE SCHEMA IF NOT EXISTS raw;"))
    conn.commit()

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
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()")),
    schema="raw"
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
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()")),
    schema="raw"
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
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()")),
    schema="raw"
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
    Column("loaded_at", PG_TIMESTAMP, server_default=sql_text("now()")),
    schema="raw"
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

def load_reddit_files_for_date(date_str, conn):
    """Load only for a specific date YYYY-MM-DD."""
    day_dir = Path("data/reddit") / date_str
    if not day_dir.is_dir():
        print(f"Reddit dir {day_dir} not found.")
        return
    fetch_date = date_str
    for file in day_dir.glob("*.json"):
        subreddit = parse_subreddit_from_filename(file.name)
        if not subreddit:
            continue
        with open(file, "r", encoding="utf-8") as f:
            posts = json.load(f)
            for post in posts:
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

def load_youtube_files_for_date(date_str, conn):
    """Load only for a specific date YYYY-MM-DD."""
    day_dir = Path("data/youtube") / date_str
    if not day_dir.is_dir():
        print(f"YouTube dir {day_dir} not found.")
        return
    fetch_date = date_str
    for file in day_dir.glob("*.json"):
        keyword = parse_keyword_from_filename(file.name)
        if not keyword:
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

def load_all_files_for_date(date_str, conn):
    load_reddit_files_for_date(date_str, conn)
    load_youtube_files_for_date(date_str, conn)


def load_youtube_comment_update_file(json_path, conn, keyword=None, fetch_date=None):
    """
    Load a new_comments_YYYY-MM-DD.json file from YouTube comment updates into the youtube_comments table.

    Args:
        json_path (str or Path): Path to the JSON file.
        conn: SQLAlchemy connection.
        keyword (str, optional): If provided, sets the 'keyword' column for all rows. Otherwise NULL.
        fetch_date (str, optional): If provided, sets the 'fetch_date' column for all rows (YYYY-MM-DD).
                                    Otherwise tries to parse from filename.
    """
    json_path = Path(json_path)
    # Try to infer fetch_date if not provided
    if fetch_date is None:
        import re
        m = re.search(r'(\d{4}-\d{2}-\d{2})', str(json_path))
        if m:
            fetch_date = m.group(1)
    # Keyword is not in file, so set to None or provide one explicitly

    with open(json_path, "r", encoding="utf-8") as f:
        comments = json.load(f)
        for com in comments:
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
    print(f"Loaded {len(comments)} new comments from {json_path}")


def load_all_youtube_comment_update_files(conn, folder="data/youtube/comment_updates"):
    """
    Loads all new_comments_*.json files in the comment_updates folder.
    """
    folder = Path(folder)
    comment_files = sorted(folder.glob("new_comments_*.json"))
    total_loaded = 0
    for f in comment_files:
        try:
            load_youtube_comment_update_file(f, conn)
            total_loaded += 1
        except Exception as e:
            print(f"Error loading {f}: {e}")
    print(f"Loaded {total_loaded} comment update files from {folder}")

def load_today_youtube_comment_update_file(conn, folder="data/youtube/comment_updates"):
    """
    Loads only today's new_comments_YYYY-MM-DD.json file.
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    file = Path(folder) / f"new_comments_{today}.json"
    if file.exists():
        load_youtube_comment_update_file(file, conn)
        print(f"Loaded today's comment update file: {file}")
    else:
        print(f"No comment update file found for today: {file}")

def get_engine():
    PG_USER = os.getenv("WAREHOUSE_USER")
    PG_PW = os.getenv("WAREHOUSE_PASSWORD")
    PG_HOST = os.getenv("WAREHOUSE_HOST")
    PG_PORT = os.getenv("WAREHOUSE_PORT", "5432")
    PG_DB = os.getenv("WAREHOUSE_DB")
    DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    return create_engine(DATABASE_URL)

if __name__ == "__main__":
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    with engine.begin() as conn:
        load_reddit_files_for_date(today_str, conn)
        load_youtube_files_for_date(today_str, conn)
        print("Today's files loaded.")
