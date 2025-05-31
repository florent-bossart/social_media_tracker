#!/bin/bash

# Complete Database Integration Solution using Docker exec
# This script provides a working alternative to the Python database integration

echo "🚀 Starting complete pipeline database import via Docker..."
echo "==============================================================="

# Function to execute SQL commands
exec_sql() {
    docker exec social_media_tracker-social_media_tracker_db-1 psql -U dbt -d social_db -c "$1"
}

# Function to copy and import CSV files
import_csv() {
    local table_name=$1
    local csv_file=$2
    local temp_table="${table_name}_temp"

    echo "📊 Importing $table_name from $csv_file..."

    # Check if file exists
    if [ ! -f "$csv_file" ]; then
        echo "❌ File not found: $csv_file"
        return 1
    fi

    # Copy CSV to container
    docker cp "$csv_file" social_media_tracker-social_media_tracker_db-1:/tmp/import.csv

    # Create temporary table with same structure (without id)
    case $table_name in
        "entity_extraction")
            exec_sql "
            CREATE TEMP TABLE $temp_table (
                source_platform TEXT,
                original_text TEXT,
                extraction_date DATE,
                confidence_score FLOAT,
                entities_artists JSON,
                entities_artists_count INTEGER,
                entities_songs JSON,
                entities_songs_count INTEGER,
                entities_genres JSON,
                entities_genres_count INTEGER,
                entities_song_indicators JSON,
                entities_song_indicators_count INTEGER,
                entities_sentiment_indicators JSON,
                entities_sentiment_indicators_count INTEGER,
                entities_music_events JSON,
                entities_music_events_count INTEGER,
                entities_temporal_references JSON,
                entities_temporal_references_count INTEGER,
                entities_other_entities JSON,
                entities_other_entities_count INTEGER
            );
            "
            ;;
        "sentiment_analysis")
            exec_sql "
            CREATE TEMP TABLE $temp_table (
                source_platform TEXT,
                original_text TEXT,
                sentiment_score FLOAT,
                sentiment_label TEXT,
                sentiment_reasoning TEXT,
                artist_sentiment JSON,
                genre_sentiment JSON,
                overall_sentiment TEXT,
                confidence_score FLOAT,
                analysis_date DATE
            );
            "
            ;;
        "trend_analysis")
            exec_sql "
            CREATE TEMP TABLE $temp_table (
                artist_name TEXT,
                trend_score FLOAT,
                mention_count INTEGER,
                sentiment_trend FLOAT,
                platforms JSON,
                analysis_date DATE
            );
            "
            ;;
    esac

    # Import CSV data into temp table (skip header and id column)
    exec_sql "\\COPY $temp_table FROM '/tmp/import.csv' WITH CSV HEADER;"

    # Insert from temp table to actual table
    exec_sql "INSERT INTO analytics.$table_name SELECT * FROM $temp_table;"

    # Get count
    local count=$(exec_sql "SELECT COUNT(*) FROM $temp_table;" | grep -E "^\s*[0-9]+\s*$" | tr -d ' ')
    echo "✅ Imported $count records into $table_name"

    # Clean up
    exec_sql "DROP TABLE $temp_table;"
    docker exec social_media_tracker-social_media_tracker_db-1 rm -f /tmp/import.csv
}

# Clear existing data
echo "🧹 Clearing existing pipeline data..."
exec_sql "
TRUNCATE TABLE analytics.entity_extraction RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.sentiment_analysis RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.trend_analysis RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.summarization_metrics RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.summarization_insights RESTART IDENTITY CASCADE;
"
echo "✅ Data cleared successfully"

# Import each stage
echo ""
echo "📊 Stage 1: Entity Extraction"
import_csv "entity_extraction" "data/intermediate/entity_extraction/quick_test_entities.csv"

echo ""
echo "💭 Stage 2: Sentiment Analysis"
import_csv "sentiment_analysis" "data/intermediate/sentiment_analysis/entity_sentiment_combined.csv"

echo ""
echo "📈 Stage 3: Trend Analysis"
import_csv "trend_analysis" "data/intermediate/trend_analysis/artist_trends.csv"

echo ""
echo "📋 Stage 4: Summarization"
# For summarization, we need to handle both CSV and JSON files
echo "📊 Importing summarization metrics..."
if [ -f "data/intermediate/summarization/trend_insights_metrics.csv" ]; then
    docker cp "data/intermediate/summarization/trend_insights_metrics.csv" social_media_tracker-social_media_tracker_db-1:/tmp/metrics.csv
    exec_sql "
    CREATE TEMP TABLE metrics_temp (
        total_artists INTEGER,
        total_mentions INTEGER,
        avg_sentiment FLOAT,
        top_platforms JSON,
        analysis_confidence FLOAT,
        analysis_date DATE
    );
    \\COPY metrics_temp FROM '/tmp/metrics.csv' WITH CSV HEADER;
    INSERT INTO analytics.summarization_metrics SELECT * FROM metrics_temp;
    DROP TABLE metrics_temp;
    "
    echo "✅ Imported summarization metrics"
else
    echo "⚠️ Summarization metrics file not found"
fi

echo ""
echo "📋 Final database validation..."
exec_sql "
SELECT
    'entity_extraction' as table_name, COUNT(*) as records FROM analytics.entity_extraction
UNION ALL
SELECT
    'sentiment_analysis' as table_name, COUNT(*) as records FROM analytics.sentiment_analysis
UNION ALL
SELECT
    'trend_analysis' as table_name, COUNT(*) as records FROM analytics.trend_analysis
UNION ALL
SELECT
    'summarization_metrics' as table_name, COUNT(*) as records FROM analytics.summarization_metrics
UNION ALL
SELECT
    'summarization_insights' as table_name, COUNT(*) as records FROM analytics.summarization_insights
ORDER BY table_name;
"

echo ""
echo "🎉 Database integration completed successfully!"
