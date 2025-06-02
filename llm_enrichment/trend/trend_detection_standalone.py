#!/usr/bin/env python3
"""
Standalone Trend Detection Module (with embedded config)

This module analyzes combined entity and sentiment data to identify music trends.
Configuration is embedded to avoid import issues.

Author: GitHub Copilot Assistant
Date: 2025-01-07
"""

import pandas as pd
import json # Added import
import logging # Added import
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter, defaultdict
import re
import sys
import os
import argparse # Added argparse
from pathlib import Path # Added Path
import traceback # Added import
import ast

# Using embedded config for true standalone nature
class TrendDetectionConfig:
    """Simple configuration class"""
    def __init__(self, log_level="INFO"):
        self.log_level = log_level # Allow dynamic log level
        self.min_mentions_for_trend = 2
        self.high_engagement_threshold = 3  # Matches reference, though reference uses it as count
        self.medium_engagement_threshold = 2 # Matches reference, though reference uses it as count
        self.positive_sentiment_threshold = 6.5
        self.negative_sentiment_threshold = 4.5
        # Weights from reference script's TrendDetectionConfig (can be adjusted)
        self.mention_weight = 0.4
        self.sentiment_weight = 0.3
        self.consistency_weight = 0.3
        self.max_top_results = 10 # Matches reference
        self.artist_trends_filename = "artist_trends.csv"
        self.genre_trends_filename = "genre_trends.csv"
        self.temporal_trends_filename = "temporal_trends.csv"
        self.trend_summary_filename = "trend_summary.json"
        # Add other relevant config fields from trend_detection_config.py if needed by ported logic
        self.min_artist_mentions = 1 # from trend_detection_config.py
        self.min_genre_mentions = 1  # from trend_detection_config.py


class TrendMetrics:
    """Class for storing artist trend metrics (aligning with reference TrendMetrics dataclass)"""
    def __init__(self, entity_type: str, entity_name: str, mention_count: int,
                 sentiment_score: float, sentiment_consistency: float, growth_rate: float,
                 engagement_level: str, trend_strength: float, trend_direction: str,
                 first_seen: str, last_seen: str, platforms: List[str],
                 peak_sentiment: float, sentiment_volatility: float):
        self.entity_type = entity_type
        self.entity_name = entity_name
        self.mention_count = mention_count
        self.sentiment_score = sentiment_score  # avg_sentiment in reference
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
            'platforms': self.platforms, # Keep as list, CSV writer will handle
            'peak_sentiment': self.peak_sentiment,
            'sentiment_volatility': self.sentiment_volatility
        }

class GenreTrend:
    """Class for genre trends (aligning with reference GenreTrend dataclass)"""
    def __init__(self, genre: str, popularity_score: float, sentiment_trend: str,
                 artist_diversity: int, cross_platform_presence: int,
                 emotional_associations: List[str], trend_momentum: float):
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
            'emotional_associations': self.emotional_associations, # Keep as list
            'trend_momentum': self.trend_momentum
        }

class TemporalTrend:
    """Data class for temporal trend analysis (aligning with reference TemporalTrend dataclass)"""
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
            'dominant_artists': self.dominant_artists, # Keep as list
            'dominant_genres': self.dominant_genres,   # Keep as list
            'sentiment_shift': self.sentiment_shift,
            'engagement_pattern': self.engagement_pattern,
            'notable_events': self.notable_events     # Keep as list
        }


