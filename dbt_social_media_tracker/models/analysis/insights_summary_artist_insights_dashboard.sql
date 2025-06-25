{{ config(materialized='view') }}

SELECT
    analysis_timestamp,
    {{ url_decode('artist_name') }} as artist_name,
    insight_text,
    source_file
FROM {{ source('analytics', 'insights_summary_artist_insights') }}
ORDER BY analysis_timestamp DESC, artist_name
