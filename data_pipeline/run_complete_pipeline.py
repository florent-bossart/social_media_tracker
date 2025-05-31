#!/usr/bin/env python3
"""
Complete Multi-Stage Japanese Music Trends Analysis Pipeline

This script runs the full pipeline from entity extraction through sentiment analysis
to trend detection, producing comprehensive music trend insights.

Author: GitHub Copilot Assistant
Date: 2025-01-07
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
from dotenv import load_dotenv # Added import

# Add the project root to the Python path
# Assuming this script is in data_pipeline, the project root is one level up
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(_PROJECT_ROOT)


# Define default ngrok URLs as constants or load from a config file if preferred
DEFAULT_ENTITY_EXTRACTION_HOST = "https://0631-2400-4050-3243-1400-be00-2b32-3d86-ec6.ngrok-free.app"
DEFAULT_SENTIMENT_ANALYSIS_HOST = "https://89ee-2400-4050-3243-1400-985a-ca78-1567-5b73.ngrok-free.app"
# Add a general LLM host, which can be overridden by specific ones if they are also provided.
DEFAULT_LLM_HOST = None # Or a sensible default like "http://localhost:11434"

load_dotenv(dotenv_path=os.path.join(_PROJECT_ROOT, '.env')) # Load environment variables from .env file in project root

def setup_logging():
    """Setup logging for the pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def run_entity_extraction(logger, input_file: str, output_dir: str, ollama_host_url: str) -> Dict[str, Any]:
    """Run entity extraction stage"""
    logger.info(f"🔍 Starting Entity Extraction Stage on {ollama_host_url}")

    try:
        from llm_enrichment.entity.entity_extraction import MusicEntityExtractor
        from llm_enrichment.entity.entity_extraction_config import EntityExtractionConfig

        config = EntityExtractionConfig()
        # MusicEntityExtractor now takes ollama_host directly
        extractor = MusicEntityExtractor(config, ollama_host=ollama_host_url)

        # Determine platform and date for the process_file method
        platform = "reddit" if "reddit" in input_file.lower() else "youtube" if "youtube" in input_file.lower() else "unknown"
        current_date = datetime.now().strftime('%Y%m%d')
        output_file_path = extractor.process_file(input_file, platform, current_date)

        if output_file_path and os.path.exists(output_file_path):
            # File was created, proceed to read it
            df = pd.read_csv(output_file_path)
            result = {
                "status": "success",
                "output_file": output_file_path,
                "records_processed": len(df) # Get record count from the output file
            }
        elif output_file_path: # Path was returned, but file doesn't exist
            logger.error(f"Entity extractor reported output path {output_file_path}, but the file was not found.")
            result = {"status": "error", "error": f"Output file {output_file_path} not created by extractor."}
        else: # No output path was returned from extractor.process_file
            result = {"status": "error", "error": "Entity extraction process_file returned no output path"}

        if result.get("status") == "success":
            logger.info(f"✅ Entity extraction completed: {result['output_file']}")
            return {
                "status": "success",
                "output_file": result["output_file"],
                "records_processed": result.get("records_processed", 0)
            }
        else:
            logger.error(f"❌ Entity extraction failed: {result.get('error', 'Unknown error')}")
            return {"status": "error", "error": result.get("error", "Unknown error")}

    except Exception as e:
        logger.error(f"❌ Entity extraction error: {e}")
        return {"status": "error", "error": str(e)}

