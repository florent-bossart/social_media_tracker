#!/usr/bin/env python3
"""
Trend Detection Module for Japanese Music Social Media Analysis Pipeline

This module analyzes combined entity and sentiment data to identify music trends,
including artist popularity, genre movements, sentiment patterns, and temporal dynamics.

Author: GitHub Copilot Assistant
Date: 2025-01-07
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from collections import Counter, defaultdict
import re
from dataclasses import dataclass, asdict
import sys
import os

from .trend_detection_config import TrendDetectionConfig

@dataclass
class TrendMetrics:
    """Data class for storing trend metrics"""
    entity_type: str
    entity_name: str
    mention_count: int
    sentiment_score: float
    sentiment_consistency: float
    growth_rate: float
    engagement_level: str
    trend_strength: float
    trend_direction: str
    first_seen: str
    last_seen: str
    platforms: List[str]
    peak_sentiment: float
    sentiment_volatility: float

@dataclass
class GenreTrend:
    """Data class for genre-specific trends"""
    genre: str
    popularity_score: float
    sentiment_trend: str
    artist_diversity: int
    cross_platform_presence: int
    emotional_associations: List[str]
    trend_momentum: float

@dataclass
class TemporalTrend:
    """Data class for temporal trend analysis"""
    time_period: str
    dominant_artists: List[str]
    dominant_genres: List[str]
    sentiment_shift: float
    engagement_pattern: str
    notable_events: List[str]

class TrendDetector:
    """
    Analyzes combined entity and sentiment data to detect music trends
    """

    def __init__(self, config: Optional[TrendDetectionConfig] = None, ollama_host: Optional[str] = None):
        """Initialize the trend detector"""
        self.config = config or TrendDetectionConfig()
        # Although TrendDetector doesn't directly call Ollama in the provided snippet,
        # we add the ollama_host parameter for consistency and future use if it were to call an LLM.
        # If TrendDetector is not supposed to use Ollama, this parameter can be removed or ignored.
        # For now, we'll store it if provided, but it won't be used by the current methods.
        self.ollama_base_url = ollama_host # Store it, though not used by current methods
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load the combined entity-sentiment data"""
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data for trend analysis"""
        # Convert processing_date to datetime
        df['processing_date'] = pd.to_datetime(df['processing_date'])

        # Parse JSON arrays safely
        def safe_parse_json(text):
            if pd.isna(text) or text == '[]':
                return []
            try:
                return json.loads(text.replace("'", '"'))
            except:
                return []

        df['artists_found'] = df['artists_found'].apply(safe_parse_json)
        df['songs_found'] = df['songs_found'].apply(safe_parse_json)
        df['genres_found'] = df['genres_found'].apply(safe_parse_json)
        df['emotional_indicators'] = df['emotional_indicators'].apply(safe_parse_json)

        # Convert sentiment strength to numeric
        df['sentiment_strength'] = pd.to_numeric(df['sentiment_strength'], errors='coerce')
        df['sentiment_confidence'] = pd.to_numeric(df['sentiment_confidence'], errors='coerce')

        self.logger.info("Data preprocessing completed")
        return df

    def analyze_artist_trends(self, df: pd.DataFrame) -> List[TrendMetrics]:
        """Analyze trends for individual artists"""
        artist_trends = []

        # Flatten artist mentions
        artist_mentions = []
        for idx, row in df.iterrows():
            for artist in row['artists_found']:
                artist_mentions.append({
                    'artist': artist,
                    'date': row['processing_date'],
                    'platform': row['source_platform'],
                    'sentiment_strength': row['sentiment_strength'],
                    'sentiment_confidence': row['sentiment_confidence'],
                    'overall_sentiment': row['overall_sentiment'],
                    'artist_sentiment': row['artist_sentiment']
                })

        if not artist_mentions:
            self.logger.warning("No artist mentions found in data")
            return artist_trends

        artist_df = pd.DataFrame(artist_mentions)

        # Group by artist and calculate metrics
        for artist in artist_df['artist'].unique():
            artist_data = artist_df[artist_df['artist'] == artist]

            # Calculate trend metrics
            mention_count = len(artist_data)

            # Sentiment metrics
            sentiment_scores = artist_data['sentiment_strength'].dropna()
            avg_sentiment = sentiment_scores.mean() if len(sentiment_scores) > 0 else 5.0
            sentiment_consistency = 1.0 - (sentiment_scores.std() / 10.0) if len(sentiment_scores) > 1 else 1.0

            # Growth rate (simplified - based on mention distribution over time)
            dates = artist_data['date'].sort_values()
            if len(dates) > 1:
                time_span = (dates.iloc[-1] - dates.iloc[0]).days
                growth_rate = mention_count / max(time_span, 1)
            else:
                growth_rate = mention_count

            # Engagement level
            if mention_count >= 3:
                engagement_level = "high"
            elif mention_count >= 2:
                engagement_level = "medium"
            else:
                engagement_level = "low"

            # Trend strength (combines mentions, sentiment, and consistency)
            trend_strength = (
                min(mention_count / 5.0, 1.0) * 0.4 +
                (avg_sentiment / 10.0) * 0.3 +
                sentiment_consistency * 0.3
            )

            # Trend direction
            if avg_sentiment > 6.5:
                trend_direction = "positive"
            elif avg_sentiment < 4.5:
                trend_direction = "negative"
            else:
                trend_direction = "neutral"

            platforms = list(artist_data['platform'].unique())

            artist_trends.append(TrendMetrics(
                entity_type="artist",
                entity_name=artist,
                mention_count=mention_count,
                sentiment_score=avg_sentiment,
                sentiment_consistency=sentiment_consistency,
                growth_rate=growth_rate,
                engagement_level=engagement_level,
                trend_strength=trend_strength,
                trend_direction=trend_direction,
                first_seen=dates.iloc[0].strftime('%Y-%m-%d') if len(dates) > 0 else "",
                last_seen=dates.iloc[-1].strftime('%Y-%m-%d') if len(dates) > 0 else "",
                platforms=platforms,
                peak_sentiment=sentiment_scores.max() if len(sentiment_scores) > 0 else avg_sentiment,
                sentiment_volatility=sentiment_scores.std() if len(sentiment_scores) > 0 else 0.0
            ))

        # Sort by trend strength
        artist_trends.sort(key=lambda x: x.trend_strength, reverse=True)
        self.logger.info(f"Analyzed trends for {len(artist_trends)} artists")

        return artist_trends

    def analyze_genre_trends(self, df: pd.DataFrame) -> List[GenreTrend]:
        """Analyze trends for music genres"""
        genre_trends = []

        # Flatten genre mentions
        genre_mentions = []
        for idx, row in df.iterrows():
            for genre in row['genres_found']:
                genre_mentions.append({
                    'genre': genre,
                    'date': row['processing_date'],
                    'platform': row['source_platform'],
                    'sentiment_strength': row['sentiment_strength'],
                    'overall_sentiment': row['overall_sentiment'],
                    'emotional_indicators': row['emotional_indicators'],
                    'artists_found': row['artists_found']
                })

        if not genre_mentions:
            self.logger.warning("No genre mentions found in data")
            return genre_trends

        genre_df = pd.DataFrame(genre_mentions)

        # Group by genre and calculate metrics
        for genre in genre_df['genre'].unique():
            genre_data = genre_df[genre_df['genre'] == genre]

            # Popularity score
            mention_count = len(genre_data)
            platform_count = len(genre_data['platform'].unique())
            popularity_score = mention_count * platform_count

            # Sentiment trend
            sentiment_scores = genre_data['sentiment_strength'].dropna()
            avg_sentiment = sentiment_scores.mean() if len(sentiment_scores) > 0 else 5.0

            if avg_sentiment > 6.5:
                sentiment_trend = "positive"
            elif avg_sentiment < 4.5:
                sentiment_trend = "negative"
            else:
                sentiment_trend = "neutral"

            # Artist diversity
            all_artists = []
            for artists_list in genre_data['artists_found']:
                all_artists.extend(artists_list)
            artist_diversity = len(set(all_artists))

            # Cross-platform presence
            cross_platform_presence = len(genre_data['platform'].unique())

            # Emotional associations
            all_emotions = []
            for emotions_list in genre_data['emotional_indicators']:
                all_emotions.extend(emotions_list)
            emotion_counts = Counter(all_emotions)
            emotional_associations = [emotion for emotion, count in emotion_counts.most_common(3)]

            # Trend momentum (simplified calculation)
            trend_momentum = min(popularity_score / 10.0, 1.0)

            genre_trends.append(GenreTrend(
                genre=genre,
                popularity_score=popularity_score,
                sentiment_trend=sentiment_trend,
                artist_diversity=artist_diversity,
                cross_platform_presence=cross_platform_presence,
                emotional_associations=emotional_associations,
                trend_momentum=trend_momentum
            ))

        # Sort by popularity score
        genre_trends.sort(key=lambda x: x.popularity_score, reverse=True)
        self.logger.info(f"Analyzed trends for {len(genre_trends)} genres")

        return genre_trends

    def analyze_temporal_trends(self, df: pd.DataFrame) -> List[TemporalTrend]:
        """Analyze trends over time periods"""
        temporal_trends = []

        if df.empty:
            return temporal_trends

        # Group by date
        df_sorted = df.sort_values('processing_date')
        dates = df_sorted['processing_date'].unique()

        for date in dates:
            date_data = df[df['processing_date'] == date]

            # Dominant artists
            all_artists = []
            for artists_list in date_data['artists_found']:
                all_artists.extend(artists_list)
            artist_counts = Counter(all_artists)
            dominant_artists = [artist for artist, count in artist_counts.most_common(3)]

            # Dominant genres
            all_genres = []
            for genres_list in date_data['genres_found']:
                all_genres.extend(genres_list)
            genre_counts = Counter(all_genres)
            dominant_genres = [genre for genre, count in genre_counts.most_common(3)]

            # Sentiment shift (compared to previous date if available)
            current_sentiment = date_data['sentiment_strength'].mean()
            sentiment_shift = 0.0  # Simplified - would compare to previous period

            # Engagement pattern
            total_mentions = len(date_data)
            if total_mentions >= 3:
                engagement_pattern = "high"
            elif total_mentions >= 2:
                engagement_pattern = "medium"
            else:
                engagement_pattern = "low"

            # Notable events (simplified - based on high sentiment variance)
            sentiment_variance = date_data['sentiment_strength'].var()
            notable_events = []
            if sentiment_variance > 5.0:
                notable_events.append("High sentiment variance detected")

            temporal_trends.append(TemporalTrend(
                time_period=date.strftime('%Y-%m-%d'),
                dominant_artists=dominant_artists,
                dominant_genres=dominant_genres,
                sentiment_shift=sentiment_shift,
                engagement_pattern=engagement_pattern,
                notable_events=notable_events
            ))

        self.logger.info(f"Analyzed temporal trends for {len(temporal_trends)} time periods")
        return temporal_trends

    def generate_trend_summary(self, artist_trends: List[TrendMetrics],
                             genre_trends: List[GenreTrend],
                             temporal_trends: List[TemporalTrend]) -> Dict[str, Any]:
        """Generate a comprehensive trend summary"""
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "overview": {
                "total_artists_analyzed": len(artist_trends),
                "total_genres_analyzed": len(genre_trends),
                "time_periods_analyzed": len(temporal_trends)
            },
            "top_artists": [
                {
                    "name": trend.entity_name,
                    "trend_strength": round(trend.trend_strength, 3),
                    "mentions": trend.mention_count,
                    "sentiment": trend.trend_direction,
                    "platforms": trend.platforms
                }
                for trend in artist_trends[:5]
            ],
            "top_genres": [
                {
                    "name": trend.genre,
                    "popularity_score": trend.popularity_score,
                    "sentiment_trend": trend.sentiment_trend,
                    "artist_diversity": trend.artist_diversity,
                    "platforms": trend.cross_platform_presence
                }
                for trend in genre_trends[:5]
            ],
            "sentiment_patterns": {
                "positive_trends": len([t for t in artist_trends if t.trend_direction == "positive"]),
                "negative_trends": len([t for t in artist_trends if t.trend_direction == "negative"]),
                "neutral_trends": len([t for t in artist_trends if t.trend_direction == "neutral"])
            },
            "engagement_levels": {
                "high": len([t for t in artist_trends if t.engagement_level == "high"]),
                "medium": len([t for t in artist_trends if t.engagement_level == "medium"]),
                "low": len([t for t in artist_trends if t.engagement_level == "low"])
            }
        }

        return summary

    def save_trends(self, artist_trends: List[TrendMetrics],
                   genre_trends: List[GenreTrend],
                   temporal_trends: List[TemporalTrend],
                   summary: Dict[str, Any],
                   output_dir: str) -> Dict[str, str]:
        """Save trend analysis results to files"""
        os.makedirs(output_dir, exist_ok=True)

        output_files = {}

        # Save artist trends
        artist_df = pd.DataFrame([asdict(trend) for trend in artist_trends])
        artist_file = os.path.join(output_dir, "artist_trends.csv")
        artist_df.to_csv(artist_file, index=False)
        output_files["artist_trends"] = artist_file

        # Save genre trends
        genre_df = pd.DataFrame([asdict(trend) for trend in genre_trends])
        genre_file = os.path.join(output_dir, "genre_trends.csv")
        genre_df.to_csv(genre_file, index=False)
        output_files["genre_trends"] = genre_file

        # Save temporal trends
        temporal_df = pd.DataFrame([asdict(trend) for trend in temporal_trends])
        temporal_file = os.path.join(output_dir, "temporal_trends.csv")
        temporal_df.to_csv(temporal_file, index=False)
        output_files["temporal_trends"] = temporal_file

        # Save summary
        summary_file = os.path.join(output_dir, "trend_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        output_files["summary"] = summary_file

        self.logger.info(f"Saved trend analysis results to {output_dir}")
        return output_files

    def analyze_trends(self, input_file: str, output_dir: str) -> Dict[str, Any]:
        """Main method to analyze trends from combined entity-sentiment data"""
        try:
            # Load and preprocess data
            df = self.load_data(input_file)
            df = self.preprocess_data(df)

            # Perform trend analysis
            artist_trends = self.analyze_artist_trends(df)
            genre_trends = self.analyze_genre_trends(df)
            temporal_trends = self.analyze_temporal_trends(df)

            # Generate summary
            summary = self.generate_trend_summary(artist_trends, genre_trends, temporal_trends)

            # Save results
            output_files = self.save_trends(artist_trends, genre_trends, temporal_trends,
                                          summary, output_dir)

            result = {
                "status": "success",
                "summary": summary,
                "output_files": output_files,
                "metrics": {
                    "artist_trends_found": len(artist_trends),
                    "genre_trends_found": len(genre_trends),
                    "temporal_periods_analyzed": len(temporal_trends)
                }
            }

            self.logger.info("Trend analysis completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metrics": {
                    "artist_trends_found": 0,
                    "genre_trends_found": 0,
                    "temporal_periods_analyzed": 0
                }
            }

def main():
    """Example usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze music trends from combined data')
    parser.add_argument('--input', '-i', required=True, help='Input CSV file with combined data')
    parser.add_argument('--output', '-o', required=True, help='Output directory for trend analysis')
    parser.add_argument('--config', '-c', help='Configuration file path')

    args = parser.parse_args()

    # Load configuration if provided
    config = None
    if args.config:
        config = TrendDetectionConfig.from_file(args.config)

    # Initialize trend detector
    detector = TrendDetector(config)

    # Run analysis
    result = detector.analyze_trends(args.input, args.output)

    if result["status"] == "success":
        print("✅ Trend analysis completed successfully!")
        print(f"📊 Found {result['metrics']['artist_trends_found']} artist trends")
        print(f"🎵 Found {result['metrics']['genre_trends_found']} genre trends")
        print(f"📅 Analyzed {result['metrics']['temporal_periods_analyzed']} time periods")
        print(f"📁 Results saved to: {args.output}")
    else:
        print(f"❌ Trend analysis failed: {result['error']}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
