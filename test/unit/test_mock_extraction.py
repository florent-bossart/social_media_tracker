#!/usr/bin/env python3
"""
Mock entity extraction for fast testing and validation
"""

import pandas as pd
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add data_pipeline to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_pipeline'))

from data_pipeline.entity_extraction_config import OUTPUT_PATH_ENTITIES

class MockEntityExtractor:
    """Mock extractor for testing pipeline without slow LLM calls"""

    def __init__(self):
        pass

    def extract_entities_from_text(self, text: str, platform: str) -> dict:
        """Mock entity extraction based on simple keyword matching"""
        entities = {
            "artists": [],
            "songs": [],
            "genres": [],
            "song_indicators": [],
            "sentiment_indicators": [],
            "music_events": [],
            "temporal_references": [],
            "other_entities": []
        }

        text_lower = text.lower()

        # Simple keyword matching for demonstration
        known_artists = ['yoasobi', 'wagakki band', 'mrs. green apple', 'ado', 'eve']
        genres = ['j-pop', 'j-rock', 'vocaloid', 'anime']
        song_words = ['song', 'music', 'album', 'single', 'cover', 'live', 'mv']
        sentiment_words = ['love', 'amazing', 'incredible', 'perfect', 'great', 'awesome', 'bad', 'terrible']
        events = ['concert', 'tour', 'release', 'collaboration', 'collab']
        temporal = ['new', 'latest', 'recent', 'today', '2024', '2025']

        for artist in known_artists:
            if artist in text_lower:
                entities["artists"].append(artist.title())

        for genre in genres:
            if genre in text_lower:
                entities["genres"].append(genre)

        for word in song_words:
            if word in text_lower:
                entities["song_indicators"].append(word)

        for word in sentiment_words:
            if word in text_lower:
                entities["sentiment_indicators"].append(word)

        for word in events:
            if word in text_lower:
                entities["music_events"].append(word)

        for word in temporal:
            if word in text_lower:
                entities["temporal_references"].append(word)

        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def calculate_confidence(self, entities: dict, text: str) -> float:
        """Calculate mock confidence based on number of entities found"""
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        return min(1.0, total_entities * 0.2)  # Max 1.0 confidence

    def _flatten_entities(self, entities: dict) -> dict:
        """Flatten entities for CSV storage"""
        flattened = {}

        for entity_type, entity_list in entities.items():
            if entity_list:
                flattened[f'entities_{entity_type}'] = json.dumps(entity_list)
                flattened[f'entities_{entity_type}_count'] = len(entity_list)
            else:
                flattened[f'entities_{entity_type}'] = ''
                flattened[f'entities_{entity_type}_count'] = 0

        return flattened

    def save_results(self, results: list, output_path: str):
        """Save extraction results to CSV"""
        if not results:
            print("⚠️  No results to save")
            return

        df = pd.DataFrame(results)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"💾 Saved {len(results)} entity extractions to {output_path}")

def test_mock_extraction():
    """Test the mock extraction on sample data"""
    print("🧪 Testing Mock Entity Extraction Pipeline")
    print("=" * 50)

    # Load sample data
    input_file = "data/intermediate/translated/20250528_full_youtube_comments_cleaned_nllb_translated.csv"

    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    valid_df = df[df['comment_text_en_nllb'].notna() & (df['comment_text_en_nllb'] != '')]
    sample_df = valid_df.head(10).copy()

    print(f"📊 Processing {len(sample_df)} sample comments")

    extractor = MockEntityExtractor()
    results = []

    for idx, row in sample_df.iterrows():
        text = str(row['comment_text_en_nllb'])
        entities = extractor.extract_entities_from_text(text, "youtube")
        confidence = extractor.calculate_confidence(entities, text)

        result = {
            'id': idx,
            'source_platform': 'youtube',
            'original_text': text,
            'extraction_date': datetime.now().strftime('%Y-%m-%d'),
            'source_date': row.get('comment_published_at', ''),
            'confidence_score': confidence,
            **extractor._flatten_entities(entities)
        }

        results.append(result)

        print(f"📝 Comment {idx}: {text[:80]}{'...' if len(text) > 80 else ''}")
        print(f"   🎯 Confidence: {confidence:.2f}")
        if any(entities.values()):
            print("   📊 Entities:", {k: v for k, v in entities.items() if v})
        print()

    # Save results
    output_path = "data/intermediate/entity_extraction/mock_test_entities.csv"
    extractor.save_results(results, output_path)

    # Show summary
    results_df = pd.DataFrame(results)
    print("\n📈 Summary:")
    print(f"   • Total comments: {len(results)}")
    print(f"   • Average confidence: {results_df['confidence_score'].mean():.2f}")

    # Count entities by type
    entity_columns = [col for col in results_df.columns if col.endswith('_count')]
    for col in entity_columns:
        entity_type = col.replace('entities_', '').replace('_count', '')
        total = results_df[col].sum()
        if total > 0:
            print(f"   • Total {entity_type}: {total}")

if __name__ == "__main__":
    test_mock_extraction()
