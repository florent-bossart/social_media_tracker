import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

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
    filename = f"{extraction_date}_{outfile}"
    output_path = os.path.join(output_dir, filename)
    print(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(result.fetchone())
        df = pd.read_sql(sql, conn)
    df.to_csv(output_path, index=False)
    print(f"Wrote {len(df)} rows to {output_path}")

if __name__ == "__main__":
    # Extract cleaned Reddit comments
    reddit_sql = """
    SELECT
        comment_id, post_id, author_clean, body_clean, created_utc_fmt, fetch_date_fmt
    FROM intermediate.cleaned_reddit_comments
    """
    extract_to_csv(reddit_sql, "reddit_comments_cleaned.csv")

    # Extract cleaned YouTube comments
    youtube_sql = """
    SELECT
        comment_pk, video_id, comment_id, text_clean, author_clean, published_at, keyword_clean, fetch_date
    FROM intermediate.cleaned_youtube_comments
    """
    extract_to_csv(youtube_sql, "youtube_comments_cleaned.csv")
