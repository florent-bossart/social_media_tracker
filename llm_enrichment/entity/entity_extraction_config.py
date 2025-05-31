"""
Configuration for Japanese Music Entity Extraction
"""

class EntityExtractionConfig:
    OLLAMA_BASE_URL = "https://0631-2400-4050-3243-1400-be00-2b32-3d86-ec6.ngrok-free.app"  # Updated to ngrok URL
    OLLAMA_MODEL = "llama3:latest"  # Updated to llama3:latest for Windows Ollama

    KNOWN_ARTISTS = [
        # From your SUBREDDIT_KEYWORDS and general knowledge
        "YOASOBI", "Ado", "King Gnu", "Sakanaction", "Mrs. Green Apple",
        "Eve", "Fujii Kaze", "Daoko", "CreepyNuts", "BABYMETAL",
        "One Ok Rock", "Scandal", "Official HIGE Dandism", "Yorushika",
        "Aimer", "Yonezu Kenshi", "LiSA", "Perfume", "Asian Kung-Fu Generation",
        "RADWIMPS", "UVERworld", "Polkadot Stingray", "FLOW", "Supercell",
        "GLAY", "Luna Sea", "The Gazette", "Miwa", "Bump of Chicken",
        "Spitz", "Man with a Mission", "Wagakki Band", "Hana", "Chai"
    ]

    KNOWN_GENRES = [
        "J-Pop", "J-Rock", "City Pop", "Vocaloid", "Anime", "Visual Kei",
        "Japanese Hip-Hop", "Japanese Jazz", "Japanese Folk", "Japanese Metal",
        "Japanese Electronic", "Japanese Classical", "Japanese Ambient",
        "Japanese Experimental", "Japanese Indie", "Japanese Acoustic",
        "Japanese Instrumental", "Shibuya-kei", "Enka", "Kayokyoku"
    ]

    SONG_INDICATORS = [
        "new song", "latest song", "new release", "latest release", "debut song",
        "single", "album", "EP", "cover", "remix", "collaboration", "collab",
        "featuring", "feat", "music video", "MV", "live", "concert", "performance",
        "acoustic", "instrumental", "original", "theme song", "opening", "ending"
    ]

    SENTIMENT_INDICATORS = [
        # Positive
        "amazing", "incredible", "fantastic", "perfect", "beautiful", "stunning",
        "masterpiece", "brilliant", "excellent", "outstanding", "wonderful",
        "trending", "popular", "viral", "hit", "favorite", "love", "best",

        # Negative
        "disappointing", "boring", "terrible", "awful", "worst", "hate",
        "overrated", "underwhelming", "mediocre", "bad", "poor",

        # Neutral/Descriptive
        "different", "unique", "interesting", "nostalgic", "catchy", "emotional",
        "energetic", "calm", "powerful", "soft", "heavy", "light"
    ]

    MUSIC_EVENTS = [
        "music festival", "concert tour", "album release", "single release",
        "award show", "music awards", "live stream", "online concert",
        "fan meeting", "collaboration announcement"
    ]

    TEMPORAL_REFERENCES = [
        "last year", "this year", "next year", "recently", "upcoming", "newly",
        "classic", "old school", "throwback", "latest", "current", "future"
    ]

    # Input/Output Paths (can be overridden)
    INPUT_PATH_YOUTUBE = "data/intermediate/{date}_youtube_comments_cleaned.csv"
    INPUT_PATH_REDDIT = "data/intermediate/{date}_reddit_comments_cleaned.csv"
    OUTPUT_PATH_ENTITIES = "data/intermediate/entity_extraction/{date}_{platform}_entities.csv"
    OUTPUT_PATH_COMBINED = "data/intermediate/entity_extraction/{date}_combined_entities.csv"

    # Processing Parameters
    BATCH_SIZE = 50
    MAX_RETRIES = 3
    OLLAMA_REQUEST_DELAY = 0  # Reduced delay to 0
    CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence to consider an entity valid

    # Entity Extraction Prompt (using f-string for easy modification)
    ENTITY_EXTRACTION_PROMPT = """
    Extract musical entities from the following Japanese social media text.
    Focus on artists, songs, genres, and related terms.
    Provide the output in JSON format with the following keys:
    "artists", "songs", "genres", "song_indicators", "sentiment_indicators", "music_events", "temporal_references", "other_entities".
    Each key should have a list of strings as its value. If no entities are found for a key, use an empty list.
    The output MUST be a single, valid JSON object. Do not include any text, explanations, or comments before, after, or within the JSON object itself.

    Text: "{text}"
    """
    def __init__(self):
        pass # Keep as a class with attributes

# For direct execution or testing
if __name__ == "__main__":
    config = EntityExtractionConfig()
    print(f"Ollama URL: {config.OLLAMA_BASE_URL}")
    print(f"Known Artists: {len(config.KNOWN_ARTISTS)}")
    print(f"Prompt Example: {config.ENTITY_EXTRACTION_PROMPT[:100]}...")