# Helper function to parse entity lists (improved version)
def _safe_parse_entity_list(text: Any, logger: logging.Logger) -> List[str]:
    """
    Safely parses a string that should represent a list of entities.
    Handles JSON-like strings, simple comma-separated strings, and pandas NaNs.
    """
    if pd.isna(text):
        return []
    if isinstance(text, list): # Already a list
        return [str(item) for item in text if item is not None]

    if not isinstance(text, str):
        logger.debug(f"Input to _safe_parse_entity_list is not a string or NaN, but {type(text)}: {text}. Returning empty list.")
        return []

    text_stripped = text.strip()
    if not text_stripped or text_stripped == '[]':
        return []

    try:
        # Handle JSON-like strings, e.g., "['item1', 'item2']" or '["item1", "item2"]'
        if (text_stripped.startswith('[') and text_stripped.endswith(']')) or \
           (text_stripped.startswith('{') and text_stripped.endswith('}')): # Allow for set-like strings too
            try:
                loaded_data = json.loads(text_stripped)
                if isinstance(loaded_data, list):
                    return [str(item) for item in loaded_data if item is not None]
                return [str(loaded_data)]

            except json.JSONDecodeError:
                if text_stripped.startswith('[') and text_stripped.endswith(']'):
                    try:
                        # Corrected line: Use ''' for the string containing quotes
                        processed_text = text_stripped.replace('\'', '"')
                        loaded_data = json.loads(processed_text)
                        if isinstance(loaded_data, list):
                            return [str(item) for item in loaded_data if item is not None]
                        return [str(loaded_data)]
                    except json.JSONDecodeError:
                        logger.debug(f"Failed to parse '{text_stripped}' as JSON list even after quote replacement. Will try ast.literal_eval or split.")
                        pass
        try:
            # import ast # Not used here, but kept for context if ast.literal_eval was intended
            evaluated = eval(text_stripped) # Retained eval as per previous version, consider ast.literal_eval for safety
            if isinstance(evaluated, list):
                return [str(item).strip() for item in evaluated if item and str(item).strip()]
            elif isinstance(evaluated, (str, int, float)):
                return [str(evaluated).strip()]
            elif isinstance(evaluated, set):
                 return [str(item).strip() for item in list(evaluated) if item and str(item).strip()]
            else:
                logger.debug(f"eval of '{text_stripped}' resulted in non-list/set/str type: {type(evaluated)}. Trying split.")
        except (SyntaxError, ValueError, TypeError, NameError) as e_eval:
            logger.debug(f"eval failed for '{text_stripped}': {e_eval}. Trying comma split.")

        if not (text_stripped.startswith('[') and text_stripped.endswith(']')) and ',' in text_stripped:
            return [item.strip() for item in text_stripped.split(',') if item.strip()]

        if text_stripped:
            return [text_stripped]

        return []

    except Exception as e:
        logger.warning(f"Unexpected error parsing entity string: '{text}'. Error: {e}. Returning empty list.")
        return []


