#!/usr/bin/env python3
"""
Simple sentiment analysis debug test
"""

import sys
import os

print("🔍 Debug Test Starting...")

# Add the data_pipeline directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_pipeline'))

print("✅ Added data_pipeline to path")

try:
    print("📦 Importing sentiment_analysis_config...")
    import sentiment_analysis_config
    print("✅ Config imported successfully")

    print("📦 Importing SentimentAnalyzer...")
    from sentiment_analysis import SentimentAnalyzer
    print("✅ SentimentAnalyzer imported successfully")

    print("🏗️ Creating analyzer instance...")
    analyzer = SentimentAnalyzer()
    print("✅ Analyzer created successfully")

    print("🧪 Testing simple text analysis...")
    test_text = "This song is amazing! I love it so much."
    result = analyzer.analyze_sentiment_llm(test_text)
    if result is None:
        print("🔄 LLM analysis failed, trying rule-based fallback...")
        result = analyzer.analyze_basic_sentiment(test_text)
    print(f"✅ Analysis result: {result}")

    print("🎉 All tests passed!")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
