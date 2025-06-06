#!/usr/bin/env python3
"""
Standalone Combined Trend Detection Module

This module analyzes combined entity and sentiment data from multiple sources (e.g., YouTube and Reddit)
to identify music trends. It loads data from two specified input files, merges them,
and then performs trend analysis. Configuration is embedded.

Author: GitHub Copilot Assistant
Date: 2025-05-31
"""

import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter, defaultdict
import re
import sys
import os
import argparse
from pathlib import Path
import traceback
import ast

# --- Configuration Class (Embedded) ---
class TrendDetectionConfig:
    """Simple configuration class"""
    def __init__(self, log_level="INFO"):
        self.log_level = log_level
        self.min_mentions_for_trend = 2
        self.high_engagement_threshold = 3
        self.medium_engagement_threshold = 2
        self.positive_sentiment_threshold = 6.5
        self.negative_sentiment_threshold = 4.5
        self.mention_weight = 0.4
        self.sentiment_weight = 0.3
        self.consistency_weight = 0.3
        self.max_top_results = 10
        self.artist_trends_filename = "artist_trends.csv"
        self.genre_trends_filename = "genre_trends.csv"
        self.temporal_trends_filename = "temporal_trends.csv"
        self.trend_summary_filename = "trend_summary.json"
        self.min_artist_mentions = 1
        self.min_genre_mentions = 1

# --- Data Classes (Embedded) ---
class TrendMetrics:
    """Class for storing artist trend metrics"""
    def __init__(self, entity_type: str, entity_name: str, mention_count: int,
                 sentiment_score: float, sentiment_consistency: float, growth_rate: float,
                 engagement_level: str, trend_strength: float, trend_direction: str,
                 first_seen: str, last_seen: str, platforms: List[str],
                 peak_sentiment: float, sentiment_volatility: float):
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
        return self.__dict__

class GenreTrend:
    """Class for genre trends"""
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
        return self.__dict__

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
        return self.__dict__

# --- Helper Function for Parsing Entity Lists ---
def _safe_parse_entity_list(text: Any, logger: logging.Logger) -> List[str]:
    if pd.isna(text): return []
    if isinstance(text, list): return [str(item) for item in text if item is not None]
    if not isinstance(text, str):
        logger.debug(f"Input to _safe_parse_entity_list is not str/NaN: {type(text)}. Value: {text}")
        return []
    text_stripped = text.strip()
    if not text_stripped or text_stripped == '[]': return []
    try:
        if (text_stripped.startswith('[') and text_stripped.endswith(']')) or \
           (text_stripped.startswith('{') and text_stripped.endswith('}')):
            try:
                loaded_data = json.loads(text_stripped)
                return [str(item) for item in loaded_data if item is not None] if isinstance(loaded_data, list) else [str(loaded_data)]
            except json.JSONDecodeError:
                try:
                    processed_text = text_stripped.replace('\'', '"') # Handle single quotes in list-like strings
                    loaded_data = json.loads(processed_text)
                    return [str(item) for item in loaded_data if item is not None] if isinstance(loaded_data, list) else [str(loaded_data)]
                except json.JSONDecodeError:
                    logger.debug(f"JSON parsing failed for '{text_stripped}', trying eval.") # Fall through to eval
        # Try eval as a fallback (use with caution, consider ast.literal_eval if security is paramount)
        evaluated = eval(text_stripped)
        if isinstance(evaluated, list): return [str(item).strip() for item in evaluated if item and str(item).strip()]
        if isinstance(evaluated, set): return [str(item).strip() for item in list(evaluated) if item and str(item).strip()]
        if isinstance(evaluated, (str, int, float)): return [str(evaluated).strip()]
        logger.debug(f"Eval of '{text_stripped}' non-list/set/str: {type(evaluated)}. Trying split.")
    except (SyntaxError, ValueError, TypeError, NameError) as e_eval:
        logger.debug(f"Eval failed for '{text_stripped}': {e_eval}. Trying comma split.")
    if not (text_stripped.startswith('[') and text_stripped.endswith(']')) and ',' in text_stripped:
        return [item.strip() for item in text_stripped.split(',') if item.strip()]
    return [text_stripped] if text_stripped else [] # Single item or fallback