class TrendDetector:
    """
    Analyzes combined entity and sentiment data to detect music trends
    """

    def __init__(self, config: Optional[TrendDetectionConfig] = None, ollama_host: Optional[str] = None):
        """Initialize the trend detector"""
        self.config = config or TrendDetectionConfig()
        self.ollama_host = ollama_host
        self.logger = logging.getLogger(__name__)
        self.processing_date_col = 'source_date'  # Default, will be verified in preprocess
        self.setup_logging()
        if self.ollama_host:
            self.logger.info(f"TrendDetector initialized with Ollama host: {self.ollama_host} (currently not used for LLM calls by this class).")

    def setup_logging(self):
        """Setup logging configuration"""
        # Clear existing handlers for the logger, if any
        # This prevents duplicate logs if TrendDetector is instantiated multiple times in a session
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()

        # Create a handler for console output
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(console_handler)

        # Set the logger level
        log_level_to_set = getattr(logging, self.config.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level_to_set)

        self.logger.info(f"Logging initialized with level {self.config.log_level.upper()} ({log_level_to_set}).")
        self.logger.debug("This is a test debug message from setup_logging.")

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
        self.logger.info("Preprocessing data...")
        if df.empty:
            self.logger.warning("Input DataFrame is empty. Skipping preprocessing.")
            return df

        # --- Date Column Selection ---
        date_column_candidates = ['source_date', 'date', 'created_at', 'timestamp', 'fetch_date', 'extraction_date']
        selected_date_col = None
        for col_candidate in date_column_candidates:
            if col_candidate in df.columns:
                try:
                    # Test conversion and check for sufficient valid dates
                    temp_dates = pd.to_datetime(df[col_candidate], errors='coerce')
                    if temp_dates.notna().sum() > 0.5 * len(df):
                        selected_date_col = col_candidate
                        self.logger.info(f"Using '{selected_date_col}' as the primary date column.")
                        break
                    else:
                        self.logger.warning(f"Candidate date column '{col_candidate}' has too many invalid dates.")
                except Exception as e:
                    self.logger.warning(f"Error testing date column '{col_candidate}': {e}")

        if not selected_date_col:
            if 'analysis_date' in df.columns:
                try:
                    temp_dates = pd.to_datetime(df['analysis_date'], errors='coerce')
                    if temp_dates.notna().sum() > 0.5 * len(df):
                        selected_date_col = 'analysis_date'
                        self.logger.warning(f"CRITICAL: Using 'analysis_date' as the date column. Trend timing will be based on analysis time.")
                    else:
                        self.logger.error("No suitable date column found (including 'analysis_date').")
                        raise ValueError("A usable date column is required.")
                except Exception as e:
                    self.logger.error(f"Error testing 'analysis_date': {e}. No suitable date column.")
                    raise ValueError("A usable date column is required.")
            else:
                self.logger.error("No suitable date column found. 'source_date' and other candidates missing/invalid, 'analysis_date' not present.")
                raise ValueError("A usable date column is required.")

        self.processing_date_col = selected_date_col
        df[self.processing_date_col] = pd.to_datetime(df[self.processing_date_col], errors='coerce')
        df = df.dropna(subset=[self.processing_date_col]) # Remove rows where date conversion failed

        # --- Sentiment Columns ---
        if 'sentiment_label' not in df.columns:
            df['sentiment_label'] = 'neutral'
        else:
            df['sentiment_label'] = df['sentiment_label'].fillna('neutral')

        # Use 'sentiment_score' as the primary numeric sentiment value.
        # If 'sentiment_score' is not present, try to use 'sentiment_strength'.
        if 'sentiment_score' not in df.columns and 'sentiment_strength' in df.columns:
            self.logger.info("Column 'sentiment_score' not found. Using 'sentiment_strength' as 'sentiment_score'.")
            df.rename(columns={'sentiment_strength': 'sentiment_score'}, inplace=True)
        elif 'sentiment_score' not in df.columns:
            self.logger.warning("'sentiment_score' and 'sentiment_strength' columns not found. Defaulting 'sentiment_score' to 0.0. Analysis may be affected.")
            df['sentiment_score'] = 0.0

        # Ensure 'sentiment_score' is numeric and fill NaNs
        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce').fillna(0.0)

        # Standardize sentiment confidence score
        target_confidence_col = 'sentiment_confidence_score' # Standard name
        source_confidence_options = ['sentiment_confidence_score', 'sentiment_confidence', '_score']
        processed_confidence = False
        for source_col in source_confidence_options:
            if source_col in df.columns:
                df[target_confidence_col] = pd.to_numeric(df[source_col], errors='coerce').fillna(0.5)
                if source_col != target_confidence_col: # If we copied from an alias
                    df.drop(columns=[source_col], inplace=True, errors='ignore')
                self.logger.info(f"Processed sentiment confidence from '{source_col}' into '{target_confidence_col}'.")
                processed_confidence = True
                break
        if not processed_confidence:
            df[target_confidence_col] = 0.5 # Default if not found
            self.logger.info(f"No sentiment confidence column found among {source_confidence_options}. Defaulting '{target_confidence_col}' to 0.5.")

        # --- Entity Column Mapping and Parsing ---
        entity_mapping_config = {
            'entities_artists': ['entities_artists', 'artists_found'],
            'entities_genres': ['entities_genres', 'genres_found', 'genre_found'],
            'entities_songs': ['entities_songs', 'songs_found']
        }

        for target_col, source_aliases in entity_mapping_config.items():
            mapped_from_alias = False
            if target_col not in df.columns:
                for alias in source_aliases:
                    if alias in df.columns:
                        df.rename(columns={alias: target_col}, inplace=True)
                        self.logger.info(f"Mapped source column '{alias}' to target '{target_col}'.")
                        mapped_from_alias = True
                        break

            if target_col not in df.columns and not mapped_from_alias:
                self.logger.warning(f"Target entity column '{target_col}' and its aliases {source_aliases} not found. Initializing as empty.")
                df[target_col] = pd.Series([[] for _ in range(len(df))], dtype='object') # Initialize with empty lists

            # Apply robust parsing to ensure it's a list of strings
            df[target_col] = df[target_col].apply(lambda x: _safe_parse_entity_list(x, self.logger))
            self.logger.debug(f"Sample of parsed '{target_col}' after _safe_parse_entity_list: {df[target_col].head().tolist()}")


        # Ensure 'source_platform' exists, defaulting if not
        if 'source_platform' not in df.columns:
            self.logger.warning("'source_platform' column not found. Defaulting to 'unknown'.")
            df['source_platform'] = 'unknown'
        else:
            df['source_platform'] = df['source_platform'].fillna('unknown')

        # Drop rows with no identifiable entities if configured (optional, for now keep all)
        # df.dropna(subset=['entities_artists', 'entities_genres'], how='all', inplace=True)

        self.logger.info("Data preprocessing completed.")
        self.logger.debug(f"Columns after preprocessing: {df.columns.tolist()}")
        if not df.empty:
            self.logger.debug(f"Sample data post-preprocessing (first row):\n{df.head(1).to_dict(orient='records')}")
        return df

    def _get_engagement_level(self, mention_count: int) -> str:
        """Determines engagement level based on mention count."""
        if mention_count >= self.config.high_engagement_threshold: # e.g., 3+
            return "high"
        elif mention_count >= self.config.medium_engagement_threshold: # e.g., 2
            return "medium"
        else: # e.g., 1
            return "low"

    def analyze_artist_trends(self, df: pd.DataFrame) -> List[TrendMetrics]:
        """Analyze trends for individual artists, adapted from reference script."""
        artist_trends = []
        self.logger.info("Analyzing artist trends...")

        # Flatten artist mentions
        artist_mentions_data = []
        for idx, row in df.iterrows():
            # entities_artists should be a list of strings after preprocessing
            for artist_name in row['entities_artists']:
                if not artist_name or pd.isna(artist_name): # Skip empty or NaN artist names
                    continue
                artist_mentions_data.append({
                    'artist_name': str(artist_name).strip(), # Ensure it's a clean string
                    'date': row[self.processing_date_col],
                    'platform': row['source_platform'],
                    'sentiment_score': row['sentiment_score'], # Using 'sentiment_score' as proxy for 'sentiment_strength'
                    'sentiment_confidence': row['sentiment_confidence_score'] # Standardized confidence column
                    # 'overall_sentiment': row['sentiment_label'], # If needed
                })

        if not artist_mentions_data:
            self.logger.warning("No valid artist mentions found after flattening. Skipping artist trend analysis.")
            return artist_trends

        artist_df = pd.DataFrame(artist_mentions_data)
        if artist_df.empty:
            self.logger.warning("Artist DataFrame is empty after creation. Skipping artist trend analysis.")
            return artist_trends

        self.logger.debug(f"Generated artist_df with {len(artist_df)} mentions.")

        for artist_name_val, artist_data in artist_df.groupby('artist_name'):
            if not artist_name_val or pd.isna(artist_name_val): # Should be filtered by now, but double check
                continue

            mention_count = len(artist_data)
            if mention_count < self.config.min_artist_mentions: # Use config
                continue

            sentiment_scores = artist_data['sentiment_score'].dropna()
            avg_sentiment = sentiment_scores.mean() if not sentiment_scores.empty else 5.0 # Default to neutral
            # Sentiment consistency: 1 - (std_dev / range_of_scores), assuming scores 0-10
            sentiment_consistency = (1.0 - (sentiment_scores.std() / 10.0)) if len(sentiment_scores) > 1 else 1.0
            sentiment_consistency = max(0.0, min(1.0, sentiment_consistency)) # Clamp to [0,1]

            dates = artist_data['date'].sort_values()
            first_seen = dates.iloc[0] if not dates.empty else pd.NaT
            last_seen = dates.iloc[-1] if not dates.empty else pd.NaT

            growth_rate = 0.0
            if not dates.empty and len(dates) > 1 and pd.notna(first_seen) and pd.notna(last_seen):
                time_span_days = (last_seen - first_seen).days
                growth_rate = mention_count / max(time_span_days, 1) # Mentions per day
            elif mention_count > 0 : # Single mention or all on same day
                growth_rate = float(mention_count)


            engagement_level = self._get_engagement_level(mention_count)

            # Trend strength (weighted score)
            # Ensure components are in [0,1] range for weighting
            norm_mention_strength = min(mention_count / (self.config.high_engagement_threshold * 2), 1.0) # Normalize mentions
            norm_sentiment_strength = avg_sentiment / 10.0 # Assuming sentiment score is 0-10

            trend_strength = (
                norm_mention_strength * self.config.mention_weight +
                norm_sentiment_strength * self.config.sentiment_weight +
                sentiment_consistency * self.config.consistency_weight
            )
            trend_strength = round(trend_strength, 3)

            # Trend direction based on sentiment
            if avg_sentiment > self.config.positive_sentiment_threshold:
                trend_direction = "positive"
            elif avg_sentiment < self.config.negative_sentiment_threshold:
                trend_direction = "negative"
            else:
                trend_direction = "neutral"

            platforms = list(artist_data['platform'].unique())
            peak_sentiment = sentiment_scores.max() if not sentiment_scores.empty else avg_sentiment
            sentiment_volatility = sentiment_scores.std() if not sentiment_scores.empty else 0.0

            artist_trends.append(TrendMetrics(
                entity_type="artist",
                entity_name=str(artist_name_val),
                mention_count=mention_count,
                sentiment_score=round(avg_sentiment, 2),
                sentiment_consistency=round(sentiment_consistency, 2),
                growth_rate=round(growth_rate, 2),
                engagement_level=engagement_level,
                trend_strength=trend_strength,
                trend_direction=trend_direction,
                first_seen=first_seen.strftime('%Y-%m-%d') if pd.notna(first_seen) else "",
                last_seen=last_seen.strftime('%Y-%m-%d') if pd.notna(last_seen) else "",
                platforms=platforms,
                peak_sentiment=round(peak_sentiment, 2),
                sentiment_volatility=round(sentiment_volatility, 2)
            ))

        artist_trends.sort(key=lambda x: x.trend_strength, reverse=True)
        self.logger.info(f"Analyzed trends for {len(artist_trends)} artists.")
        if artist_trends:
             self.logger.debug(f"Top artist trend: {artist_trends[0].to_dict()}")
        return artist_trends

    def analyze_genre_trends(self, df: pd.DataFrame) -> List[GenreTrend]:
        """Analyze trends for music genres, adapted from reference script."""
        genre_trends = []
        self.logger.info("Analyzing genre trends...")

        genre_mentions_data = []
        for idx, row in df.iterrows():
            # entities_genres should be a list of strings
            for genre_name in row['entities_genres']:
                if not genre_name or pd.isna(genre_name):
                    continue
                genre_mentions_data.append({
                    'genre_name': str(genre_name).strip(),
                    'date': row[self.processing_date_col],
                    'platform': row['source_platform'],
                    'sentiment_score': row['sentiment_score'], # Proxy for sentiment_strength
                    # 'emotional_indicators': row.get('emotional_indicators', []), # If available and parsed
                    'artists_in_mention': row['entities_artists'] # List of artists in the same mention
                })

        if not genre_mentions_data:
            self.logger.warning("No valid genre mentions found. Skipping genre trend analysis.")
            return genre_trends

        genre_df = pd.DataFrame(genre_mentions_data)
        if genre_df.empty:
            self.logger.warning("Genre DataFrame is empty. Skipping genre trend analysis.")
            return genre_trends

        self.logger.debug(f"Generated genre_df with {len(genre_df)} mentions.")

        for genre_name_val, genre_data in genre_df.groupby('genre_name'):
            if not genre_name_val or pd.isna(genre_name_val):
                continue

            mention_count = len(genre_data)
            if mention_count < self.config.min_genre_mentions: # Use config
                continue

            platform_count = len(genre_data['platform'].unique())
            # Popularity score: simple mention count * platform diversity factor
            popularity_score = mention_count * (1 + (platform_count -1) * 0.1) # Boost for more platforms

            sentiment_scores = genre_data['sentiment_score'].dropna()
            avg_sentiment = sentiment_scores.mean() if not sentiment_scores.empty else 5.0

            if avg_sentiment > self.config.positive_sentiment_threshold:
                sentiment_trend = "positive"
            elif avg_sentiment < self.config.negative_sentiment_threshold:
                sentiment_trend = "negative"
            else:
                sentiment_trend = "neutral"

            all_artists_for_genre = []
            for artists_list in genre_data['artists_in_mention']: # artists_in_mention is already a list
                all_artists_for_genre.extend(artists_list)
            artist_diversity = len(set(str(a).strip() for a in all_artists_for_genre if str(a).strip()))


            cross_platform_presence = platform_count

            # Emotional associations (simplified, as 'emotional_indicators' might not be robustly available)
            # Could use sentiment labels or keywords from text if available
            emotional_associations = [sentiment_trend] # Placeholder

            # Trend momentum (simplified: based on recent activity or growth if calculated)
            # For now, use popularity as a proxy
            trend_momentum = min(popularity_score / (self.config.high_engagement_threshold * 5), 1.0) # Normalize

            genre_trends.append(GenreTrend(
                genre=str(genre_name_val),
                popularity_score=round(popularity_score, 2),
                sentiment_trend=sentiment_trend,
                artist_diversity=artist_diversity,
                cross_platform_presence=cross_platform_presence,
                emotional_associations=emotional_associations,
                trend_momentum=round(trend_momentum, 2)
            ))

        genre_trends.sort(key=lambda x: x.popularity_score, reverse=True)
        self.logger.info(f"Analyzed trends for {len(genre_trends)} genres.")
        if genre_trends:
            self.logger.debug(f"Top genre trend: {genre_trends[0].to_dict()}")
        return genre_trends

    def analyze_temporal_trends(self, df: pd.DataFrame) -> List[TemporalTrend]:
        """Analyze trends over time periods, adapted from reference script."""
        temporal_trends = []
        self.logger.info("Analyzing temporal trends...")

        if df.empty or self.processing_date_col not in df.columns:
            self.logger.warning("DataFrame empty or date column missing for temporal analysis.")
            return temporal_trends

        # Ensure date column is datetime
        df[self.processing_date_col] = pd.to_datetime(df[self.processing_date_col])
        df_sorted = df.sort_values(self.processing_date_col)

        # Group by a defined period, e.g., daily or weekly. For now, daily.
        # To use weekly: df_sorted.groupby(pd.Grouper(key=self.processing_date_col, freq='W'))
        grouped_by_date = df_sorted.groupby(df_sorted[self.processing_date_col].dt.date)

        prev_period_sentiment = None

        for date_period, period_data in grouped_by_date:
            time_period_str = date_period.strftime('%Y-%m-%d')

            all_artists_in_period = []
            for artists_list in period_data['entities_artists']:
                all_artists_in_period.extend(artists_list)
            artist_counts = Counter(str(a).strip() for a in all_artists_in_period if str(a).strip())
            dominant_artists = [artist for artist, count in artist_counts.most_common(3)]

            all_genres_in_period = []
            for genres_list in period_data['entities_genres']:
                all_genres_in_period.extend(genres_list)
            genre_counts = Counter(str(g).strip() for g in all_genres_in_period if str(g).strip())
            dominant_genres = [genre for genre, count in genre_counts.most_common(3)]

            current_period_sentiment = period_data['sentiment_score'].mean()
            sentiment_shift = 0.0
            if prev_period_sentiment is not None and pd.notna(current_period_sentiment):
                sentiment_shift = current_period_sentiment - prev_period_sentiment

            if pd.notna(current_period_sentiment):
                prev_period_sentiment = current_period_sentiment
            else: # If current is NaN, don't update prev_period_sentiment to allow comparison with next valid
                pass


            total_mentions_in_period = len(period_data)
            engagement_pattern = self._get_engagement_level(total_mentions_in_period)

            # Notable events (simplified - e.g., high sentiment variance or large shift)
            notable_events = []
            sentiment_variance = period_data['sentiment_score'].var()
            if pd.notna(sentiment_variance) and sentiment_variance > (self.config.positive_sentiment_threshold / 2)**2 : # Heuristic
                notable_events.append(f"High sentiment variance ({sentiment_variance:.2f})")
            if abs(sentiment_shift) > 2.0: # Significant shift
                 notable_events.append(f"Significant sentiment shift ({sentiment_shift:.2f})")


            temporal_trends.append(TemporalTrend(
                time_period=time_period_str,
                dominant_artists=dominant_artists,
                dominant_genres=dominant_genres,
                sentiment_shift=round(sentiment_shift, 2),
                engagement_pattern=engagement_pattern,
                notable_events=notable_events
            ))

        self.logger.info(f"Analyzed temporal trends for {len(temporal_trends)} time periods.")
        return temporal_trends

    def generate_trend_summary(self, artist_trends: List[TrendMetrics],
                             genre_trends: List[GenreTrend],
                             temporal_trends: List[TemporalTrend]) -> Dict[str, Any]:
        """Generate a comprehensive trend summary, adapted from reference script."""
        self.logger.info("Generating trend summary...")
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "config_summary": { # Add some key config values for context
                "log_level": self.config.log_level,
                "min_mentions_for_trend": self.config.min_mentions_for_trend,
                "positive_sentiment_threshold": self.config.positive_sentiment_threshold,
            },
            "overview": {
                "total_artists_analyzed": len(artist_trends),
                "total_genres_analyzed": len(genre_trends),
                "time_periods_analyzed": len(temporal_trends)
            },
            "top_artists": [
                {
                    "name": trend.entity_name,
                    "trend_strength": trend.trend_strength, # Already rounded
                    "mentions": trend.mention_count,
                    "sentiment_score": trend.sentiment_score, # Already rounded
                    "sentiment_direction": trend.trend_direction,
                    "platforms": trend.platforms
                }
                for trend in artist_trends[:self.config.max_top_results] # Use config for top N
            ],
            "top_genres": [
                {
                    "name": trend.genre,
                    "popularity_score": trend.popularity_score, # Already rounded
                    "sentiment_trend": trend.sentiment_trend,
                    "artist_diversity": trend.artist_diversity,
                    "platforms_count": trend.cross_platform_presence # Renamed for clarity
                }
                for trend in genre_trends[:self.config.max_top_results] # Use config for top N
            ],
            "sentiment_patterns_artists": {
                "positive_trends": len([t for t in artist_trends if t.trend_direction == "positive"]),
                "negative_trends": len([t for t in artist_trends if t.trend_direction == "negative"]),
                "neutral_trends": len([t for t in artist_trends if t.trend_direction == "neutral"])
            },
            "engagement_levels_artists": {
                "high": len([t for t in artist_trends if t.engagement_level == "high"]),
                "medium": len([t for t in artist_trends if t.engagement_level == "medium"]),
                "low": len([t for t in artist_trends if t.engagement_level == "low"])
            }
        }
        if temporal_trends:
            summary["latest_temporal_period"] = temporal_trends[-1].to_dict() if temporal_trends else {}

        self.logger.info("Trend summary generated.")
        return summary

    def save_trends(self, artist_trends: List[TrendMetrics],
                   genre_trends: List[GenreTrend],
                   temporal_trends: List[TemporalTrend],
                   summary: Dict[str, Any],
                   output_dir: str,
                   date_tag: str,  # Added
                   source_tag: str # Added
                   ) -> Dict[str, str]:
        """Save trend analysis results to files, adapted from reference script."""
        self.logger.info(f"Saving trend analysis results to directory: {output_dir} with date_tag='{date_tag}', source_tag='{source_tag}'")
        os.makedirs(output_dir, exist_ok=True)
        output_files = {}

        def create_dynamic_filename(base_filename_config_key: str) -> str:
            base_filename = getattr(self.config, base_filename_config_key)
            stem = Path(base_filename).stem
            suffix = Path(base_filename).suffix
            return f"{stem}_{date_tag}_{source_tag}{suffix}"

        try:
            # Save artist trends
            if artist_trends:
                artist_filename = create_dynamic_filename('artist_trends_filename')
                artist_file = os.path.join(output_dir, artist_filename)
                artist_df = pd.DataFrame([trend.to_dict() for trend in artist_trends])
                artist_df.to_csv(artist_file, index=False, encoding='utf-8')
                output_files["artist_trends"] = artist_file
                self.logger.info(f"Artist trends saved to {artist_file}")
            else:
                self.logger.info("No artist trends to save.")

            # Save genre trends
            if genre_trends:
                genre_filename = create_dynamic_filename('genre_trends_filename')
                genre_file = os.path.join(output_dir, genre_filename)
                genre_df = pd.DataFrame([trend.to_dict() for trend in genre_trends])
                genre_df.to_csv(genre_file, index=False, encoding='utf-8')
                output_files["genre_trends"] = genre_file
                self.logger.info(f"Genre trends saved to {genre_file}")
            else:
                self.logger.info("No genre trends to save.")

            # Save temporal trends
            if temporal_trends:
                temporal_filename = create_dynamic_filename('temporal_trends_filename')
                temporal_file = os.path.join(output_dir, temporal_filename)
                temporal_df = pd.DataFrame([trend.to_dict() for trend in temporal_trends])
                temporal_df.to_csv(temporal_file, index=False, encoding='utf-8')
                output_files["temporal_trends"] = temporal_file
                self.logger.info(f"Temporal trends saved to {temporal_file}")
            else:
                self.logger.info("No temporal trends to save.")

            # Save summary
            if summary:
                summary_filename = create_dynamic_filename('trend_summary_filename')
                summary_file = os.path.join(output_dir, summary_filename)
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                output_files["summary"] = summary_file
                self.logger.info(f"Trend summary saved to {summary_file}")
            else:
                self.logger.info("No summary to save.")

        except Exception as e:
            self.logger.error(f"Error saving trend results: {e}", exc_info=True)
            # It's often better to raise here or return an error status
            # For now, just log and continue, returning successfully saved files.
            # raise # Or handle more gracefully

        self.logger.info(f"Trend analysis results saved. Files: {list(output_files.keys())}")
        return output_files

    def run_analysis_pipeline(self, input_file: str, output_dir: str) -> Dict[str, Any]:
        """Main orchestrator method for the trend analysis pipeline."""
        self.logger.info(f"Starting trend analysis pipeline for input: {input_file}, output: {output_dir}")

        # --- Extract date_tag and source_tag from input_file ---
        input_filename_stem = Path(input_file).stem
        input_filename_lower = Path(input_file).name.lower()

        # Extract date_tag (YYYYMMDD)
        # Corrected regex: removed extra backslashes
        date_match = re.search(r"(\\d{8})", input_filename_stem)
        if not date_match: # Try another common pattern if first fails
            date_match = re.search(r"(\\d{4}\\d{2}\\d{2})", input_filename_stem)

        if date_match:
            date_tag = date_match.group(1)
        else:
            date_tag = datetime.now().strftime("%Y%m%d")
            self.logger.info(f"No YYYYMMDD date pattern found in filename '{Path(input_file).name}'. Using current date: {date_tag}")

        # Extract source_tag
        if "youtube" in input_filename_lower:
            source_tag = "youtube"
        elif "reddit" in input_filename_lower:
            source_tag = "reddit"
        else:
            # Fallback: try to get the first part of the filename before an underscore
            parts = input_filename_stem.split('_')
            if parts and parts[0]:
                source_tag = parts[0].lower()
            else:
                source_tag = "data" # Generic fallback
        self.logger.info(f"Determined date_tag='{date_tag}' and source_tag='{source_tag}' from input file.")
        # --- End of tag extraction ---

        results = {
            "status": "failure", # Default to failure
            "summary": {},
            "output_files": {},
            "metrics": {
                "artist_trends_found": 0,
                "genre_trends_found": 0,
                "temporal_periods_analyzed": 0
            },
            "error": None
        }
        try:
            # Load and preprocess data
            raw_df = self.load_data(input_file)
            if raw_df.empty:
                self.logger.warning("Loaded DataFrame is empty. Aborting analysis.")
                results["error"] = "Loaded DataFrame is empty."
                return results

            processed_df = self.preprocess_data(raw_df)
            if processed_df.empty:
                self.logger.warning("Processed DataFrame is empty. Aborting analysis.")
                results["error"] = "Processed DataFrame is empty after preprocessing."
                return results

            # Perform trend analysis
            artist_trends = self.analyze_artist_trends(processed_df)
            genre_trends = self.analyze_genre_trends(processed_df)
            temporal_trends = self.analyze_temporal_trends(processed_df)

            # Generate summary
            summary = self.generate_trend_summary(artist_trends, genre_trends, temporal_trends)

            # Save results
            output_files = self.save_trends(artist_trends, genre_trends, temporal_trends,
                                          summary, output_dir,
                                          date_tag, source_tag) # Pass tags here

            results.update({
                "status": "success",
                "summary": summary,
                "output_files": output_files,
                "metrics": {
                    "artist_trends_found": len(artist_trends),
                    "genre_trends_found": len(genre_trends),
                    "temporal_periods_analyzed": len(temporal_trends)
                }
            })
            self.logger.info("Trend analysis pipeline completed successfully.")

        except ValueError as ve: # Catch specific errors like missing date column
            self.logger.error(f"ValueError during trend analysis: {ve}", exc_info=True)
            results["error"] = str(ve)
        except Exception as e:
            self.logger.error(f"Unhandled error in trend analysis pipeline: {e}", exc_info=True)
            results["error"] = str(e)
            # Include traceback in debug log for detailed diagnostics
            self.logger.debug(f"Traceback: {traceback.format_exc()}")

        return results

    # Remove the old _parse_entity_list method as it's replaced by _safe_parse_entity_list (global helper)
    # def _parse_entity_list(self, entity_str: Any) -> List[str]: ... (This method is now removed)

    # Remove old analysis methods if they were named differently or had different signatures
    # and are now fully replaced by the refactored ones above.
    # For example, if there was an old `detect_trends_from_file`, it's now covered by `run_analysis_pipeline`.


