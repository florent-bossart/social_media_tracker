#!/usr/bin/env python3
"""
Test the corrected database integration
"""

import os
import sys
sys.path.insert(0, '/home/florent.bossart/code/florent-bossart/social_media_tracker')

# Set environment
os.environ.update({
    'WAREHOUSE_HOST': 'localhost',
    'WAREHOUSE_PORT': '5434',
    'WAREHOUSE_DB': 'social_db',
    'WAREHOUSE_USER': 'dbt',
    'WAREHOUSE_PASSWORD': 'bossart'
})

try:
    from data_pipeline.database_integration import PipelineDBIntegrator

    print("🔧 Testing corrected database integration...")
    integrator = PipelineDBIntegrator()

    # Clear previous data
    print("🧹 Clearing previous data...")
    with integrator.engine.begin() as conn:
        for table in ['entity_extraction', 'sentiment_analysis', 'trend_analysis',
                      'summarization_metrics', 'summarization_insights']:
            conn.execute(integrator.metadata.bind.text(f'TRUNCATE TABLE analytics.{table} CASCADE;'))

    print("✅ Tables cleared")

    # Test individual imports
    print("\n📊 Testing individual imports...")

    # Entity extraction
    result = integrator.import_entity_extraction('data/intermediate/entity_extraction/quick_test_entities.csv')
    print(f"Entity extraction: {'✅' if result.success else '❌'} {result.records_imported} records")
    if not result.success:
        print(f"   Error: {result.error_message[:80]}...")

    # Sentiment analysis
    result = integrator.import_sentiment_analysis('data/intermediate/sentiment_analysis/entity_sentiment_combined.csv')
    print(f"Sentiment analysis: {'✅' if result.success else '❌'} {result.records_imported} records")
    if not result.success:
        print(f"   Error: {result.error_message[:80]}...")

    # Trend analysis
    result = integrator.import_trend_analysis('data/intermediate/trend_analysis/artist_trends.csv')
    print(f"Trend analysis: {'✅' if result.success else '❌'} {result.records_imported} records")
    if not result.success:
        print(f"   Error: {result.error_message[:80]}...")

    # Summarization
    results = integrator.import_summarization_data(
        'data/intermediate/summarization/trend_insights_metrics.csv',
        'data/intermediate/summarization/trend_insights_summary.json'
    )

    for result in results:
        print(f"{result.stage}: {'✅' if result.success else '❌'} {result.records_imported} records")
        if not result.success:
            print(f"   Error: {result.error_message[:80]}...")

    print("\n🔍 Final database validation...")
    validation = integrator.validate_database_integration()
    print(f"Overall status: {validation['overall_status']}")

    for table, stats in validation['table_stats'].items():
        print(f"   {table}: {stats['record_count']} records")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
