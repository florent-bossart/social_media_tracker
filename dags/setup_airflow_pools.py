#!/usr/bin/env python3
"""
Airflow Memory Optimization Configuration

This script sets up Airflow pools and configurations to manage memory-intensive tasks.
Run this after Airflow is initialized to configure memory management.
"""

import os
import sys
from pathlib import Path

# Add Airflow to path
sys.path.append('/app')

try:
    from airflow import settings
    from airflow.models import Pool
    from airflow.utils.db import create_session

    def setup_memory_pools():
        """Set up Airflow pools for memory management"""

        with create_session() as session:
            # Create or update memory intensive pool
            memory_pool = session.query(Pool).filter(Pool.pool == 'memory_intensive_pool').first()

            if memory_pool:
                memory_pool.slots = 1  # Only allow 1 memory-intensive task at a time
                memory_pool.description = 'Pool for memory-intensive tasks like ML model inference'
            else:
                memory_pool = Pool(
                    pool='memory_intensive_pool',
                    slots=1,
                    description='Pool for memory-intensive tasks like ML model inference'
                )
                session.add(memory_pool)

            # Create or update translation pool
            translation_pool = session.query(Pool).filter(Pool.pool == 'translation_pool').first()

            if translation_pool:
                translation_pool.slots = 1  # Only allow 1 translation task at a time
                translation_pool.description = 'Pool specifically for translation tasks'
            else:
                translation_pool = Pool(
                    pool='translation_pool',
                    slots=1,
                    description='Pool specifically for translation tasks'
                )
                session.add(translation_pool)

            session.commit()
            print("✅ Airflow pools configured successfully")
            print("   - memory_intensive_pool: 1 slot")
            print("   - translation_pool: 1 slot")

    if __name__ == "__main__":
        setup_memory_pools()

except ImportError as e:
    print(f"❌ Could not import Airflow components: {e}")
    print("This script should be run from within the Airflow environment")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error setting up pools: {e}")
    sys.exit(1)
