#!/usr/bin/env python3
"""
Standalone Trend Detection Module (with embedded config)

This module analyzes combined entity and sentiment data to identify music trends.
Configuration is embedded to avoid import issues.

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
import sys
import os
import argparse # Added argparse
from pathlib import Path # Added Path

# Using embedded config for true standalone nature
class TrendDetectionConfig:
    """Simple configuration class"""
    def __init__(self):
        self.log_level = "INFO"
        self.min_mentions_for_trend = 2
        self.high_engagement_threshold = 3
        self.medium_engagement_threshold = 2
        self.positive_sentiment_threshold = 6.5
        self.negative_sentiment_threshold = 4.5
        self.mention_weight = 0.4
        self.sentiment_weight = 0.3
        self.consistency_weight = 0.3
        self.max_top_results = 10
        # Add default output filenames
        self.artist_trends_filename = "artist_trends.csv"
        self.genre_trends_filename = "genre_trends.csv"
        self.temporal_trends_filename = "temporal_trends.csv"
        self.trend_summary_filename = "trend_summary.json"

class TrendMetrics:
    """Simple class for storing trend metrics"""
    def __init__(self, entity_type, entity_name, mention_count, sentiment_score,
                 sentiment_consistency, growth_rate, engagement_level, trend_strength,
                 trend_direction, first_seen, last_seen, platforms, peak_sentiment,
                 sentiment_volatility):
        self.entity_type = entity_type
        self.entity_name = entity_name
        self.mention_count = mention_count
        self.sentiment_score = sentiment_score
        self.sentiment_consistency = sentiment_consistency
        self.growth_rate = growth_rate
        self.engagement_level = engagement_level
        self.trend_strength = trend_strength
        self.trend_direction = trend_direction
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.platforms = platforms
        self.peak_sentiment = peak_sentiment
        self.sentiment_volatility = sentiment_volatility

    def to_dict(self):
        return {
            'entity_type': self.entity_type,
            'entity_name': self.entity_name,
            'mention_count': self.mention_count,
            'sentiment_score': self.sentiment_score,
            'sentiment_consistency': self.sentiment_consistency,
            'growth_rate': self.growth_rate,
            'engagement_level': self.engagement_level,
            'trend_strength': self.trend_strength,
            'trend_direction': self.trend_direction,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'platforms': str(self.platforms), # Ensure platforms are stringified for CSV
            'peak_sentiment': self.peak_sentiment,
            'sentiment_volatility': self.sentiment_volatility
        }

class GenreTrend:
    """Simple class for genre trends"""
    def __init__(self, genre, popularity_score, sentiment_trend, artist_diversity,
                 cross_platform_presence, emotional_associations, trend_momentum):
        self.genre = genre
        self.popularity_score = popularity_score
        self.sentiment_trend = sentiment_trend
        self.artist_diversity = artist_diversity
        self.cross_platform_presence = cross_platform_presence
        self.emotional_associations = emotional_associations
        self.trend_momentum = trend_momentum

    def to_dict(self):
        return {
            'genre': self.genre,
            'popularity_score': self.popularity_score,
            'sentiment_trend': self.sentiment_trend,
            'artist_diversity': self.artist_diversity,
            'cross_platform_presence': self.cross_platform_presence,
            'emotional_associations': str(self.emotional_associations), # Ensure lists are stringified
            'trend_momentum': self.trend_momentum
        }

class TemporalTrend:
    """Data class for temporal trend analysis"""
    def __init__(self, time_period: str, dominant_artists: List[str], dominant_genres: List[str],
                 sentiment_shift: float, engagement_pattern: str, notable_events: List[str]):
        self.time_period = time_period
        self.dominant_artists = dominant_artists
        self.dominant_genres = dominant_genres
        self.sentiment_shift = sentiment_shift
        self.engagement_pattern = engagement_pattern
        self.notable_events = notable_events

    def to_dict(self):
        return {
            'time_period': self.time_period,
            'dominant_artists': str(self.dominant_artists),
            'dominant_genres': str(self.dominant_genres),
            'sentiment_shift': self.sentiment_shift,
            'engagement_pattern': self.engagement_pattern,
            'notable_events': str(self.notable_events)
        }

class TrendDetector:
    """
    Analyzes combined entity and sentiment data to detect music trends
    """

    def __init__(self, config: Optional[TrendDetectionConfig] = None, ollama_host: Optional[str] = None):
        """Initialize the trend detector"""
        self.config = config or TrendDetectionConfig()
        self.ollama_host = ollama_host
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        if self.ollama_host:
            self.logger.info(f"TrendDetector initialized with Ollama host: {self.ollama_host} (currently not used for LLM calls by this class).")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper(), logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load the combined entity-sentiment data"""
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data from {file_path}: {e}")
            raise

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data for trend analysis"""
        date_col_options = ['analysis_date', 'source_date', 'processing_date', 'created_utc_fmt', 'comment_published_at', 'date']
        date_col_to_use = None
        for col in date_col_options:
            if col in df.columns:
                date_col_to_use = col
                break

        if date_col_to_use:
            df[date_col_to_use] = pd.to_datetime(df[date_col_to_use], errors='coerce')
            if date_col_to_use != 'processing_date': # Standardize column name
                 df.rename(columns={date_col_to_use: 'processing_date'}, inplace=True)
            self.logger.info(f"Using '{date_col_to_use}' as processing_date.")
        else:
            self.logger.warning(f"Could not find a suitable date column from {date_col_options}. Temporal analysis might be affected. Creating a dummy 'processing_date' with current date.")
            df['processing_date'] = pd.to_datetime(datetime.now().date())

        def safe_parse_json(text):
            if pd.isna(text) or text == '[]' or text == '':
                return []
            try:
                # Attempt to load if it's a valid JSON string representation of a list
                if isinstance(text, str) and text.startswith('[') and text.endswith(']'):
                    return json.loads(text.replace("'", '"')) # More robust replacement for single quotes
                elif isinstance(text, list): # Already a list
                    return text
                return [] # Fallback for other types or malformed strings
            except json.JSONDecodeError:
                self.logger.debug(f"Could not parse text as JSON list: {text[:100]}")
                return [] # Fallback for malformed JSON
            except Exception as e:
                self.logger.error(f"Unexpected error in safe_parse_json for text {text[:100]}: {e}")
                return []

        for col_name in ['artists_found', 'songs_found', 'genres_found', 'emotional_indicators']:
            if col_name not in df.columns:
                df[col_name] = pd.Series([[] for _ in range(len(df))])
            else:
                df[col_name] = df[col_name].fillna('[]').astype(str) # Ensure string type before apply
            df[col_name] = df[col_name].apply(safe_parse_json)

        df['sentiment_strength'] = pd.to_numeric(df.get('sentiment_strength', 5.0), errors='coerce').fillna(5.0)
        df['sentiment_confidence'] = pd.to_numeric(df.get('sentiment_confidence', 0.5), errors='coerce').fillna(0.5)
        df['overall_sentiment'] = df.get('overall_sentiment', 'neutral').fillna('neutral')
        df['artist_sentiment'] = df.get('artist_sentiment', 'none').fillna('none')
        df['source_platform'] = df.get('source_platform', 'unknown').fillna('unknown')

        self.logger.info("Data preprocessing completed")
        return df

    def analyze_artist_trends(self, df: pd.DataFrame) -> List[TrendMetrics]:
        """Analyze trends for individual artists"""
        artist_trends = []
        if 'artists_found' not in df.columns or 'processing_date' not in df.columns:
            self.logger.warning("Missing 'artists_found' or 'processing_date' for artist trend analysis.")
            return artist_trends

        artist_mentions = []
        for idx, row in df.iterrows():
            for artist in row.get('artists_found', []):
                if not isinstance(artist, str) or not artist.strip(): # Skip non-string or empty artists
                    continue
                artist_mentions.append({
                    'artist': artist,
                    'date': row['processing_date'],
                    'platform': row.get('source_platform', 'unknown'),
                    'sentiment_strength': row.get('sentiment_strength', 5.0),
                    'sentiment_confidence': row.get('sentiment_confidence', 0.5),
                    'overall_sentiment': row.get('overall_sentiment', 'neutral'),
                    'artist_sentiment': row.get('artist_sentiment', 'none')
                })

        if not artist_mentions:
            self.logger.info("No valid artist mentions found in data after filtering.")
            return artist_trends

        artist_df = pd.DataFrame(artist_mentions)
        for artist_name in artist_df['artist'].unique():
            artist_data = artist_df[artist_df['artist'] == artist_name]
            mention_count = len(artist_data)
            sentiment_scores = artist_data['sentiment_strength'].dropna()
            avg_sentiment = sentiment_scores.mean() if not sentiment_scores.empty else 5.0
            sentiment_consistency = 1.0 - (sentiment_scores.std() / 10.0) if len(sentiment_scores) > 1 else 1.0
            dates = artist_data['date'].dropna().sort_values()
            growth_rate = 0.0
            if not dates.empty:
                time_span_days = (dates.iloc[-1] - dates.iloc[0]).days if len(dates) > 1 else 1
                growth_rate = mention_count / max(time_span_days, 1)

            engagement_level = "low"
            if mention_count >= self.config.high_engagement_threshold:
                engagement_level = "high"
            elif mention_count >= self.config.medium_engagement_threshold:
                engagement_level = "medium"

            trend_strength = (
                min(mention_count / (self.config.high_engagement_threshold * 2), 1.0) * self.config.mention_weight +
                (avg_sentiment / 10.0) * self.config.sentiment_weight +
                sentiment_consistency * self.config.consistency_weight
            )
            trend_direction = "neutral"
            if avg_sentiment > self.config.positive_sentiment_threshold:
                trend_direction = "positive"
            elif avg_sentiment < self.config.negative_sentiment_threshold:
                trend_direction = "negative"

            artist_trends.append(TrendMetrics(
                entity_type="artist",
                entity_name=artist_name,
                mention_count=mention_count,
                sentiment_score=avg_sentiment,
                sentiment_consistency=sentiment_consistency,
                growth_rate=growth_rate,
                engagement_level=engagement_level,
                trend_strength=trend_strength,
                trend_direction=trend_direction,
                first_seen=dates.iloc[0].strftime('%Y-%m-%d') if not dates.empty else "N/A",
                last_seen=dates.iloc[-1].strftime('%Y-%m-%d') if not dates.empty else "N/A",
                platforms=list(artist_data['platform'].unique()),
                peak_sentiment=sentiment_scores.max() if not sentiment_scores.empty else avg_sentiment,
                sentiment_volatility=sentiment_scores.std() if not sentiment_scores.empty else 0.0
            ))
        artist_trends.sort(key=lambda x: x.trend_strength, reverse=True)
        self.logger.info(f"Analyzed trends for {len(artist_trends)} artists")
        return artist_trends

    def analyze_genre_trends(self, df: pd.DataFrame) -> List[GenreTrend]:
        """Analyze trends for music genres"""
        genre_trends = []
        if 'genres_found' not in df.columns or 'processing_date' not in df.columns:
            self.logger.warning("Missing 'genres_found' or 'processing_date' for genre trend analysis.")
            return genre_trends

        genre_mentions = []
        for idx, row in df.iterrows():
            for genre in row.get('genres_found', []):
                if not isinstance(genre, str) or not genre.strip(): continue
                genre_mentions.append({
                    'genre': genre,
                    'date': row['processing_date'],
                    'platform': row.get('source_platform', 'unknown'),
                    'sentiment_strength': row.get('sentiment_strength', 5.0),
                    'overall_sentiment': row.get('overall_sentiment', 'neutral'),
                    'emotional_indicators': row.get('emotional_indicators', []),
                    'artists_found': row.get('artists_found', [])
                })

        if not genre_mentions:
            self.logger.info("No valid genre mentions found.")
            return genre_trends

        genre_df = pd.DataFrame(genre_mentions)
        for genre_name in genre_df['genre'].unique():
            genre_data = genre_df[genre_df['genre'] == genre_name]
            mention_count = len(genre_data)
            platform_count = len(genre_data['platform'].unique())
            popularity_score = mention_count * platform_count
            sentiment_scores = genre_data['sentiment_strength'].dropna()
            avg_sentiment = sentiment_scores.mean() if not sentiment_scores.empty else 5.0
            sentiment_trend = "neutral"
            if avg_sentiment > self.config.positive_sentiment_threshold: sentiment_trend = "positive"
            elif avg_sentiment < self.config.negative_sentiment_threshold: sentiment_trend = "negative"
            all_artists_in_genre = []
            for artists_list in genre_data['artists_found']:
                all_artists_in_genre.extend(artists_list)
            artist_diversity = len(set(all_artists_in_genre))
            all_emotions = []
            for emotions_list in genre_data['emotional_indicators']:
                all_emotions.extend(emotions_list)
            emotion_counts = Counter(all_emotions)
            emotional_associations = [emotion for emotion, count in emotion_counts.most_common(3)]
            trend_momentum = min(popularity_score / (self.config.high_engagement_threshold * platform_count if platform_count > 0 else 10.0), 1.0)

            genre_trends.append(GenreTrend(
                genre=genre_name,
                popularity_score=popularity_score,
                sentiment_trend=sentiment_trend,
                artist_diversity=artist_diversity,
                cross_platform_presence=platform_count,
                emotional_associations=emotional_associations,
                trend_momentum=trend_momentum
            ))
        genre_trends.sort(key=lambda x: x.popularity_score, reverse=True)
        self.logger.info(f"Analyzed trends for {len(genre_trends)} genres")
        return genre_trends

    def analyze_temporal_trends(self, df: pd.DataFrame) -> List[TemporalTrend]:
        """Analyze trends over time periods"""
        temporal_trends = []
        if df.empty or 'processing_date' not in df.columns or df['processing_date'].isnull().all():
            self.logger.warning("Cannot analyze temporal trends due to empty data or missing/invalid 'processing_date'.")
            return temporal_trends

        df_sorted_by_date = df.sort_values('processing_date')
        unique_dates = df_sorted_by_date['processing_date'].unique()

        for period_date in unique_dates:
            if pd.isna(period_date): continue # Skip NaT dates
            daily_data = df_sorted_by_date[df_sorted_by_date['processing_date'] == period_date]
            all_artists_today = []
            for artists_list in daily_data.get('artists_found', pd.Series([[]]*len(daily_data))):
                all_artists_today.extend(artists_list)
            artist_counts_today = Counter(all_artists_today)
            dominant_artists = [artist for artist, count in artist_counts_today.most_common(3)]
            all_genres_today = []
            for genres_list in daily_data.get('genres_found', pd.Series([[]]*len(daily_data))):
                all_genres_today.extend(genres_list)
            genre_counts_today = Counter(all_genres_today)
            dominant_genres = [genre for genre, count in genre_counts_today.most_common(3)]
            current_sentiment_avg = daily_data['sentiment_strength'].mean()
            sentiment_shift = 0.0 # Simplified; requires comparison to previous period for true shift
            total_mentions_today = len(daily_data)
            engagement_pattern = "low"
            if total_mentions_today >= self.config.high_engagement_threshold: engagement_pattern = "high"
            elif total_mentions_today >= self.config.medium_engagement_threshold: engagement_pattern = "medium"
            sentiment_variance_today = daily_data['sentiment_strength'].var()
            notable_events = ["High sentiment variance"] if sentiment_variance_today > 5.0 else []

            temporal_trends.append(TemporalTrend(
                time_period=pd.to_datetime(period_date).strftime('%Y-%m-%d'),
                dominant_artists=dominant_artists,
                dominant_genres=dominant_genres,
                sentiment_shift=current_sentiment_avg, # Reporting avg sentiment for the period
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
                for trend in artist_trends[:self.config.max_top_results]
            ],
            "top_genres": [
                {
                    "name": trend.genre,
                    "popularity_score": trend.popularity_score,
                    "sentiment_trend": trend.sentiment_trend,
                    "artist_diversity": trend.artist_diversity,
                    "platforms": trend.cross_platform_presence
                }
                for trend in genre_trends[:self.config.max_top_results]
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
                   temporal_trends: List[TemporalTrend], # Corrected: ensure this param is used
                   summary: Dict[str, Any],
                   output_dir: str) -> Dict[str, str]:
        """Save trend analysis results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_files = {}

        if artist_trends:
            artist_df = pd.DataFrame([t.to_dict() for t in artist_trends])
            path = output_path / self.config.artist_trends_filename
            artist_df.to_csv(path, index=False)
            output_files['artist_trends'] = str(path)
            self.logger.info(f"Saved artist trends to {path}")
        else: self.logger.info("No artist trends to save.")

        if genre_trends:
            genre_df = pd.DataFrame([g.to_dict() for g in genre_trends])
            path = output_path / self.config.genre_trends_filename
            genre_df.to_csv(path, index=False)
            output_files['genre_trends'] = str(path)
            self.logger.info(f"Saved genre trends to {path}")
        else: self.logger.info("No genre trends to save.")

        if temporal_trends: # Corrected: use the parameter
            temporal_df = pd.DataFrame([t.to_dict() for t in temporal_trends])
            path = output_path / self.config.temporal_trends_filename
            temporal_df.to_csv(path, index=False)
            output_files['temporal_trends'] = str(path)
            self.logger.info(f"Saved temporal trends to {path}")
        else: self.logger.info("No temporal trends to save.")

        if summary:
            path = output_path / self.config.trend_summary_filename
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            output_files['trend_summary'] = str(path)
            self.logger.info(f"Saved trend summary to {path}")
        else: self.logger.info("No summary to save.")

        return output_files

    def analyze_trends(self, input_file_path: str, output_dir: str) -> Dict[str, Any]:
        """Main method to run all trend analyses and save results"""
        self.logger.info(f"Starting trend analysis for file: {input_file_path}")
        try:
            df = self.load_data(input_file_path)
            df = self.preprocess_data(df)

            artist_trends = self.analyze_artist_trends(df)
            genre_trends = self.analyze_genre_trends(df)
            temporal_trends = self.analyze_temporal_trends(df)

            summary = self.generate_trend_summary(artist_trends, genre_trends, temporal_trends)

            output_files = self.save_trends(artist_trends, genre_trends, temporal_trends, summary, output_dir)

            self.logger.info("Trend analysis completed.")
            return {
                "status": "success",
                "output_files": output_files,
                "metrics": {
                    "artist_trends_found": len(artist_trends),
                    "genre_trends_found": len(genre_trends),
                    "temporal_periods_analyzed": len(temporal_trends)
                },
                "summary": summary
            }
        except Exception as e:
            self.logger.error(f"Error during trend analysis pipeline: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Standalone Trend Detection Module for Japanese Music Social Media Analysis.")
    parser.add_argument("--input_file", type=str, required=True,
                        help="Path to the input CSV file (typically sentiment analysis output).")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Directory to save the trend analysis results (CSV files and JSON summary).")
    parser.add_argument("--ollama-host", type=str, default=None,
                        help="Optional: Ollama host URL (e.g., http://localhost:11434). Currently not used by TrendDetector for LLM calls but included for consistency.")

    args = parser.parse_args()

    config = TrendDetectionConfig()
    detector = TrendDetector(config=config, ollama_host=args.ollama_host)

    results = detector.analyze_trends(args.input_file, args.output_dir)

    if results["status"] == "success":
        print("\\n✅ Trend detection completed successfully!")
        if "output_files" in results and results["output_files"]:
            print("Output files:")
            for key, path in results["output_files"].items():
                print(f"  - {key}: {path}")
        if "metrics" in results and results["metrics"]:
            print("\\nMetrics:")
            for key, value in results["metrics"].items():
                print(f"  - {key}: {value}")
    else:
        print("\\n❌ Trend detection failed.")
        if "error" in results:
            print(f"Error: {results['error']}")

if __name__ == "__main__":
    main()
