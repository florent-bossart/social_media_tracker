#!/usr/bin/env python3
"""
Test the improved database integration with data clearing functionality
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

    print("🔧 Testing improved database integration with data clearing...")
    integrator = PipelineDBIntegrator()

    # First, let's check current data counts
    print("\n📊 Current database state:")
    validation = integrator.validate_database_integration()
    for table, stats in validation['table_stats'].items():
        print(f"   {table}: {stats['record_count']} records")

    # Test the complete pipeline import with clear_existing=True
    print("\n🧹 Testing complete pipeline import with data clearing...")
    results = integrator.import_complete_pipeline(clear_existing=True)

    print("\n📋 Import Results:")
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.stage}: {result.records_imported} records")
        if not result.success and result.error_message:
            print(f"   Error: {result.error_message[:100]}...")

    # Final validation
    print("\n🔍 Final database validation...")
    validation = integrator.validate_database_integration()
    print(f"Overall status: {validation['overall_status']}")

    for table, stats in validation['table_stats'].items():
        print(f"   {table}: {stats['record_count']} records")

    # Test analytics views if available
    print("\n📊 Testing analytics views...")
    try:
        with integrator.engine.connect() as conn:
            # Test pipeline overview view
            result = conn.execute(integrator.metadata.bind.text(
                "SELECT * FROM analytics.pipeline_overview_view LIMIT 1;"
            ))
            row = result.fetchone()
            if row:
                print("✅ Pipeline overview view accessible")
            else:
                print("⚠️ Pipeline overview view is empty")
    except Exception as e:
        print(f"⚠️ Analytics views test failed: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
