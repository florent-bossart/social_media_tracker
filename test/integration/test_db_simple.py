#!/usr/bin/env python3
"""
Simple test script for database integration with manual environment setup
"""

import os
import sys
sys.path.append('/home/florent.bossart/code/florent-bossart/social_media_tracker')

# Set environment variables manually for testing
os.environ['WAREHOUSE_HOST'] = 'localhost'
os.environ['WAREHOUSE_PORT'] = '5434'
os.environ['WAREHOUSE_DB'] = 'social_db'
os.environ['WAREHOUSE_USER'] = 'dbt'
os.environ['WAREHOUSE_PASSWORD'] = 'bossart'

try:
    from data_pipeline.database_integration import PipelineDBIntegrator

    print("🔌 Testing database connection...")
    integrator = PipelineDBIntegrator()

    # Test connection
    with integrator.engine.connect() as conn:
        result = conn.execute(integrator.metadata.bind.text("SELECT version()"))
        version = result.scalar()
        print(f"✅ Connected to PostgreSQL: {version}")

    # Test schema creation
    print("\n🗃️ Creating schema and tables...")
    success = integrator.create_schema_and_tables()

    if success:
        print("✅ Schema and tables created successfully")

        # Test data import
        print("\n📊 Testing data import...")
        results = integrator.import_complete_pipeline()

        successful_imports = sum(1 for r in results if r.success)
        total_records = sum(r.records_imported for r in results if r.success)

        print(f"\n📈 Import Results:")
        print(f"   Successful stages: {successful_imports}/{len(results)}")
        print(f"   Total records imported: {total_records}")

        # Test validation
        print("\n🔍 Running validation...")
        validation = integrator.validate_database_integration()
        print(f"   Validation status: {validation['overall_status']}")

        if validation['overall_status'] in ['success', 'tables_created_no_data']:
            print("🎉 Database integration test PASSED!")
        else:
            print("⚠️ Database integration test completed with warnings")
    else:
        print("❌ Schema creation failed")

except Exception as e:
    print(f"❌ Test failed: {str(e)}")
    import traceback
    traceback.print_exc()
