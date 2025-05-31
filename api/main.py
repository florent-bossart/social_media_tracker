from http.client import HTTPException
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .youtube import search_and_fetch_video_data, save_video_snapshot, save_comments_snapshot
from .youtube_quota import quota
from .reddit import fetch_reddit_posts_daily
from .reddit_init import fetch_reddit_posts_full
from .updates_youtube_comments_from_fetched import update_comments_from_fetched_rotating



import random
from datetime import datetime, timezone

app = FastAPI()
# Subreddit keywords for Reddit API (placeholder list; to be populated later)
SUBREDDIT_KEYWORDS = [
    # General Music Subreddits
    "Jpop",
    "JapaneseMusic",
    "Vocaloid",
    "CityPop",
    "Jrock",
    "AnimeThemes",

    # Band-Specific Subreddits
    "AsianKungFuGeneration",
    "Perfume",
    "BABYMETAL",
    "OneOkRock",
    "ScandalBand",
    "OfficialHIGE",
    "Yorushika",
    "Aimer",
    "YonezuKenshi",
    "LisaJpop",
    "KingGnu",
    "Sakanaction",
    "MrsGreenApple",
    "Ado",
    "AnoMusic",
    "ManWithAMission",
    "BumpOfChicken",
    "Spitz",
    "MONOGATARI",
    "RADWIMPS",
    "UVERworld",
    "PolkadotStingray",
    "FLOW",
    "Supercell",
    "LiSA",
    "GLAY",
    "LunaSea",
    "TheGazette",
    "Miwa",
    "YOASOBI",
    "Eve",
    "FujiiKaze",
    "Daoko",
    "CreepyNuts",
    "Hana",
    "Genm"
    "ChaiBand"
]

# Search keywords list for YouTube API
SEARCH_KEYWORDS = [
    "最新曲 日本",          # "Latest songs Japan" - General search for the latest Japanese music.
    "新曲 Jpop",           # "New song Jpop" - Focuses on new releases in the Jpop genre.
    "Japanese music 2025", # Searches for Japanese music, targeting trends and releases in 2025.
    "Jpop new release",    # Searches for new Jpop releases specifically.
    "Jpop トレンド",        # "Jpop trend" - Focuses on trending Jpop songs and artists.
    "Japanese MV 2025",    # "Japanese Music Video 2025" - Targets music videos released in 2025.
    "急上昇 音楽",          # "Trending music" - Searches for music currently trending on YouTube in Japan.
    "アニソン 新曲",        # "New anime songs" - Targets anime soundtracks, a major part of Japanese music culture.
    "Vtuber 音楽",         # "Vtuber music" - Focuses on music by virtual YouTubers, a growing trend.
    "日本 ロック 新曲",     # "Japanese rock new releases" - Explores the rock genre in Japan.
    "インディーズ 音楽 日本", # "Japanese indie music" - Targets indie music to discover emerging artists and non-mainstream trends.
    "和楽器バンド",          # "Wagakki Band" - Focuses on a specific band that combines traditional Japanese instruments with modern rock, helping discover similar fusion music.
    "ボカロ 新曲",          # "Vocaloid new songs" - New Vocaloid releases
    "J-Rock 2025",         # Japanese rock music for 2025
    "シティポップ",         # "City Pop" - Popular Japanese music genre
    "アイドル 音楽",        # "Idol music" - Japanese idol music
    "日本語ラップ",         # "Japanese rap" - Japanese hip-hop/rap music
    "エレクトロニカ 日本",   # "Japanese electronica" - Electronic music from Japan
    "フォーク 日本",        # "Japanese folk" - Japanese folk music
    "メタル 日本",          # "Japanese metal" - Japanese metal music
    "ジャズ 日本",          # "Japanese jazz" - Japanese jazz music
    "クラシック 日本",      # "Japanese classical" - Japanese classical music
    "アンビエント 日本",    # "Japanese ambient" - Japanese ambient music
    "実験音楽 日本",        # "Japanese experimental music" - Japanese experimental music
    # Additional high-value keywords for broader coverage
    "音楽 2025 日本",       # "Music 2025 Japan" - Year-specific search
    "J-pop cover",         # Cover versions often have high engagement
    "日本 バンド 2025",     # "Japanese bands 2025" - Band-focused search
    "アコースティック 日本", # "Japanese acoustic" - Acoustic music genre
    "インストゥルメンタル 日本", # "Japanese instrumental" - Instrumental music
    "コラボ 音楽 日本",     # "Music collaboration Japan" - Collaborative works
    "リミックス 日本",      # "Japanese remix" - Remix versions
    "カバー曲 日本",        # "Japanese cover songs" - Cover songs
    "オリジナル曲",        # "Original songs" - Original compositions
    "新人アーティスト",     # "New artists" - Emerging artists
    "話題の曲",            # "Trending songs" - Popular/viral songs
    "MVランキング",        # "Music video ranking" - Popular music videos
]


@app.get("/")
def read_root():
    return {"message": "Welcome to the Social Media Sentiment Tracker API"}


@app.get("/youtube")
def get_youtube_data():
    fetch_date = datetime.now(timezone.utc).date().isoformat()
    all_results = []

    for query in SEARCH_KEYWORDS:
        try:
            video_data, comments = search_and_fetch_video_data(query)
            save_video_snapshot(video_data, query, fetch_date)
            save_comments_snapshot(comments, query, fetch_date)  # Ensures comments are saved
            all_results.append({
                "query": query,
                "videos_fetched": len(video_data),
                "comments_fetched": len(comments),
                "quota_used": quota.used,
                "quota_remaining": quota.remaining()
            })
        except RuntimeError as e:
            all_results.append({"query": query, "error": str(e)})
            continue  # Continue to the next keyword if quota is insufficient

    return {
        "fetched_at": fetch_date,
        "results": all_results
    }

# Reddit API Route for Daily Fetch
@app.get("/reddit/daily")
def get_reddit_daily_data():
    fetch_date = datetime.now(timezone.utc).date().isoformat()
    all_results = []

    for subreddit in SUBREDDIT_KEYWORDS:
        try:
            posts = fetch_reddit_posts_daily(subreddit)
            all_results.append({
                "subreddit": subreddit,
                "posts_fetched": len(posts),
                "fetched_at": fetch_date
            })
        except Exception as e:
            all_results.append({"subreddit": subreddit, "error": str(e)})

    return {
        "fetched_at": fetch_date,
        "results": all_results
    }


# Reddit API Route for Initial Full Load
@app.get("/reddit/full")
def get_reddit_full_data():
    fetch_date = datetime.now(timezone.utc).date().isoformat()
    all_results = []

    for subreddit in SUBREDDIT_KEYWORDS:
        try:
            posts = fetch_reddit_posts_full(subreddit)
            all_results.append({
                "subreddit": subreddit,
                "posts_fetched": len(posts),
                "fetched_at": fetch_date
            })
        except Exception as e:
            all_results.append({"subreddit": subreddit, "error": str(e)})

    return {
        "fetched_at": fetch_date,
        "results": all_results
    }


@app.post("/update_youtube_comments_from_fetched_rotating")
def trigger_update_youtube_comments_from_fetched_rotating():
    return update_comments_from_fetched_rotating()
