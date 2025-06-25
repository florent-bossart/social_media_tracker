-- Pipeline Overview
-- Overview of the data pipeline status
{{ config(materialized='view') }}

SELECT
    'pipeline_overview' as overview_type,
    'supabase' as target_environment,
    COUNT(*) as total_records,
    MIN(artist_name) as sample_artist,
    MAX(artist_name) as last_artist_alphabetically,
    CURRENT_TIMESTAMP as pipeline_run_time
FROM {{ ref('artist_sentiment_dashboard') }}