# --- TrendDetector Class ---
class TrendDetector:
    def __init__(self, config: Optional[TrendDetectionConfig] = None, ollama_host: Optional[str] = None):
        self.config = config or TrendDetectionConfig()
        self.ollama_host = ollama_host # Not used in this version
        self.logger = logging.getLogger(__name__)
        self.processing_date_col = 'source_date'
        self.setup_logging()

    def setup_logging(self):
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        log_level_to_set = getattr(logging, self.config.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level_to_set)
        self.logger.info(f"Logging initialized: level {self.config.log_level.upper()} ({log_level_to_set}).")

    def load_and_combine_data(self, file_path1: str, file_path2: str) -> pd.DataFrame:
        self.logger.info(f"Loading data from: {file_path1} and {file_path2}")
        try:
            df1 = pd.read_csv(file_path1)
            self.logger.info(f"Loaded {len(df1)} records from {file_path1}")
            df2 = pd.read_csv(file_path2)
            self.logger.info(f"Loaded {len(df2)} records from {file_path2}")

            # Add a source identifier before combining if not present
            # This helps in case 'source_platform' is missing or needs to be standardized
            # For simplicity, we assume 'source_platform' might exist or we derive it.
            # If 'source_platform' is reliably present and correct in both, this step can be simpler.

            filename1_lower = Path(file_path1).name.lower()
            if 'source_platform' not in df1.columns:
                 df1['source_platform'] = 'youtube' if 'youtube' in filename1_lower else ('reddit' if 'reddit' in filename1_lower else 'source1')

            filename2_lower = Path(file_path2).name.lower()
            if 'source_platform' not in df2.columns:
                df2['source_platform'] = 'youtube' if 'youtube' in filename2_lower else ('reddit' if 'reddit' in filename2_lower else 'source2')

            combined_df = pd.concat([df1, df2], ignore_index=True)
            self.logger.info(f"Combined data: {len(combined_df)} total records.")
            return combined_df
        except Exception as e:
            self.logger.error(f"Error loading or combining data: {e}", exc_info=True)
            raise

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocesses the combined data."""
        self.logger.info("Preprocessing combined data...")
        if df.empty:
            self.logger.warning("Input DataFrame is empty for combined preprocessing. Skipping.")
            return df

        # --- Date Column Selection and Processing ---
        # Standardize to 'processed_date' column for downstream use
        # Priority: 'created_at', then 'source_date', then 'date', then 'timestamp'
        date_col_candidates = ['created_at', 'source_date', 'date', 'timestamp', 'fetch_date', 'extraction_date']
        selected_date_col = None

        for col_candidate in date_col_candidates:
            if col_candidate in df.columns:
                try:
                    # Attempt to convert and check validity
                    temp_dates = pd.to_datetime(df[col_candidate], errors='coerce')
                    if temp_dates.notna().sum() > 0.5 * len(df): # Check if at least 50% are valid dates
                        selected_date_col = col_candidate
                        self.logger.info(f"Using '{selected_date_col}' as the primary date column for combined data.")
                        break
                    else:
                        self.logger.warning(f"Candidate date column '{col_candidate}' in combined data has too many invalid/missing values.")
                except Exception as e:
                    self.logger.warning(f"Error processing candidate date column '{col_candidate}' in combined data: {e}")

        if selected_date_col:
            df[self.processing_date_col] = pd.to_datetime(df[selected_date_col], errors='coerce')
            # If selected_date_col is different from self.processing_date_col and we want to keep only one, drop original
            # For now, we just ensure self.processing_date_col (default 'source_date') gets the valid dates.
            # If 'source_date' was not the selected_date_col, this effectively renames/copies it.
            # If 'source_date' was selected, it just converts it.
            if selected_date_col != self.processing_date_col and self.processing_date_col in df.columns:
                 # This case implies self.processing_date_col (e.g. 'source_date') was not chosen,
                 # but another candidate (e.g. 'created_at') was.
                 # We are assigning the chosen valid dates to the target `self.processing_date_col`.
                 pass # df[self.processing_date_col] is already assigned above.
            elif selected_date_col == self.processing_date_col:
                 pass # Already converted in place.


        else: # No suitable primary date column found from candidates
            self.logger.error("No suitable primary date column (created_at, source_date, etc.) found in combined data. Temporal analysis will be severely impacted or fail.")
            # Fallback: create a dummy date column with current date to prevent crashes, but log error.
            # This is a last resort. Downstream functions should handle NaT if this fails.
            df[self.processing_date_col] = pd.NaT # Assign NaT if no valid date column
            # Consider raising an error if a date column is absolutely critical:
            # raise ValueError("A usable date column is critical and was not found or was invalid.")

        # Drop rows where the final processing_date_col is NaT
        df.dropna(subset=[self.processing_date_col], inplace=True)
        if df.empty:
            self.logger.warning(f"DataFrame became empty after dropping rows with invalid dates in '{self.processing_date_col}'.")
            return df

        self.logger.info(f"Using '{self.processing_date_col}' for all date operations, populated from '{selected_date_col if selected_date_col else 'N/A'}'.")

        # Handle sentiment score: use 'sentiment_score', fallback to 'sentiment_strength', then to 0.0
        if 'sentiment_score' in df.columns:
            sentiment_series = df['sentiment_score']
        elif 'sentiment_strength' in df.columns:
            self.logger.info("Using 'sentiment_strength' as 'sentiment_score'.")
            sentiment_series = df['sentiment_strength']
        else:
            self.logger.warning("'sentiment_score' and 'sentiment_strength' not found. Defaulting to 0.0.")
            sentiment_series = pd.Series([0.0] * len(df), index=df.index, name='sentiment_score')

        df['sentiment_score'] = pd.to_numeric(sentiment_series, errors='coerce').fillna(0.0)
        df['sentiment_score'] = df['sentiment_score'].astype(float)

        # Normalize entity columns (artists, songs, genres)
        for col in ['entities_artists', 'entities_songs', 'entities_genres']:
            if col in df.columns:
                # Ensure the column is treated as string before attempting string operations
                df[col] = df[col].astype(str).fillna('')
                # Corrected line: Use the global _safe_parse_entity_list helper
                df[col] = df[col].apply(lambda x: _safe_parse_entity_list(x, self.logger))
            else:
                self.logger.warning(f"Entity column '{col}' not found. Proceeding without it.")
                df[col] = pd.Series([[] for _ in range(len(df))], index=df.index)

        self.logger.info(f"Combined data preprocessed. Shape: {df.shape}")
        return df

    def _get_engagement_level(self, mention_count: int) -> str:
        if mention_count >= self.config.high_engagement_threshold: return "high"
        if mention_count >= self.config.medium_engagement_threshold: return "medium"
        return "low"

    # --- Analysis Methods (analyze_artist_trends, analyze_genre_trends, analyze_temporal_trends) ---
    # These methods would be nearly identical to those in trend_detection_standalone.py
    # For brevity, their full implementation is omitted here but should be copied from
    # the refactored trend_detection_standalone.py.
    # Key is that they operate on the preprocessed combined DataFrame.

    def analyze_artist_trends(self, df: pd.DataFrame) -> List[TrendMetrics]:
        """Analyze trends for individual artists, adapted from reference script."""
        artist_trends = []
        self.logger.info("Analyzing artist trends on combined data...") # Modified log message

        # Flatten artist mentions
        artist_mentions_data = []
        for idx, row in df.iterrows():
            # entities_artists should be a list of strings after preprocessing
            for artist_name in row['entities_artists']:
                if not artist_name or pd.isna(artist_name): # Skip empty or NaN artist names
                    continue
                artist_mentions_data.append({
                    'artist_name': str(artist_name).strip(), # Ensure it's a clean string
                    # Corrected: Use self.processing_date_col as the key for the date
                    self.processing_date_col: row[self.processing_date_col],
                    'platform': row.get('source_platform', 'unknown'), # Use .get for safety
                    'sentiment_score': row.get('sentiment_score', 0.0), # Use .get for safety
                    'sentiment_confidence': row.get('sentiment_confidence_score', 0.5) # Use .get for safety
                })

        if not artist_mentions_data:
            self.logger.warning("No valid artist mentions found after flattening (combined data). Skipping artist trend analysis.")
            return artist_trends

        artist_df = pd.DataFrame(artist_mentions_data)
        if artist_df.empty:
            self.logger.warning("Artist DataFrame is empty after creation (combined data). Skipping artist trend analysis.")
            return artist_trends

        self.logger.debug(f"Generated artist_df with {len(artist_df)} mentions (combined data).")

        for artist_name_val, artist_data in artist_df.groupby('artist_name'):
            if not artist_name_val or pd.isna(artist_name_val):
                continue

            mention_count = len(artist_data)
            if mention_count < self.config.min_artist_mentions:
                continue

            sentiment_scores = artist_data['sentiment_score'].dropna()
            avg_sentiment = sentiment_scores.mean() if not sentiment_scores.empty else 5.0
            sentiment_consistency = (1.0 - (sentiment_scores.std() / 10.0)) if len(sentiment_scores) > 1 else 1.0
            sentiment_consistency = max(0.0, min(1.0, sentiment_consistency))

            # Corrected: Use self.processing_date_col to access the date series
            dates = artist_data[self.processing_date_col].sort_values()
            first_seen = dates.iloc[0] if not dates.empty else pd.NaT
            last_seen = dates.iloc[-1] if not dates.empty else pd.NaT

            growth_rate = 0.0
            if not dates.empty and len(dates) > 1 and pd.notna(first_seen) and pd.notna(last_seen):
                time_span_days = (last_seen - first_seen).days
                growth_rate = mention_count / max(time_span_days, 1)
            elif mention_count > 0 :
                growth_rate = float(mention_count)

            engagement_level = self._get_engagement_level(mention_count)

            norm_mention_strength = min(mention_count / (self.config.high_engagement_threshold * 2), 1.0)
            norm_sentiment_strength = avg_sentiment / 10.0

            trend_strength = (
                norm_mention_strength * self.config.mention_weight +
                norm_sentiment_strength * self.config.sentiment_weight +
                sentiment_consistency * self.config.consistency_weight
            )
            trend_strength = round(trend_strength, 3)

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
        self.logger.info(f"Analyzed trends for {len(artist_trends)} artists (combined data).")
        if artist_trends:
             self.logger.debug(f"Top artist trend (combined data): {artist_trends[0].to_dict()}")
        return artist_trends

    def analyze_genre_trends(self, df: pd.DataFrame) -> List[GenreTrend]:
        """Analyze trends for music genres, adapted from reference script."""
        genre_trends = []
        self.logger.info("Analyzing genre trends on combined data...") # Modified log message

        genre_mentions_data = []
        for idx, row in df.iterrows():
            for genre_name in row['entities_genres']:
                if not genre_name or pd.isna(genre_name):
                    continue
                genre_mentions_data.append({
                    'genre_name': str(genre_name).strip(),
                    # Corrected: Use self.processing_date_col as the key for the date
                    self.processing_date_col: row[self.processing_date_col],
                    'platform': row.get('source_platform', 'unknown'),
                    'sentiment_score': row.get('sentiment_score', 0.0),
                    'artists_in_mention': row['entities_artists']
                })

        if not genre_mentions_data:
            self.logger.warning("No valid genre mentions found (combined data). Skipping genre trend analysis.")
            return genre_trends

        genre_df = pd.DataFrame(genre_mentions_data)
        if genre_df.empty:
            self.logger.warning("Genre DataFrame is empty (combined data). Skipping genre trend analysis.")
            return genre_trends

        self.logger.debug(f"Generated genre_df with {len(genre_df)} mentions (combined data).")

        for genre_name_val, genre_data in genre_df.groupby('genre_name'):
            if not genre_name_val or pd.isna(genre_name_val):
                continue

            mention_count = len(genre_data)
            if mention_count < self.config.min_genre_mentions:
                continue

            platform_count = len(genre_data['platform'].unique())
            popularity_score = mention_count * (1 + (platform_count -1) * 0.1)

            sentiment_scores = genre_data['sentiment_score'].dropna()
            avg_sentiment = sentiment_scores.mean() if not sentiment_scores.empty else 5.0

            if avg_sentiment > self.config.positive_sentiment_threshold:
                sentiment_trend = "positive"
            elif avg_sentiment < self.config.negative_sentiment_threshold:
                sentiment_trend = "negative"
            else:
                sentiment_trend = "neutral"

            all_artists_for_genre = []
            for artists_list in genre_data['artists_in_mention']:
                all_artists_for_genre.extend(artists_list)
            artist_diversity = len(set(str(a).strip() for a in all_artists_for_genre if str(a).strip()))

            cross_platform_presence = platform_count
            emotional_associations = [sentiment_trend]
            trend_momentum = min(popularity_score / (self.config.high_engagement_threshold * 5), 1.0)

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
        self.logger.info(f"Analyzed trends for {len(genre_trends)} genres (combined data).")
        if genre_trends:
            self.logger.debug(f"Top genre trend (combined data): {genre_trends[0].to_dict()}")
        return genre_trends

    def analyze_temporal_trends(self, df: pd.DataFrame) -> List[TemporalTrend]:
        """Analyze trends over time periods, adapted from reference script."""
        temporal_trends = []
        self.logger.info("Analyzing temporal trends on combined data...") # Modified log message

        if df.empty or self.processing_date_col not in df.columns:
            self.logger.warning("DataFrame empty or date column missing for temporal analysis (combined data).")
            return temporal_trends

        df[self.processing_date_col] = pd.to_datetime(df[self.processing_date_col])
        df_sorted = df.sort_values(self.processing_date_col)

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

            total_mentions_in_period = len(period_data)
            engagement_pattern = self._get_engagement_level(total_mentions_in_period)

            notable_events = []
            sentiment_variance = period_data['sentiment_score'].var()
            if pd.notna(sentiment_variance) and sentiment_variance > (self.config.positive_sentiment_threshold / 2)**2 :
                notable_events.append(f"High sentiment variance ({sentiment_variance:.2f})")
            if abs(sentiment_shift) > 2.0:
                 notable_events.append(f"Significant sentiment shift ({sentiment_shift:.2f})")

            temporal_trends.append(TemporalTrend(
                time_period=time_period_str,
                dominant_artists=dominant_artists,
                dominant_genres=dominant_genres,
                sentiment_shift=round(sentiment_shift, 2),
                engagement_pattern=engagement_pattern,
                notable_events=notable_events
            ))

        self.logger.info(f"Analyzed temporal trends for {len(temporal_trends)} time periods (combined data).")
        return temporal_trends


    def generate_trend_summary(self, artist_trends: List[TrendMetrics],
                             genre_trends: List[GenreTrend],
                             temporal_trends: List[TemporalTrend]) -> Dict[str, Any]:
        """Generate a comprehensive trend summary, adapted from reference script."""
        self.logger.info("Generating trend summary for combined data...") # Modified log message
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "config_summary": {
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
                    "trend_strength": trend.trend_strength,
                    "mentions": trend.mention_count,
                    "sentiment_score": trend.sentiment_score,
                    "sentiment_direction": trend.trend_direction,
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
                    "platforms_count": trend.cross_platform_presence
                }
                for trend in genre_trends[:self.config.max_top_results]
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

        self.logger.info("Trend summary generated (combined data).")
        return summary

    def save_trends(self, artist_trends: List[TrendMetrics],
                   genre_trends: List[GenreTrend],
                   temporal_trends: List[TemporalTrend],
                   summary: Dict[str, Any],
                   output_dir: str,
                   date_tag: str,
                   source_tag: str # For combined, this might be "combined" or derived
                   ) -> Dict[str, str]:
        self.logger.info(f"Saving combined trend results to {output_dir} (date: {date_tag}, source: {source_tag})")
        os.makedirs(output_dir, exist_ok=True)
        output_files = {}

        def create_filename(base_cfg_key: str) -> str:
            base = getattr(self.config, base_cfg_key)
            return f"{Path(base).stem}_{date_tag}_{source_tag}{Path(base).suffix}"

        if artist_trends:
            fn = create_filename('artist_trends_filename')
            pd.DataFrame([t.to_dict() for t in artist_trends]).to_csv(os.path.join(output_dir, fn), index=False, encoding='utf-8')
            output_files["artist_trends"] = os.path.join(output_dir, fn)
        # ... (Save genre_trends, temporal_trends, summary similarly) ...
        if genre_trends:
            fn_genre = create_filename('genre_trends_filename')
            pd.DataFrame([t.to_dict() for t in genre_trends]).to_csv(os.path.join(output_dir, fn_genre), index=False, encoding='utf-8')
            output_files["genre_trends"] = os.path.join(output_dir, fn_genre)

        if temporal_trends:
            fn_temporal = create_filename('temporal_trends_filename')
            pd.DataFrame([t.to_dict() for t in temporal_trends]).to_csv(os.path.join(output_dir, fn_temporal), index=False, encoding='utf-8')
            output_files["temporal_trends"] = os.path.join(output_dir, fn_temporal)

        if summary:
            fn_summary = create_filename('trend_summary_filename')
            with open(os.path.join(output_dir, fn_summary), 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            output_files["summary"] = os.path.join(output_dir, fn_summary)

        self.logger.info(f"Saved combined trend files: {list(output_files.keys())}")
        return output_files

    def run_analysis_pipeline(self, input_file_youtube: str, input_file_reddit: str, output_dir: str) -> Dict[str, Any]:
        self.logger.info(f"Starting COMBINED trend analysis: YouTube='{input_file_youtube}', Reddit='{input_file_reddit}', Output='{output_dir}'")

        # Determine date_tag (e.g., from one of the files or current date)
        # For simplicity, using the date from the YouTube filename or current date
        date_match = re.search(r"(\d{8})", Path(input_file_youtube).stem)
        date_tag = date_match.group(1) if date_match else datetime.now().strftime("%Y%m%d")
        source_tag = "combined" # Specific tag for combined analysis outputs

        results = {"status": "failure", "error": None, "output_files": {}, "summary": {}, "metrics": {}}
        try:
            combined_df = self.load_and_combine_data(input_file_youtube, input_file_reddit)
            if combined_df.empty:
                results["error"] = "Combined DataFrame is empty after loading."; return results

            processed_df = self.preprocess_data(combined_df)
            if processed_df.empty:
                results["error"] = "Processed DataFrame is empty."; return results

            artist_trends = self.analyze_artist_trends(processed_df) # Assumed full implementation
            genre_trends = self.analyze_genre_trends(processed_df)   # Assumed full implementation
            temporal_trends = self.analyze_temporal_trends(processed_df) # Assumed full implementation

            summary = self.generate_trend_summary(artist_trends, genre_trends, temporal_trends) # Assumed

            output_files = self.save_trends(artist_trends, genre_trends, temporal_trends,
                                          summary, output_dir, date_tag, source_tag)
            results.update({
                "status": "success", "summary": summary, "output_files": output_files,
                "metrics": {
                    "artist_trends_found": len(artist_trends),
                    "genre_trends_found": len(genre_trends),
                    "temporal_periods_analyzed": len(temporal_trends)
                }
            })
            self.logger.info("Combined trend analysis pipeline completed successfully.")
        except ValueError as ve:
            self.logger.error(f"ValueError in combined pipeline: {ve}", exc_info=True)
            results["error"] = str(ve)
        except Exception as e:
            self.logger.error(f"Error in combined pipeline: {e}", exc_info=True)
            results["error"] = str(e)
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
        return results

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="Combined Music Trend Detection from YouTube and Reddit CSV data.")
    parser.add_argument("--input_file_youtube", required=True, help="Path to YouTube input CSV.")
    parser.add_argument("--input_file_reddit", required=True, help="Path to Reddit input CSV.")
    parser.add_argument("--output_dir", required=True, help="Directory for trend analysis results.")
    parser.add_argument("--log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Logging level.")

    args = parser.parse_args()

    config = TrendDetectionConfig(log_level=args.log_level)
    detector = TrendDetector(config=config)

    detector.logger.info(f"Executing combined script: YT='{args.input_file_youtube}', Reddit='{args.input_file_reddit}', Out='{args.output_dir}', Log='{args.log_level}'")

    try:
        analysis_result = detector.run_analysis_pipeline(args.input_file_youtube, args.input_file_reddit, args.output_dir)
        if analysis_result["status"] == "success":
            detector.logger.info("Combined trend analysis finished successfully.")
            # detector.logger.info(f"Summary: {json.dumps(analysis_result['summary'], indent=2)}") # Can be verbose
        else:
            detector.logger.error(f"Combined trend analysis failed. Error: {analysis_result.get('error', 'Unknown')}")
            sys.exit(1)
    except Exception as e:
        detector.logger.critical(f"Critical error in main (combined script): {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