def run_sentiment_analysis(logger, input_file: str, output_dir: str, ollama_host_url: str) -> Dict[str, Any]:
    """Run sentiment analysis stage"""
    logger.info(f"😊 Starting Sentiment Analysis Stage on {ollama_host_url}")

    try:
        from llm_enrichment.sentiment.sentiment_analysis import SentimentAnalyzer

        analyzer = SentimentAnalyzer(ollama_host=ollama_host_url) # Pass ollama_host_url

        # Construct the output filename
        base_filename = os.path.basename(input_file)
        name_part, ext_part = os.path.splitext(base_filename)
        # Example: 20230101_entity_output.csv -> 20230101_sentiment_analysis.csv
        # This assumes entity output might have a suffix like '_entity_extraction' or similar
        # We'll make a generic sentiment output name.
        # A more robust way might be to strip known suffixes from previous stage if any.
        # For now, let's use a timestamp or a fixed suffix.
        # The analyze_file method itself generates a timestamped name if output_filename is None.
        # Let's create a more predictable name.
        date_prefix = name_part.split('_')[0] if '_' in name_part else datetime.now().strftime('%Y%m%d')
        output_filename = f"{date_prefix}_sentiment_analysis_results{ext_part}"

        # The analyze_file method saves the file in its own configured SENTIMENT_OUTPUT_DIR,
        # but we want it in the pipeline's sentiment_dir.
        # For now, let's allow analyze_file to use its default output dir or make it configurable.
        # The SentimentAnalyzer.save_results uses SENTIMENT_OUTPUT_DIR.
        # We will call analyze_file, which returns the full path to the created file.
        # We need to ensure the records_processed count is also returned.

        output_file_path = analyzer.analyze_file(input_file_path=input_file, output_filename=output_filename)

        if output_file_path and os.path.exists(output_file_path):
            # Read the output file to get the count of records processed
            df_sentiment = pd.read_csv(output_file_path)
            records_processed = len(df_sentiment)
            logger.info(f"✅ Sentiment analysis completed: {output_file_path}")
            return {
                "status": "success",
                "output_file": output_file_path,
                "records_processed": records_processed
            }
        elif output_file_path: # Path was returned, but file doesn't exist
            logger.error(f"Sentiment analyzer reported output path {output_file_path}, but the file was not found.")
            return {"status": "error", "error": f"Output file {output_file_path} not created by sentiment analyzer."}
        else: # No output path was returned
            logger.error("Sentiment analysis analyze_file returned no output path.")
            return {"status": "error", "error": "Sentiment analysis analyze_file returned no output path"}

    except Exception as e:
        logger.error(f"❌ Sentiment analysis error: {e}")
        return {"status": "error", "error": str(e)}

def run_trend_detection(logger, sentiment_file: str, output_dir: str, ollama_host_url: Optional[str] = None) -> Dict[str, Any]: # Modified to take ollama_host_url
    """Run trend detection stage"""
    logger.info(f"📈 Starting Trend Detection Stage")
    if ollama_host_url:
        logger.info(f"Trend Detection will use Ollama host: {ollama_host_url} if it performs LLM calls.")

    try:
        from llm_enrichment.trend.trend_detection import TrendDetector
        from llm_enrichment.trend.trend_detection_config import TrendDetectionConfig

        config = TrendDetectionConfig()
        detector = TrendDetector(config, ollama_host=ollama_host_url) # Pass ollama_host_url

        # Run trend detection
        result = detector.analyze_trends(sentiment_file, output_dir) # Uses sentiment_file

        if result.get("status") == "success":
            logger.info(f"✅ Trend detection completed")
            return {
                "status": "success",
                "output_files": result["output_files"],
                "metrics": result["metrics"],
                "summary": result["summary"]
            }
        else:
            logger.error(f"❌ Trend detection failed: {result.get('error', 'Unknown error')}")
            return {"status": "error", "error": result.get("error", "Unknown error")}

    except Exception as e:
        logger.error(f"❌ Trend detection error: {e}")
        return {"status": "error", "error": str(e)}

