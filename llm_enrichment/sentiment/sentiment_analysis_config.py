"""
Configuration for Japanese Music Sentiment Analysis Module

This module contains configuration settings for sentiment analysis of Japanese music discussions
from social media platforms like YouTube and Reddit.
"""

# Ollama Configuration
OLLAMA_MODEL = "llama3:latest"  # Updated to match available model
OLLAMA_BASE_URL = "https://89ee-2400-4050-3243-1400-985a-ca78-1567-5b73.ngrok-free.app" # Changed to new ngrok URL for the second laptop
OLLAMA_TIMEOUT = 120  # seconds - increased for slower processing

# Sentiment Analysis Configuration
SENTIMENT_ANALYSIS_CONFIG = {
    "sentiment_categories": {
        "positive": [
            "love", "amazing", "best", "incredible", "fantastic", "awesome", "perfect",
            "brilliant", "beautiful", "great", "excellent", "outstanding", "wonderful",
            "favorite", "obsessed", "addicted", "masterpiece", "genius", "goat",
            "banger", "fire", "slaps", "hits different", "chef's kiss", "peak",
            "S-tier", "legendary", "iconic", "divine", "ethereal", "heavenly"
        ],
        "negative": [
            "hate", "terrible", "awful", "worst", "horrible", "trash", "garbage",
            "cringe", "annoying", "boring", "mid", "disappointing", "overrated",
            "bland", "stale", "repetitive", "uninspired", "lazy", "generic",
            "sellout", "commercial", "manufactured", "soulless", "pretentious",
            "tryhard", "wannabe", "copycat", "rip-off", "derivative"
        ],
        "neutral": [
            "okay", "alright", "decent", "fine", "average", "standard", "typical",
            "normal", "regular", "common", "usual", "ordinary", "conventional",
            "mainstream", "popular", "known", "recognized", "established",
            "traditional", "classic", "standard", "baseline", "reference"
        ]
    },

    "cultural_sentiment_indicators": {
        "japanese_positive": [
            "kawaii", "sugoi", "kakkoii", "tanoshii", "ureshii", "suki",
            "daisuki", "ichiban", "saiko", "yabai", "kimochi", "tanoshi"
        ],
        "japanese_negative": [
            "tsumaranai", "dame", "kirai", "iya", "mendokusai", "muzukashii",
            "samui", "kanashii", "kowai", "shinpai", "komaru"
        ]
    },

    "music_specific_sentiment": {
        "performance_positive": [
            "live", "concert", "tour", "stage presence", "vocals", "energy",
            "crowd", "atmosphere", "setlist", "encore", "acoustic", "unplugged"
        ],
        "performance_negative": [
            "lip sync", "auto-tune", "playback", "boring stage", "no energy",
            "poor sound", "bad mix", "technical issues", "short set"
        ],
        "production_positive": [
            "production quality", "mixing", "mastering", "arrangement", "composition",
            "instrumentation", "layered", "polished", "crisp", "clean"
        ],
        "production_negative": [
            "overproduced", "muddy", "compressed", "harsh", "thin", "flat",
            "cluttered", "messy", "amateur", "low quality"
        ]
    },

    "genre_sentiment_associations": {
        "j-pop": ["catchy", "mainstream", "commercial", "accessible", "polished"],
        "j-rock": ["energetic", "raw", "powerful", "emotional", "authentic"],
        "visual kei": ["dramatic", "theatrical", "artistic", "unique", "extravagant"],
        "city pop": ["nostalgic", "smooth", "sophisticated", "timeless", "groovy"],
        "vocaloid": ["innovative", "creative", "digital", "synthetic", "experimental"],
        "anime music": ["epic", "emotional", "nostalgic", "memorable", "uplifting"]
    },

    "artist_sentiment_context": {
        # Common sentiment patterns for specific artists
        "controversial_topics": [
            "industry plant", "sellout", "manufactured", "corporate", "marketing",
            "overrated", "underrated", "overhyped", "underappreciated"
        ],
        "authenticity_indicators": [
            "genuine", "real", "authentic", "original", "unique", "personal",
            "heartfelt", "sincere", "honest", "raw", "unfiltered"
        ]
    }
}

# Sentiment Analysis Prompts
SENTIMENT_ANALYSIS_PROMPTS = {
    "main_prompt": """
You are a sentiment analysis expert specializing in Japanese music discussions on social media.

Analyze the sentiment of this comment about Japanese music:
"{text}"

Consider:
1. Overall sentiment (positive, negative, neutral)
2. Sentiment strength (1-10 scale)
3. Specific aspects mentioned (artist, song, performance, etc.)
4. Cultural context and slang
5. Emotional intensity
6. Comparative statements

Respond ONLY with valid JSON in this exact format:
{{
    "overall_sentiment": "positive|negative|neutral",
    "sentiment_strength": 7,
    "confidence": 0.85,
    "sentiment_aspects": {{
        "artist_sentiment": "positive|negative|neutral|none",
        "music_quality_sentiment": "positive|negative|neutral|none",
        "performance_sentiment": "positive|negative|neutral|none",
        "personal_experience_sentiment": "positive|negative|neutral|none"
    }},
    "emotional_indicators": ["love", "excitement", "nostalgia"],
    "sentiment_reasoning": "Brief explanation of sentiment analysis"
}}
""",

    "comparative_sentiment_prompt": """
You are analyzing sentiment in comments that compare Japanese music artists or songs.

Text: "{text}"

Focus on:
1. Which entities are being compared favorably vs unfavorably
2. Relative sentiment between compared items
3. Preference indicators

Respond ONLY with valid JSON:
{{
    "comparison_type": "artist_vs_artist|song_vs_song|genre_vs_genre|era_vs_era",
    "favorable_entities": ["entity1", "entity2"],
    "unfavorable_entities": ["entity3"],
    "comparison_sentiment": "strong_preference|mild_preference|balanced|conflicted",
    "sentiment_reasoning": "Brief explanation"
}}
"""
}

# Processing Configuration
PROCESSING_CONFIG = {
    "batch_size": 10,
    "max_retries": 3,
    "retry_delay": 2,  # seconds
    "sentiment_threshold": 0.6,  # minimum confidence for including sentiment
    "enable_comparative_analysis": True,
    "enable_aspect_sentiment": True,
    "enable_cultural_context": True
}

# Output Configuration
OUTPUT_CONFIG = {
    "include_original_text": True,
    "include_confidence_scores": True,
    "include_reasoning": True,
    "include_aspect_breakdown": True,
    "postgres_compatible": True
}

# File paths
SENTIMENT_OUTPUT_DIR = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/sentiment_analysis"
SENTIMENT_LOG_FILE = "/home/florent.bossart/code/florent-bossart/social_media_tracker/logs/sentiment_analysis.log"
