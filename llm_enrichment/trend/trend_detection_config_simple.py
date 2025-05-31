#!/usr/bin/env python3
"""
Simplified Trend Detection Configuration for Testing

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

    # Basic configuration
    log_level: str = "INFO"
    min_mentions_for_trend: int = 2
    high_engagement_threshold: int = 3
    medium_engagement_threshold: int = 2
    positive_sentiment_threshold: float = 6.5
    negative_sentiment_threshold: float = 4.5

    # Weights
    mention_weight: float = 0.4
    sentiment_weight: float = 0.3
    consistency_weight: float = 0.3

    # Output settings
    max_top_results: int = 10
    include_low_engagement: bool = True

    # Platform weights (simplified)
    platform_weights: Dict[str, float] = field(default_factory=lambda: {
        "youtube": 1.0,
        "twitter": 0.9,
        "reddit": 0.8
    })

    def validate(self) -> List[str]:
        """Validate configuration settings"""
        issues = []

        # Check basic thresholds
        if self.min_mentions_for_trend < 1:
            issues.append("min_mentions_for_trend must be at least 1")

        if self.high_engagement_threshold <= self.medium_engagement_threshold:
            issues.append("high_engagement_threshold must be greater than medium_engagement_threshold")

        # Check weights sum
        weight_sum = self.mention_weight + self.sentiment_weight + self.consistency_weight
        if abs(weight_sum - 1.0) > 0.001:
            issues.append(f"Weights must sum to 1.0, got {weight_sum}")

        return issues

# Test configuration instances
DEVELOPMENT_CONFIG = TrendDetectionConfig(
    log_level="DEBUG",
    min_mentions_for_trend=1,
    high_engagement_threshold=2,
    medium_engagement_threshold=1
)

def get_config(config_type: str = "default") -> TrendDetectionConfig:
    """Get configuration by type"""
    if config_type == "development":
        return DEVELOPMENT_CONFIG
    return TrendDetectionConfig()

def main():
    """Test the configuration"""
    print("Testing simplified config...")
    config = TrendDetectionConfig()
    issues = config.validate()

    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration is valid")

if __name__ == "__main__":
    main()
