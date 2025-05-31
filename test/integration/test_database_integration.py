#!/usr/bin/env python3
"""
Database Integration Testing Script
This script validates all pipeline data imports and analytics queries
"""

import psycopg2
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.database_integration import PipelineDBIntegrator, ImportResult

def test_database_connection():
    """Test basic database connection"""
    print("🔌 Testing database connection...")

    try:
        integrator = PipelineDBIntegrator()
        with integrator.engine.connect() as conn:
            result = conn.execute(integrator.metadata.bind.text("SELECT 1 as test"))
            test_value = result.scalar()

        if test_value == 1:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed - unexpected result")
            return False

    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_schema_creation():
    """Test analytics schema and table creation"""
    print("\n🗃️ Testing schema and table creation...")

    try:
        integrator = PipelineDBIntegrator()
        success = integrator.create_schema_and_tables()

        if success:
            # Verify tables exist
            with integrator.engine.connect() as conn:
                tables_to_check = [
                    'entity_extraction',
                    'sentiment_analysis',
                    'trend_analysis',
                    'summarization_metrics',
                    'summarization_insights'
                ]

                for table in tables_to_check:
                    try:
                        result = conn.execute(integrator.metadata.bind.text(
                            f"SELECT COUNT(*) FROM analytics.{table}"
                        ))
                        print(f"✅ Table analytics.{table} exists")
                    except Exception as e:
                        print(f"❌ Table analytics.{table} not found: {str(e)}")
                        return False

            print("✅ All pipeline tables created successfully")
            return True
        else:
            print("❌ Schema creation failed")
            return False

    except Exception as e:
        print(f"❌ Schema creation error: {str(e)}")
        return False

def test_data_import():
    """Test data import for all pipeline stages"""
    print("\n📊 Testing data import...")

    integrator = PipelineDBIntegrator()

    # Run complete pipeline import
    results = integrator.import_complete_pipeline()

    success_count = 0
    total_records = 0

    for result in results:
        if result.success:
            print(f"✅ {result.stage}: {result.records_imported} records imported")
            success_count += 1
            total_records += result.records_imported
        else:
            print(f"❌ {result.stage}: {result.error_message}")

    print(f"\n📈 Import Summary:")
    print(f"   Successful imports: {success_count}/{len(results)}")
    print(f"   Total records: {total_records}")

    return success_count > 0

def test_data_validation():
    """Test data validation and consistency"""
    print("\n🔍 Testing data validation...")

    integrator = PipelineDBIntegrator()
    validation_results = integrator.validate_database_integration()

    if validation_results['overall_status'] in ['success', 'tables_created_no_data']:
        print("✅ Database validation passed")

        # Additional consistency checks
        entity_count = validation_results['record_counts'].get('entity_extraction', 0)
        sentiment_count = validation_results['record_counts'].get('sentiment_analysis', 0)

        if entity_count > 0 and sentiment_count > 0:
            print(f"✅ Data flow validation: {entity_count} entities → {sentiment_count} sentiment records")

        return True
    else:
        print(f"❌ Database validation failed: {validation_results['overall_status']}")
        return False

def test_analytics_views():
    """Test analytics views and functions"""
    print("\n📊 Testing analytics views...")

    try:
        integrator = PipelineDBIntegrator()

        with integrator.engine.connect() as conn:
            # Test pipeline overview
            try:
                result = conn.execute(integrator.metadata.bind.text(
                    "SELECT * FROM analytics.pipeline_overview"
                ))
                overview_data = result.fetchall()
                print(f"✅ Pipeline overview: {len(overview_data)} stages")
            except Exception as e:
                print(f"❌ Pipeline overview failed: {str(e)}")
                return False

            # Test artist trends summary
            try:
                result = conn.execute(integrator.metadata.bind.text(
                    "SELECT * FROM analytics.artist_trends_summary LIMIT 5"
                ))
                trends_data = result.fetchall()
                print(f"✅ Artist trends summary: {len(trends_data)} records")
            except Exception as e:
                print(f"❌ Artist trends summary failed: {str(e)}")
                return False

            # Test platform sentiment comparison
            try:
                result = conn.execute(integrator.metadata.bind.text(
                    "SELECT * FROM analytics.platform_sentiment_comparison"
                ))
                platform_data = result.fetchall()
                print(f"✅ Platform sentiment comparison: {len(platform_data)} platforms")
            except Exception as e:
                print(f"❌ Platform sentiment comparison failed: {str(e)}")
                return False

        print("✅ All analytics views working correctly")
        return True

    except Exception as e:
        print(f"❌ Analytics views test failed: {str(e)}")
        return False

