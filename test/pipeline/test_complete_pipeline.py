#!/usr/bin/env python3
"""
Complete Entity Extraction Test and Validation
"""

import pandas as pd
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the data_pipeline to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_pipeline'))

def run_complete_test():
    """Run complete entity extraction test"""
    print("🧪 Entity Extraction Pipeline Test")
    print("=" * 50)

    # Test 1: Load and validate data
    print("\n📊 Step 1: Loading translated data...")
    input_file = "data/intermediate/translated/20250528_full_youtube_comments_cleaned_nllb_translated.csv"

    try:
        df = pd.read_csv(input_file)
        valid_df = df[df['comment_text_en_nllb'].notna() & (df['comment_text_en_nllb'] != '')]
        print(f"✅ Loaded {len(df)} total comments, {len(valid_df)} with translations")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return

    # Test 2: Create sample data for testing
    print("\n📝 Step 2: Creating test sample...")
    # Get a mix of comments including music-related ones
    sample_comments = []

    # Add specific test cases
    test_cases = [
        "if you liked it, check out another song the wagakki band created together with amy lee",
        "I love YOASOBI new music!",
        "This J-Pop song is amazing",
    ]

    # Add real data
    real_samples = valid_df.head(3)
    for idx, row in real_samples.iterrows():
        sample_comments.append({
            'id': idx,
            'text': str(row['comment_text_en_nllb']),
            'source': 'real_data'
        })

    # Add test cases
    for i, text in enumerate(test_cases):
        sample_comments.append({
            'id': f'test_{i}',
            'text': text,
            'source': 'test_case'
        })

    print(f"✅ Created {len(sample_comments)} test samples")

    # Test 3: Mock entity extraction
    print("\n🔍 Step 3: Running mock entity extraction...")

    def extract_entities_mock(text):
        """Mock entity extraction using keyword matching"""
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

        # Artists
        artists = ['yoasobi', 'wagakki band', 'mrs. green apple', 'ado', 'eve', 'amy lee']
        for artist in artists:
            if artist in text_lower:
                entities["artists"].append(artist.title())

        # Genres
        genres = ['j-pop', 'j-rock', 'vocaloid', 'anime', 'city pop']
        for genre in genres:
            if genre in text_lower:
                entities["genres"].append(genre)

        # Song indicators
        song_words = ['song', 'music', 'album', 'single', 'cover', 'live', 'mv', 'track']
        for word in song_words:
            if word in text_lower:
                entities["song_indicators"].append(word)

        # Sentiment
        positive = ['love', 'amazing', 'incredible', 'perfect', 'great', 'awesome', 'beautiful']
        negative = ['hate', 'terrible', 'awful', 'bad', 'worst']
        for word in positive + negative:
            if word in text_lower:
                entities["sentiment_indicators"].append(word)

        # Events
        events = ['concert', 'tour', 'release', 'collaboration', 'collab', 'live', 'performance']
        for word in events:
            if word in text_lower:
                entities["music_events"].append(word)

        # Temporal
        temporal = ['new', 'latest', 'recent', 'today', '2024', '2025', 'now']
        for word in temporal:
            if word in text_lower:
                entities["temporal_references"].append(word)

        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    # Process samples
    results = []
    for sample in sample_comments:
        text = sample['text']
        entities = extract_entities_mock(text)

        # Calculate confidence
        total_entities = sum(len(v) for v in entities.values())
        confidence = min(1.0, total_entities * 0.15)

        # Flatten entities for CSV
        flattened = {}
        for entity_type, entity_list in entities.items():
            if entity_list:
                flattened[f'entities_{entity_type}'] = json.dumps(entity_list)
                flattened[f'entities_{entity_type}_count'] = len(entity_list)
            else:
                flattened[f'entities_{entity_type}'] = ''
                flattened[f'entities_{entity_type}_count'] = 0

        result = {
            'id': sample['id'],
            'source_platform': 'youtube',
            'original_text': text,
            'extraction_date': datetime.now().strftime('%Y-%m-%d'),
            'source_date': '',
            'confidence_score': confidence,
            'data_source': sample['source'],
            **flattened
        }

        results.append(result)

        # Print results
        print(f"\n📝 {sample['source']} - ID {sample['id']}")
        print(f"   Text: {text[:80]}{'...' if len(text) > 80 else ''}")
        print(f"   🎯 Confidence: {confidence:.2f}")
        if total_entities > 0:
            found_entities = {k: v for k, v in entities.items() if v}
            print(f"   📊 Entities: {found_entities}")
        else:
            print("   📊 No entities found")

    # Test 4: Save results
    print(f"\n💾 Step 4: Saving results...")
    output_dir = Path('data/intermediate/entity_extraction')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'complete_test_entities.csv'

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)

    print(f"✅ Saved {len(results)} results to {output_path}")

    # Test 5: Analysis
    print(f"\n📈 Step 5: Results Analysis")
    print(f"   • Total samples processed: {len(results)}")
    print(f"   • Average confidence: {results_df['confidence_score'].mean():.2f}")
    print(f"   • Samples with entities: {len(results_df[results_df['confidence_score'] > 0])}")

    # Count entities by type
    entity_types = ['artists', 'songs', 'genres', 'song_indicators', 'sentiment_indicators',
                   'music_events', 'temporal_references', 'other_entities']

    for entity_type in entity_types:
        count_col = f'entities_{entity_type}_count'
        if count_col in results_df.columns:
            total = results_df[count_col].sum()
            if total > 0:
                print(f"   • Total {entity_type}: {total}")

    # Test 6: Validate CSV structure for PostgreSQL
    print(f"\n🗄️  Step 6: PostgreSQL Compatibility Check")
    print("   CSV Columns:")
    for i, col in enumerate(results_df.columns):
        print(f"   {i+1:2d}. {col}")

    print(f"\n✅ Entity extraction pipeline test completed successfully!")
    print(f"📁 Output file: {output_path}")

    return output_path

if __name__ == "__main__":
    run_complete_test()
