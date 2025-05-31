#!/usr/bin/env python3
"""
Minimal database integration test
"""

import os
import sys

# Add current directory to path
current_dir = '/home/florent.bossart/code/florent-bossart/social_media_tracker'
sys.path.insert(0, current_dir)

# Set environment variables
os.environ['WAREHOUSE_HOST'] = 'localhost'
os.environ['WAREHOUSE_PORT'] = '5434'
os.environ['WAREHOUSE_DB'] = 'social_db'
os.environ['WAREHOUSE_USER'] = 'dbt'
os.environ['WAREHOUSE_PASSWORD'] = 'bossart'

print("🔧 Environment configured")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

try:
    print("📦 Importing database integration...")
    from data_pipeline.database_integration import PipelineDBIntegrator
    print("✅ Import successful")

    print("🏗️ Creating integrator instance...")
    integrator = PipelineDBIntegrator()
    print("✅ Integrator created")

    print("🔌 Testing database connection...")
    with integrator.engine.connect() as conn:
        result = conn.execute(integrator.metadata.bind.text("SELECT 1"))
        test_result = result.scalar()
        print(f"✅ Database connection successful: {test_result}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
