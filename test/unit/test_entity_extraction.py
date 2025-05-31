#!/usr/bin/env python3
"""
Test script for entity extraction module
"""

import pandas as pd
import sys
import os
import time
from pathlib import Path

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

from llm_enrichment.entity.entity_extraction import EntityExtractor
from llm_enrichment.entity.entity_extraction_config import OUTPUT_PATH_ENTITIES

def test_entity_extraction_small_sample():
    """Test entity extraction on a small sample of data"""
    print("🧪 Testing Entity Extraction Module")
    print("=" * 50)

    try:
        # Use the existing translated YouTube data
        input_file = "data/intermediate/translated/20250528_full_youtube_comments_cleaned_nllb_translated.csv"

        if not Path(input_file).exists():
            print(f"❌ Input file not found: {input_file}")
            return

        # Load the data
        print(f"📁 Loading data from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"📁 Loaded {len(df)} comments from {input_file}")

        # Filter to rows with valid translated text
        valid_df = df[df['comment_text_en_nllb'].notna() & (df['comment_text_en_nllb'] != '')]
        print(f"📊 Found {len(valid_df)} comments with translations")

        if len(valid_df) == 0:
            print("❌ No translated comments found. Using original comments instead...")
            valid_df = df[df['comment_text'].notna() & (df['comment_text'] != '')]
            print(f"📊 Using {len(valid_df)} original comments")

        # Filter to shorter comments for faster testing (< 100 characters)
        short_comments = valid_df[valid_df['comment_text_en_nllb'].str.len() < 100]
        if len(short_comments) > 0:
            sample_df = short_comments.head(2).copy()
            print(f"📊 Using {len(sample_df)} short comments for faster testing")
        else:
            sample_df = valid_df.head(2).copy()
            print(f"📊 Using {len(sample_df)} regular comments")

        # Initialize extractor
        print("🔧 Initializing EntityExtractor...")
        extractor = EntityExtractor()

        print("\n🔍 Processing sample comments:")
        print("-" * 40)        # Process each comment individually for testing
        results = []
        for idx, row in sample_df.iterrows():
            # Try translated text first, then original text
            text = row.get('comment_text_en_nllb', '')
            if pd.isna(text) or not text or str(text).strip() == "":
                text = row.get('comment_text', '')

            # Handle NaN values
            if pd.isna(text) or not text or str(text).strip() == "":
                print(f"⚠️  Row {idx}: No text found")
                continue

            text = str(text)  # Ensure it's a string
            print(f"\n📝 Comment {idx}: {text[:100]}{'...' if len(text) > 100 else ''}")

            # Extract entities with timing
            print("⏱️  Extracting entities...")
            start_time = time.time()
            entities = extractor.extract_entities_from_text(text, "youtube")
            elapsed = time.time() - start_time
            confidence = extractor.calculate_confidence(entities, text)

            print(f"⏱️  Extraction took {elapsed:.1f}s")
            print(f"🎯 Confidence: {confidence:.2f}")
            print("📊 Extracted entities:")
            for entity_type, entity_list in entities.items():
                if entity_list:
                    print(f"   • {entity_type}: {entity_list}")

            # Store result
            result = {
                'id': idx,
                'source_platform': 'youtube',
                'original_text': text,
                'extraction_date': '2025-05-29',
                'confidence_score': confidence,
                **extractor._flatten_entities(entities)
            }
            results.append(result)

        # Save results
        test_output_path = "data/intermediate/entity_extraction/test_entities.csv"
        extractor.save_results(results, test_output_path)

        print(f"\n✅ Test completed! Results saved to: {test_output_path}")
        print(f"📊 Processed {len(results)} comments successfully")

        # Show summary
        if results:
            results_df = pd.DataFrame(results)
            print("\n📈 Summary:")
            print(f"   • Average confidence: {results_df['confidence_score'].mean():.2f}")

            # Count non-empty entity types
            entity_columns = [col for col in results_df.columns if col.startswith('entities_') and col.endswith('_count')]
            for col in entity_columns:
                entity_type = col.replace('entities_', '').replace('_count', '')
                total_entities = results_df[col].sum()
                if total_entities > 0:
                    print(f"   • Total {entity_type}: {total_entities}")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_entity_extraction_small_sample()