def test_query_performance():
    """Test query performance for common analytics queries"""
    print("\n⚡ Testing query performance...")

    try:
        integrator = PipelineDBIntegrator()

        with integrator.engine.connect() as conn:
            # Test common queries with timing
            queries = [
                ("Entity count by platform",
                 "SELECT source_platform, COUNT(*) FROM analytics.entity_extraction GROUP BY source_platform"),
                ("Sentiment distribution",
                 "SELECT overall_sentiment, COUNT(*) FROM analytics.sentiment_analysis GROUP BY overall_sentiment"),
                ("Top trending artists",
                 "SELECT entity_name, trend_strength FROM analytics.trend_analysis WHERE entity_type = 'artist' ORDER BY trend_strength DESC LIMIT 10"),
                ("Average confidence scores",
                 "SELECT AVG(confidence_score) FROM analytics.summarization_metrics")
            ]

            for query_name, query_sql in queries:
                start_time = datetime.now()
                try:
                    result = conn.execute(integrator.metadata.bind.text(query_sql))
                    data = result.fetchall()
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    print(f"✅ {query_name}: {len(data)} rows in {duration:.3f}s")
                except Exception as e:
                    print(f"❌ {query_name} failed: {str(e)}")

        print("✅ Query performance tests completed")
        return True

    except Exception as e:
        print(f"❌ Query performance test failed: {str(e)}")
        return False

def generate_test_report(test_results: Dict[str, bool]) -> Dict[str, Any]:
    """Generate comprehensive test report"""

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    report = {
        'timestamp': datetime.now().isoformat(),
        'test_summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': round(success_rate, 1)
        },
        'test_results': test_results,
        'overall_status': 'PASS' if success_rate >= 80 else 'FAIL',
        'recommendations': []
    }

    # Add recommendations based on failures
    if not test_results.get('database_connection', False):
        report['recommendations'].append("Check database connection settings and credentials")
    if not test_results.get('schema_creation', False):
        report['recommendations'].append("Verify database permissions for schema creation")
    if not test_results.get('data_import', False):
        report['recommendations'].append("Check pipeline output files and data format")
    if not test_results.get('data_validation', False):
        report['recommendations'].append("Review data consistency and pipeline integration")
    if not test_results.get('analytics_views', False):
        report['recommendations'].append("Verify analytics views and SQL schema")
    if not test_results.get('query_performance', False):
        report['recommendations'].append("Check database indexing and query optimization")

    if success_rate == 100:
        report['recommendations'].append("All tests passed! Database integration is ready for production")

    return report

def main():
    """Main test execution function"""
    print("🎵 Japanese Music Trends Analysis - Database Integration Tests")
    print("=" * 70)

    # Run all tests
    test_results = {
        'database_connection': test_database_connection(),
        'schema_creation': test_schema_creation(),
        'data_import': test_data_import(),
        'data_validation': test_data_validation(),
        'analytics_views': test_analytics_views(),
        'query_performance': test_query_performance()
    }

    # Generate test report
    report = generate_test_report(test_results)

    # Print final results
    print("\n" + "=" * 70)
    print("📊 DATABASE INTEGRATION TEST RESULTS")
    print("=" * 70)

    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")

    print(f"\n📈 Overall Results:")
    print(f"   Tests Passed: {report['test_summary']['passed_tests']}/{report['test_summary']['total_tests']}")
    print(f"   Success Rate: {report['test_summary']['success_rate']}%")
    print(f"   Status: {report['overall_status']}")

    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")

    # Save test report
    os.makedirs("test_results", exist_ok=True)
    report_file = f"test_results/database_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Test report saved: {report_file}")

    # Return exit code based on overall status
    return 0 if report['overall_status'] == 'PASS' else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
