#!/usr/bin/env python3
"""
Simple verification script to test the config refactoring.
"""

import sys
import os

# Add the api directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import (
        SUBREDDIT_KEYWORDS,
        SEARCH_KEYWORDS,
        get_keyword_counts,
        get_subreddit_keywords,
        get_search_keywords
    )

    print("✅ CONFIG REFACTORING VERIFICATION")
    print("=" * 40)

    # Test direct imports
    print(f"📊 Subreddit keywords loaded: {len(SUBREDDIT_KEYWORDS)}")
    print(f"🔍 Search keywords loaded: {len(SEARCH_KEYWORDS)}")

    # Test utility functions
    counts = get_keyword_counts()
    print(f"📈 Total keywords managed: {counts['total_keywords']}")

    # Sample content
    print("\n📋 Sample Configuration:")
    print(f"  Subreddits: {', '.join(SUBREDDIT_KEYWORDS[:5])}...")
    print(f"  Search terms: {', '.join(SEARCH_KEYWORDS[:3])}...")

    # Test getter functions
    sub_list = get_subreddit_keywords()
    search_list = get_search_keywords()
    print(f"\n🔧 Utility functions working: {len(sub_list)} + {len(search_list)} keywords accessible")

    print("\n✅ All tests passed! Configuration successfully refactored.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
