#!/usr/bin/env python3
"""
Configuration for Trend Detection Module

This module contains configuration classes and settings for the trend detection
component of the Japanese music social media analysis pipeline.

Author: GitHub Copilot Assistant
Date: 2025-01-07
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json
import os

@dataclass
class TrendDetectionConfig:
    """Configuration for trend detection analysis"""

    # Logging configuration
    log_level: str = "INFO"

    # Trend analysis thresholds
    min_mentions_for_trend: int = 2
    high_engagement_threshold: int = 3
    medium_engagement_threshold: int = 2

    # Sentiment analysis thresholds
    positive_sentiment_threshold: float = 6.5
    negative_sentiment_threshold: float = 4.5
    high_sentiment_variance_threshold: float = 5.0

    # Trend strength weights
    mention_weight: float = 0.4
    sentiment_weight: float = 0.3
    consistency_weight: float = 0.3

    # Temporal analysis settings
    max_time_periods: int = 30
    trend_window_days: int = 7

    # Output settings
    max_top_results: int = 10
    include_low_engagement: bool = True
    save_detailed_metrics: bool = True

    # Platform weights (for cross-platform analysis)
    platform_weights: Dict[str, float] = field(default_factory=lambda: {
        "youtube": 1.0,
        "twitter": 0.9,
        "reddit": 0.8,
        "instagram": 0.7,
        "tiktok": 0.6
    })

    # Entity analysis settings
    min_artist_mentions: int = 1
    min_genre_mentions: int = 1
    max_artists_per_trend: int = 5
    max_genres_per_trend: int = 3

    # Growth rate calculation settings
    growth_rate_normalization: float = 5.0
    min_time_span_days: int = 1

    # Sentiment consistency settings
    sentiment_std_normalization: float = 10.0
    min_consistency_score: float = 0.0
    max_consistency_score: float = 1.0

    # Popularity score settings
    popularity_base_multiplier: float = 1.0
    cross_platform_bonus: float = 1.5

    # Emotional indicator settings
    max_emotional_associations: int = 3
    min_emotion_frequency: int = 1

    # File output settings
    output_encoding: str = "utf-8"
    csv_separator: str = ","
    json_indent: int = 2

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TrendDetectionConfig':
        """Create configuration from dictionary"""
        return cls(**config_dict)

    @classmethod
    def from_file(cls, file_path: str) -> 'TrendDetectionConfig':
        """Load configuration from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "log_level": self.log_level,
            "min_mentions_for_trend": self.min_mentions_for_trend,
            "high_engagement_threshold": self.high_engagement_threshold,
            "medium_engagement_threshold": self.medium_engagement_threshold,
            "positive_sentiment_threshold": self.positive_sentiment_threshold,
            "negative_sentiment_threshold": self.negative_sentiment_threshold,
            "high_sentiment_variance_threshold": self.high_sentiment_variance_threshold,
            "mention_weight": self.mention_weight,
            "sentiment_weight": self.sentiment_weight,
            "consistency_weight": self.consistency_weight,
            "max_time_periods": self.max_time_periods,
            "trend_window_days": self.trend_window_days,
            "max_top_results": self.max_top_results,
            "include_low_engagement": self.include_low_engagement,
            "save_detailed_metrics": self.save_detailed_metrics,
            "platform_weights": self.platform_weights,
            "min_artist_mentions": self.min_artist_mentions,
            "min_genre_mentions": self.min_genre_mentions,
            "max_artists_per_trend": self.max_artists_per_trend,
            "max_genres_per_trend": self.max_genres_per_trend,
            "growth_rate_normalization": self.growth_rate_normalization,
            "min_time_span_days": self.min_time_span_days,
            "sentiment_std_normalization": self.sentiment_std_normalization,
            "min_consistency_score": self.min_consistency_score,
            "max_consistency_score": self.max_consistency_score,
            "popularity_base_multiplier": self.popularity_base_multiplier,
            "cross_platform_bonus": self.cross_platform_bonus,
            "max_emotional_associations": self.max_emotional_associations,
            "min_emotion_frequency": self.min_emotion_frequency,
            "output_encoding": self.output_encoding,
            "csv_separator": self.csv_separator,
            "json_indent": self.json_indent
        }

    def save_to_file(self, file_path: str):
        """Save configuration to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=self.json_indent)

    def validate(self) -> List[str]:
        """Validate configuration settings and return list of issues"""
        issues = []

        # Check thresholds
        if self.min_mentions_for_trend < 1:
            issues.append("min_mentions_for_trend must be at least 1")

        if self.high_engagement_threshold <= self.medium_engagement_threshold:
            issues.append("high_engagement_threshold must be greater than medium_engagement_threshold")

        if self.positive_sentiment_threshold <= self.negative_sentiment_threshold:
            issues.append("positive_sentiment_threshold must be greater than negative_sentiment_threshold")

        # Check weights sum to 1.0
        weight_sum = self.mention_weight + self.sentiment_weight + self.consistency_weight
        if abs(weight_sum - 1.0) > 0.001:
            issues.append(f"Trend strength weights must sum to 1.0, got {weight_sum}")

        # Check platform weights
        for platform, weight in self.platform_weights.items():
            if weight < 0 or weight > 1:
                issues.append(f"Platform weight for {platform} must be between 0 and 1, got {weight}")

        # Check consistency score bounds
        if self.min_consistency_score < 0 or self.max_consistency_score > 1:
            issues.append("Consistency score bounds must be between 0 and 1")

        if self.min_consistency_score >= self.max_consistency_score:
            issues.append("min_consistency_score must be less than max_consistency_score")

        return issues

# Default configurations for different use cases
DEVELOPMENT_CONFIG = TrendDetectionConfig(
    log_level="DEBUG",
    min_mentions_for_trend=1,
    high_engagement_threshold=2,
    medium_engagement_threshold=1,
    max_top_results=5,
    include_low_engagement=True
)

PRODUCTION_CONFIG = TrendDetectionConfig(
    log_level="INFO",
    min_mentions_for_trend=3,
    high_engagement_threshold=5,
    medium_engagement_threshold=3,
    max_top_results=10,
    include_low_engagement=False,
    save_detailed_metrics=True
)

RESEARCH_CONFIG = TrendDetectionConfig(
    log_level="DEBUG",
    min_mentions_for_trend=1,
    high_engagement_threshold=3,
    medium_engagement_threshold=2,
    max_top_results=20,
    include_low_engagement=True,
    save_detailed_metrics=True,
    max_time_periods=100
)

def get_config(config_type: str = "default") -> TrendDetectionConfig:
    """Get configuration by type"""
    configs = {
        "default": TrendDetectionConfig(),
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "research": RESEARCH_CONFIG
    }

    return configs.get(config_type, TrendDetectionConfig())

def main():
    """Example usage and configuration validation"""
    # Test default configuration
    config = TrendDetectionConfig()
    issues = config.validate()

    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration is valid")

    # Save example configuration
    config.save_to_file("trend_detection_config_example.json")
    print("📁 Example configuration saved to trend_detection_config_example.json")

    # Test different configuration types
    for config_type in ["default", "development", "production", "research"]:
        config = get_config(config_type)
        issues = config.validate()
        status = "✅" if not issues else "❌"
        print(f"{status} {config_type.capitalize()} config: {len(issues)} issues")

if __name__ == "__main__":
    main()
