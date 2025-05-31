import os
import sys
from datetime import datetime
import argparse # Added import

# Add the project root to the Python path
# Assuming this script is in data_pipeline, the project root is one level up
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(_PROJECT_ROOT)

# Now that sys.path is updated, try importing from the (now correctly referenced) data_pipeline module
# The original script was in the root, so it imported run_complete_pipeline directly.
# If run_complete_pipeline is ALSO moved to data_pipeline, the import becomes relative or module-based.

try:
    # Assuming run_complete_pipeline.py is now also in data_pipeline directory
    from data_pipeline.run_complete_pipeline import run_entity_extraction, setup_logging
except ImportError as e:
    # Fallback if run_complete_pipeline is still expected at root or if there's a circular dependency concern
    # This might happen if this script is run before run_complete_pipeline.py is moved/recognized in its new path.
    try:
        # This import assumes that the original run_complete_pipeline.py (at root) is still accessible
        # or that the run_complete_pipeline.py now in data_pipeline/ can be found via _PROJECT_ROOT in sys.path
        # If run_complete_pipeline was moved to data_pipeline, this might need to be:
        # from data_pipeline.run_complete_pipeline import ...
        # For now, let's assume the goal is to use the one in data_pipeline
        # The initial sys.path.append(_PROJECT_ROOT) should allow finding `data_pipeline.run_complete_pipeline`
        # So the first try block should ideally work.
        # This second try is more of a safeguard or for a different structure.
        # Given the current refactoring, the first `try` is the target.
        print(f"Initial import failed: {e}. Attempting fallback or checking structure.")
        # If run_complete_pipeline is in the same directory (data_pipeline) as this script:
        from .run_complete_pipeline import run_entity_extraction, setup_logging
    except ImportError as e2:
        print(f"Error importing from run_complete_pipeline.py: {e2}")
        print("Please ensure run_complete_pipeline.py is in the data_pipeline directory and sys.path is correctly set.")
        sys.exit(1)

def main(): # Renamed from run_extraction_for_files and added arguments
    logger = setup_logging()

    parser = argparse.ArgumentParser(description="Run entity extraction for a specific file.")
    parser.add_argument("--input_file", required=True, help="Path to the input CSV file (relative to project root if not absolute).")
    parser.add_argument("--platform", required=True, choices=["reddit", "youtube", "other"], help="Platform of the input file (reddit, youtube, other).")
    parser.add_argument("--output_dir", required=True, help="Directory to save the output entity-extracted CSV file (relative to project root if not absolute).")
    # Add ollama_host argument, similar to run_complete_pipeline
    parser.add_argument(
        "--ollama-host",
        type=str,
        default=None, # Default to None, run_entity_extraction will use its own default if not provided
        help="Optional: Ollama host URL for Entity Extraction (e.g., http://localhost:11434 or ngrok URL)."
    )

    args = parser.parse_args()

    # Resolve output_dir relative to _PROJECT_ROOT if it's not absolute
    output_dir_path = Path(args.output_dir)
    if not output_dir_path.is_absolute():
        output_dir_path = _PROJECT_ROOT / output_dir_path
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Resolve input_file path relative to _PROJECT_ROOT if it's not absolute
    input_file_path_arg = Path(args.input_file)
    if not input_file_path_arg.is_absolute():
        input_file_path = _PROJECT_ROOT / input_file_path_arg
    else:
        input_file_path = input_file_path_arg

    platform = args.platform # Platform is used by run_entity_extraction internally now

    if not input_file_path.exists():
        logger.error(f"Input file not found: {input_file_path}")
        sys.exit(1) # Exit if file not found

    logger.info(f"Processing file: {input_file_path} for platform: {platform}")

    # Determine the entity extraction host
    # Priority: CLI arg -> Environment Variable (e.g. YOUTUBE_LLM_HOST if platform matches) -> Default in run_entity_extraction
    # For simplicity in this specific script, we'll prioritize CLI, then let run_entity_extraction handle its defaults.
    # run_entity_extraction in run_complete_pipeline.py already has logic for host selection.
    # We need to pass the ollama_host from args to run_entity_extraction.
    # The run_entity_extraction function expects ollama_host_url as its last parameter.
    # It does not automatically pick up DEFAULT_ENTITY_EXTRACTION_HOST from run_complete_pipeline if None is passed.
    # It needs an explicit host or it will fail if its internal config doesn't specify one.

    # Get the default entity extraction host from run_complete_pipeline if args.ollama_host is not set
    effective_ollama_host = args.ollama_host
    if not effective_ollama_host:
        # This import is tricky due to potential circular dependencies if not handled carefully.
        # Assuming run_complete_pipeline.py is in data_pipeline.
        from data_pipeline.run_complete_pipeline import DEFAULT_ENTITY_EXTRACTION_HOST
        effective_ollama_host = DEFAULT_ENTITY_EXTRACTION_HOST
        logger.info(f"No --ollama-host provided, using default from run_complete_pipeline: {effective_ollama_host}")

    result = run_entity_extraction(logger, str(input_file_path), str(output_dir_path), effective_ollama_host)

    if result.get("status") == "success":
        logger.info(f"Successfully processed {input_file_path}. Output: {result.get('output_file')}")
    else:
        logger.error(f"Failed to process {input_file_path}. Error: {result.get('error')}")

if __name__ == "__main__":
    # Need to import Path here if it's used, or ensure it's imported globally in the script.
    from pathlib import Path # Ensure Path is available in this scope if used by main directly.
    main() # Call the new main function