def run_summarization(logger, trend_file: str, output_dir: str, ollama_host_url: Optional[str] = None) -> Dict[str, Any]: # Modified to take ollama_host_url
    """Run summarization stage"""
    logger.info(f"📝 Starting Summarization Stage")
    if ollama_host_url:
        logger.info(f"Summarization will use Ollama host: {ollama_host_url}")
    try:
        from llm_enrichment.summarization.summarization import TrendSummarizer, SummaryConfig

        config = SummaryConfig()
        # TrendSummarizer now takes ollama_host directly
        summarizer = TrendSummarizer(config, ollama_host=ollama_host_url)

        # Run summarization
        result = summarizer.summarize_trend_data(trend_file, output_dir)

        if result.get("status") == "success":
            logger.info(f"✅ Summarization completed: {result['summary_file']}")
            return {
                "status": "success",
                "summary_file": result["summary_file"],
                "metrics": result.get("metrics", {}),
                "insights": result.get("insights", {})
            }
        else:
            logger.error(f"❌ Summarization failed: {result.get('error', 'Unknown error')}")
            return {"status": "error", "error": result.get("error", "Unknown error")}

    except Exception as e:
        logger.error(f"❌ Summarization error: {e}")
        return {"status": "error", "error": str(e)}

def run_database_integration(logger, pipeline_outputs: Dict[str, str]) -> Dict[str, Any]:
    """Run database integration stage"""
    logger.info("💾 Starting Database Integration Stage")

    try:
        from llm_enrichment.database.database_integration import DatabaseIntegrator

        integrator = DatabaseIntegrator()

        # Example: Import entity extraction data
        if "entity_extraction" in pipeline_outputs:
            result = integrator.import_entity_extraction(pipeline_outputs["entity_extraction"])
            logger.info(f"Database import for entity extraction: {result.status} - {result.message}")

        # Example: Import sentiment analysis data
        if "sentiment_analysis" in pipeline_outputs:
            result = integrator.import_sentiment_analysis(pipeline_outputs["sentiment_analysis"])
            logger.info(f"Database import for sentiment analysis: {result.status} - {result.message}")

        # Example: Import trend detection data
        if "trend_detection" in pipeline_outputs:
            result = integrator.import_trend_detection(pipeline_outputs["trend_detection"]) # Assuming this method exists
            logger.info(f"Database import for trend detection: {result.status} - {result.message}")

        # Example: Import summarization data
        if "summarization_metrics" in pipeline_outputs and "summarization_insights" in pipeline_outputs:
            # Assuming a method that takes both files or individual methods
            result_metrics = integrator.import_summarization_metrics(pipeline_outputs["summarization_metrics"])
            logger.info(f"Database import for summarization metrics: {result_metrics.status} - {result_metrics.message}")
            result_insights = integrator.import_summarization_insights(pipeline_outputs["summarization_insights"]) # Assuming this method exists
            logger.info(f"Database import for summarization insights: {result_insights.status} - {result_insights.message}")


        logger.info("✅ Database integration completed")
        return {"status": "success"}

    except ImportError as e:
        logger.error(f"Error importing database integration module: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error during database integration: {e}")
        return {"status": "error", "message": str(e)}

