#!/usr/bin/env python3
"""
Test entity extraction with music-specific comments
"""

import pandas as pd
import sys
import os
import time
from pathlib import Path

# Add data_pipeline to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_pipeline'))

from data_pipeline.entity_extraction import EntityExtractor

def test_music_comments():
    """Test entity extraction on music-specific comments"""
    print("🎵 Testing Entity Extraction with Music Comments")
    print("=" * 50)

    # Create test comments with known music content
    test_comments = [
        "I love YOASOBI's new song! It's amazing.",
        "Wagakki Band collaboration with Amy Lee is incredible!",
        "Mrs. Green Apple latest album is perfect J-Pop.",
    ]

    extractor = EntityExtractor()

    for i, comment in enumerate(test_comments):
        print(f"\n📝 Test {i+1}: {comment}")
        print("-" * 40)

        start_time = time.time()
        entities = extractor.extract_entities_from_text(comment, "test")
        elapsed = time.time() - start_time
        confidence = extractor.calculate_confidence(entities, comment)

        print(f"⏱️  Extraction took {elapsed:.1f}s")
        print(f"🎯 Confidence: {confidence:.2f}")
        print("📊 Extracted entities:")
        for entity_type, entity_list in entities.items():
            if entity_list:
                print(f"   • {entity_type}: {entity_list}")

        if not any(entities.values()):
            print("   ⚠️  No entities extracted")

if __name__ == "__main__":
    test_music_comments()
