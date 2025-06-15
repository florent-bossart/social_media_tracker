"""
Configuration file for the Social Media Tracker API
Contains keyword lists and configuration settings for Reddit and YouTube data fetching.
"""

# Subreddit keywords for Reddit API
# These subreddits are monitored for Japanese music content
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
    "Genm",
    "ChaiBand"
]

# Search keywords for YouTube API
# These terms are used to discover trending Japanese music content
SEARCH_KEYWORDS = [
    # Current Trends and New Releases
    "最新曲 日本",          # "Latest songs Japan" - General search for the latest Japanese music
    "新曲 Jpop",           # "New song Jpop" - Focuses on new releases in the Jpop genre
    "Japanese music 2025", # Searches for Japanese music, targeting trends and releases in 2025
    "Jpop new release",    # Searches for new Jpop releases specifically
    "Jpop トレンド",        # "Jpop trend" - Focuses on trending Jpop songs and artists
    "Japanese MV 2025",    # "Japanese Music Video 2025" - Targets music videos released in 2025
    "急上昇 音楽",          # "Trending music" - Searches for music currently trending on YouTube in Japan
    "音楽 2025 日本",       # "Music 2025 Japan" - Year-specific search
    
    # Genre-Specific Keywords
    "アニソン 新曲",        # "New anime songs" - Targets anime soundtracks, a major part of Japanese music culture
    "Vtuber 音楽",         # "Vtuber music" - Focuses on music by virtual YouTubers, a growing trend
    "日本 ロック 新曲",     # "Japanese rock new releases" - Explores the rock genre in Japan
    "インディーズ 音楽 日本", # "Japanese indie music" - Targets indie music to discover emerging artists and non-mainstream trends
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
    "アコースティック 日本", # "Japanese acoustic" - Acoustic music genre
    "インストゥルメンタル 日本", # "Japanese instrumental" - Instrumental music
    
    # Artist and Band Specific
    "和楽器バンド",          # "Wagakki Band" - Focuses on a specific band that combines traditional Japanese instruments with modern rock
    "日本 バンド 2025",     # "Japanese bands 2025" - Band-focused search
    "新人アーティスト",     # "New artists" - Emerging artists
    
    # Content Types and Formats
    "J-pop cover",         # Cover versions often have high engagement
    "カバー曲 日本",        # "Japanese cover songs" - Cover songs
    "オリジナル曲",        # "Original songs" - Original compositions
    "コラボ 音楽 日本",     # "Music collaboration Japan" - Collaborative works
    "リミックス 日本",      # "Japanese remix" - Remix versions
    "話題の曲",            # "Trending songs" - Popular/viral songs
    "MVランキング",        # "Music video ranking" - Popular music videos
]

# API Configuration
DEFAULT_MAX_RESULTS_PER_QUERY = 10  # Default number of results to fetch per search query
DEFAULT_FETCH_COMMENTS = True       # Whether to fetch comments by default
DEFAULT_QUOTA_LIMIT = 10000         # Daily quota limit for YouTube API

# Utility functions for keyword management
def get_subreddit_keywords():
    """Return the list of subreddit keywords for Reddit API."""
    return SUBREDDIT_KEYWORDS.copy()

def get_search_keywords():
    """Return the list of search keywords for YouTube API."""
    return SEARCH_KEYWORDS.copy()

def get_keyword_counts():
    """Return counts of configured keywords."""
    return {
        "subreddit_keywords": len(SUBREDDIT_KEYWORDS),
        "search_keywords": len(SEARCH_KEYWORDS),
        "total_keywords": len(SUBREDDIT_KEYWORDS) + len(SEARCH_KEYWORDS)
    }

def add_subreddit_keyword(keyword):
    """Add a new subreddit keyword if it doesn't already exist."""
    if keyword not in SUBREDDIT_KEYWORDS:
        SUBREDDIT_KEYWORDS.append(keyword)
        return True
    return False

def add_search_keyword(keyword):
    """Add a new search keyword if it doesn't already exist."""
    if keyword not in SEARCH_KEYWORDS:
        SEARCH_KEYWORDS.append(keyword)
        return True
    return False