def generate_pipeline_report(logger, results: Dict[str, Any], output_dir: str) -> str:
    """Generate a comprehensive pipeline execution report"""
    report = {
        "pipeline_execution": {
            "timestamp": datetime.now().isoformat(),
            "status": "success" if all(r.get("status") == "success" for r in results.values() if r) else "partial_success", # check if r is not None
            "stages_completed": len([r for r in results.values() if r and r.get("status") == "success"]), # check if r is not None
            "total_stages": len(results)
        },
        "stage_results": results,
        "data_flow": {
            "input_file": results.get("entity_extraction", {}).get("input_file", ""), # Ensure this is captured if needed
            "entity_output": results.get("entity_extraction", {}).get("output_file", ""),
            "sentiment_output": results.get("sentiment_analysis", {}).get("output_file", ""),
            "trend_outputs": results.get("trend_detection", {}).get("output_files", {}),
            "summary_output": results.get("summarization", {}).get("summary_file", "") # Added summary output
        },
        "metrics_summary": {
            "records_processed_entity": results.get("entity_extraction", {}).get("records_processed", 0),
            "records_processed_sentiment": results.get("sentiment_analysis", {}).get("records_processed", 0),
            "artist_trends_found": results.get("trend_detection", {}).get("metrics", {}).get("artist_trends_found", 0),
            "genre_trends_found": results.get("trend_detection", {}).get("metrics", {}).get("genre_trends_found", 0)
        }
    }

    # Add trend summary if available
    if "trend_detection" in results and "summary" in results["trend_detection"]:
        report["trend_insights"] = results["trend_detection"]["summary"]

    # Save report
    report_file = os.path.join(output_dir, "pipeline_execution_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"📋 Pipeline report saved to: {report_file}")
    return report_file

def run_complete_pipeline(input_file: str, base_output_dir: str = "data/intermediate",
                          entity_extraction_host: Optional[str] = None,
                          sentiment_analysis_host: Optional[str] = None,
                          llm_host: Optional[str] = None) -> Dict[str, Any]: # llm_host is general from CLI / default
    """Run the complete music trends analysis pipeline"""
    logger = setup_logging()

    logger.info("🚀 Starting Complete Japanese Music Trends Analysis Pipeline")
    logger.info("=" * 70)

    # Determine platform from input_file
    platform = "unknown"
    if "youtube" in input_file.lower():
        platform = "youtube"
    elif "reddit" in input_file.lower():
        platform = "reddit"
    logger.info(f"Platform detected: {platform}")

    # Get platform-specific LLM host from environment variables
    platform_env_llm_host = None
    if platform == "youtube":
        platform_env_llm_host = os.getenv("YOUTUBE_LLM_HOST")
        if platform_env_llm_host:
            logger.info(f"Found YOUTUBE_LLM_HOST from env: {platform_env_llm_host}")
    elif platform == "reddit":
        platform_env_llm_host = os.getenv("REDDIT_LLM_HOST")
        if platform_env_llm_host:
            logger.info(f"Found REDDIT_LLM_HOST from env: {platform_env_llm_host}")

    # Determine effective hosts
    # Priority:
    # 1. Specific CLI host (e.g., --entity-host)
    # 2. Platform-specific environment variable (e.g., YOUTUBE_LLM_HOST)
    # 3. General CLI host (--llm-host)
    # 4. Script-defined default for the stage (e.g., DEFAULT_ENTITY_EXTRACTION_HOST)

    effective_entity_host = entity_extraction_host or platform_env_llm_host or llm_host or DEFAULT_ENTITY_EXTRACTION_HOST
    effective_sentiment_host = sentiment_analysis_host or platform_env_llm_host or llm_host or DEFAULT_SENTIMENT_ANALYSIS_HOST

    # For Trend Detection and Summarization, they use a general LLM host.
    # Priority: platform_env_llm_host -> llm_host (from CLI/default) -> script's DEFAULT_LLM_HOST (which is None if llm_host arg is None)
    general_llm_for_other_stages = platform_env_llm_host or llm_host

    logger.info(f"Effective Entity Extraction Host: {effective_entity_host}")
    logger.info(f"Effective Sentiment Analysis Host: {effective_sentiment_host}")
    if general_llm_for_other_stages:
        logger.info(f"General LLM Host for Trend/Summarization: {general_llm_for_other_stages}")
    else:
        logger.info("No specific general LLM Host for Trend/Summarization; stages will use their internal defaults or None.")

    # Create output directories
    # Adjust base_output_dir to be relative to _PROJECT_ROOT if it's a relative path
    if not os.path.isabs(base_output_dir):
        base_output_dir = os.path.join(_PROJECT_ROOT, base_output_dir)

    entity_dir = os.path.join(base_output_dir, "entity_extraction")
    sentiment_dir = os.path.join(base_output_dir, "sentiment_analysis")
    trend_dir = os.path.join(base_output_dir, "trend_analysis")
    summarization_dir = os.path.join(base_output_dir, "summarization") # Added summarization_dir

    os.makedirs(entity_dir, exist_ok=True)
    os.makedirs(sentiment_dir, exist_ok=True)
    os.makedirs(trend_dir, exist_ok=True)
    os.makedirs(summarization_dir, exist_ok=True) # Create summarization_dir

    results = {}
    # Store the initial input file for the report, will be added to entity_extraction results later if needed
    # results["initial_input_file"] = input_file

    # Adjust input_file path to be absolute if it's relative, assuming it's relative to project root
    if not os.path.isabs(input_file):
        input_file = os.path.join(_PROJECT_ROOT, input_file)

    # Stage 1: Entity Extraction
    logger.info(f"📁 Input file: {input_file}")
    # Pass the input_file to entity_result for report generation
    entity_result = run_entity_extraction(logger, input_file, entity_dir, effective_entity_host) # Use effective_entity_host
    entity_result["input_file"] = input_file # Add input_file to result for reporting
    results["entity_extraction"] = entity_result


    if entity_result["status"] != "success":
        logger.error("🛑 Pipeline stopped due to entity extraction failure")
        generate_pipeline_report(logger, results, base_output_dir) # Generate report even on failure
        return {"status": "failed", "results": results}

    # Stage 2: Sentiment Analysis
    sentiment_result = run_sentiment_analysis(logger, entity_result["output_file"], sentiment_dir, effective_sentiment_host) # Use effective_sentiment_host
    results["sentiment_analysis"] = sentiment_result

    if sentiment_result["status"] != "success":
        logger.error("🛑 Pipeline stopped due to sentiment analysis failure")
        generate_pipeline_report(logger, results, base_output_dir) # Generate report even on failure
        return {"status": "failed", "results": results}

    # Stage 3: Trend Detection
    # The run_trend_detection function expects the sentiment file as input.
    # Pass general_llm_for_other_stages to trend detection
    trend_result = run_trend_detection(logger, sentiment_result["output_file"], trend_dir, ollama_host_url=general_llm_for_other_stages)
    results["trend_detection"] = trend_result


    if trend_result["status"] != "success":
        logger.warning("⚠️ Trend detection failed, but previous stages completed")
        generate_pipeline_report(logger, results, base_output_dir) # Generate report even on partial failure
        return {"status": "partial_success", "results": results}

    # Stage 4: Summarization
    trend_summary_file_for_summarization = trend_result.get("output_files", {}).get("trend_summary")
    if not trend_summary_file_for_summarization:
        logger.error("🛑 Cannot run summarization: Trend summary file not found in trend_detection output.")
        results["summarization"] = {"status": "skipped", "error": "Trend summary file missing"}
        generate_pipeline_report(logger, results, base_output_dir)
        return {"status": "partial_success", "results": results}

    # Pass general_llm_for_other_stages to summarization
    summarization_result = run_summarization(logger, trend_summary_file_for_summarization, summarization_dir, ollama_host_url=general_llm_for_other_stages)
    results["summarization"] = summarization_result


    if summarization_result["status"] != "success":
        logger.warning("⚠️ Summarization failed, but previous stages completed")
        generate_pipeline_report(logger, results, base_output_dir) # Generate report
        return {"status": "partial_success", "results": results}

    # Stage 5: Database Integration
    db_pipeline_outputs = {}
    if entity_result.get("status") == "success" and "output_file" in entity_result:
        db_pipeline_outputs["entity_extraction"] = entity_result["output_file"]
    if sentiment_result.get("status") == "success" and "output_file" in sentiment_result:
        db_pipeline_outputs["sentiment_analysis"] = sentiment_result["output_file"]
    if trend_result.get("status") == "success" and "output_files" in trend_result:
        db_pipeline_outputs["trend_detection"] = trend_result["output_files"].get("trend_summary")
    if summarization_result.get("status") == "success":
        db_pipeline_outputs["summarization_insights"] = summarization_result.get("summary_file")
        # If metrics are separate and their path is in summarization_result["metrics_file"]
        # db_pipeline_outputs["summarization_metrics"] = summarization_result.get("metrics_file")


    db_integration_result = run_database_integration(logger, db_pipeline_outputs)
    results["database_integration"] = db_integration_result

    if db_integration_result["status"] != "success":
        logger.warning("⚠️ Database integration encountered issues, but pipeline completed")
        generate_pipeline_report(logger, results, base_output_dir) # Generate report
        return {"status": "partial_success", "results": results}

    # Generate pipeline report
    report_file = generate_pipeline_report(logger, results, base_output_dir)


    # Display summary
    logger.info("\n🎉 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    logger.info("=" * 50)

    if "trend_detection" in results and results["trend_detection"].get("status") == "success":
        metrics = results["trend_detection"]["metrics"]
        logger.info(f"📊 Artist trends found: {metrics['artist_trends_found']}")
        logger.info(f"🎵 Genre trends found: {metrics['genre_trends_found']}")

        if "summary" in results["trend_detection"]:
            summary = results["trend_detection"]["summary"]
            logger.info(f"📈 Total artists analyzed: {summary['overview']['total_artists_analyzed']}")
            logger.info(f"🎭 Total genres analyzed: {summary['overview']['total_genres_analyzed']}")

            # Display top trends
            if summary.get("top_artists"):
                logger.info("\n🌟 TOP ARTIST TRENDS:")
                for i, artist in enumerate(summary["top_artists"][:3], 1):
                    logger.info(f"  {i}. {artist['name']} (strength: {artist['trend_strength']}, mentions: {artist['mentions']})")

            if summary.get("top_genres"):
                logger.info("\n🎵 TOP GENRE TRENDS:")
                for i, genre in enumerate(summary["top_genres"][:3], 1):
                    logger.info(f"  {i}. {genre['name']} (popularity: {genre['popularity_score']})")

    logger.info(f"\n📋 Full report: {report_file}")

    return {
        "status": "success",
        "results": results,
        "report_file": report_file
    }

def main():
    """Main function for command-line execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Run complete Japanese music trends analysis pipeline')
    parser.add_argument('--input', '-i',
                       default='data/intermediate/20250528_full_youtube_comments_cleaned.csv',
                       help='Input CSV file with social media comments (relative to project root)')
    parser.add_argument('--output', '-o',
                       default='data/intermediate',
                       help='Base output directory for all pipeline stages (relative to project root)')
    parser.add_argument('--entity-host',
                        default=None, # Changed from DEFAULT_ENTITY_EXTRACTION_HOST
                        help='Ollama host URL for Entity Extraction (e.g., http://localhost:11434 or ngrok URL)')
    parser.add_argument('--sentiment-host',
                        default=None, # Default to None, will use llm_host or internal default
                        help='Ollama host URL for Sentiment Analysis (e.g., http://localhost:11434 or ngrok URL). Overrides --llm-host for this stage.')
    parser.add_argument('--llm-host',
                        default=DEFAULT_LLM_HOST, # Default can be None or e.g. "http://localhost:11434"
                        help='General Ollama host URL for all LLM stages (Entity, Sentiment, Trend, Summarization). Specific stage hosts (--entity-host, --sentiment-host) will override this for their respective stages.')
    parser.add_argument('--test', action='store_true',
                       help='Run with existing entity-sentiment combined data for testing')

    args = parser.parse_args()

    run_complete_pipeline(
        input_file=args.input,
        base_output_dir=args.output,
        entity_extraction_host=args.entity_host,
        sentiment_analysis_host=args.sentiment_host,
        llm_host=args.llm_host
    )

if __name__ == "__main__":
    main()