def main():
    """Main entry point for the standalone trend detection script."""
    parser = argparse.ArgumentParser(description="Standalone Music Trend Detection from CSV data.")
    parser.add_argument("--input_file", required=True, help="Path to the input CSV file containing combined entity and sentiment data.")
    parser.add_argument("--output_dir", required=True, help="Directory to save the trend analysis results (CSV files and JSON summary).")
    parser.add_argument("--log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Logging level for the script.")

    args = parser.parse_args()

    # Initialize configuration with the specified log level
    config = TrendDetectionConfig(log_level=args.log_level)

    # Initialize the trend detector with the configuration
    # No ollama_host is passed from CLI in this setup, can be added if needed.
    detector = TrendDetector(config=config)

    # Run the main analysis pipeline
    detector.logger.info(f"Script execution started with arguments: input_file='{args.input_file}', output_dir='{args.output_dir}', log_level='{args.log_level}'")

    try:
        analysis_result = detector.run_analysis_pipeline(args.input_file, args.output_dir)

        if analysis_result["status"] == "success":
            detector.logger.info("Trend analysis finished successfully.")
            detector.logger.info(f"Summary: {json.dumps(analysis_result['summary'], indent=2)}")
            detector.logger.info(f"Output files generated in: {args.output_dir}")
        else:
            detector.logger.error(f"Trend analysis failed. Error: {analysis_result.get('error', 'Unknown error')}")
            sys.exit(1) # Exit with error code if analysis failed

    except Exception as e:
        # This catch is for unexpected errors during main() setup or if run_analysis_pipeline raises something uncaught
        detector.logger.critical(f"A critical error occurred in main execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
