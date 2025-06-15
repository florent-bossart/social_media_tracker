#!/usr/bin/env python3
"""
Basic Trend Detection Configuration

Author: GitHub Copilot Assistant
Date: 2025-01-07
"""

class TrendDetectionConfig:
    """Configuration for trend detection analysis"""

    def __init__(self):
        # Basic configuration
        self.log_level = "INFO"
        self.min_mentions_for_trend = 2
        self.high_engagement_threshold = 3
        self.medium_engagement_threshold = 2
        self.positive_sentiment_threshold = 6.5
        self.negative_sentiment_threshold = 4.5

        # Weights
        self.mention_weight = 0.4
        self.sentiment_weight = 0.3
        self.consistency_weight = 0.3

        # Output settings
        self.max_top_results = 10
        self.include_low_engagement = True

        # Platform weights
        self.platform_weights = {
            "youtube": 1.0,
            "twitter": 0.9,
            "reddit": 0.8
        }

    def validate(self):
        """Validate configuration settings"""
        issues = []

        if self.min_mentions_for_trend < 1:
            issues.append("min_mentions_for_trend must be at least 1")

        if self.high_engagement_threshold <= self.medium_engagement_threshold:
            issues.append("high_engagement_threshold must be greater than medium_engagement_threshold")

        weight_sum = self.mention_weight + self.sentiment_weight + self.consistency_weight
        if abs(weight_sum - 1.0) > 0.001:
            issues.append(f"Weights must sum to 1.0, got {weight_sum}")

        return issues

def get_config(config_type="default"):
    """Get configuration by type"""
    return TrendDetectionConfig()

# Test if we run directly
if __name__ == "__main__":
    print("Testing basic config...")
    config = TrendDetectionConfig()
    issues = config.validate()

    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration is valid")

    print(f"Config created: log_level={config.log_level}")
