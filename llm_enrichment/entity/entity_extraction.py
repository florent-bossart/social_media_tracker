"""
Entity Extraction Module for Japanese Music Social Media Data
"""

import json
import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

from .entity_extraction_config import (
    EntityExtractionConfig # Import the class
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicEntityExtractor:
    def __init__(self, config: EntityExtractionConfig, ollama_host: Optional[str] = None): # MODIFIED: Added ollama_host
        self.config = config
        self.ollama_url = f"{ollama_host or self.config.OLLAMA_BASE_URL}/api/generate" # MODIFIED: Use ollama_host if provided
        self.model = self.config.OLLAMA_MODEL

    def call_ollama(self, prompt: str) -> Optional[Dict]:
        """Call Ollama API with retry logic"""
        logger.debug(f"Calling Ollama with prompt: {prompt[:200]}...") # Log prompt
        headers = {
            "ngrok-skip-browser-warning": "true"
        }
        for attempt in range(self.config.MAX_RETRIES):
            try:
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=120,  # Increased timeout for slow model
                    headers=headers # Add the ngrok bypass header
                )
                response.raise_for_status()

                # Log raw response text
                raw_response_text = response.text
                logger.debug(f"Ollama raw response text (attempt {attempt + 1}): {raw_response_text}")

                result = response.json()
                logger.debug(f"Ollama response JSON (attempt {attempt + 1}): {result}")

                if 'response' in result and result['response']:
                    try:
                        parsed_response = json.loads(result['response'])
                        logger.debug(f"Ollama parsed 'response' field: {parsed_response}")
                        return parsed_response
                    except json.JSONDecodeError as e:
                        logger.error(f"JSONDecodeError parsing 'response' field: {result['response']}. Error: {e}")
                        return None # Explicitly return None on JSON parsing error of the 'response' field
                else:
                    logger.error(f"Unexpected response format or empty 'response' field: {result}")
                    return None

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All attempts failed for prompt")
                    return None
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(1)
                else:
                    logger.error("Failed to parse JSON response")
                    return None

        return None

    def extract_entities_from_text(self, text: str, platform: str) -> Dict:
        """Extract entities from a single text using LLM"""
        if not text or text.strip() == "":
            logger.info("Empty text provided, returning empty entities.")
            return self._empty_entities()

        prompt = self.config.ENTITY_EXTRACTION_PROMPT.format( # Use config for prompt
            text=text.replace('"', '\\"')  # Escape quotes
        )
        logger.debug(f"Generated prompt for entity extraction: {prompt[:200]}...")

        entities = self.call_ollama(prompt)

        if entities is None:
            logger.warning(f"Failed to extract entities or got None from call_ollama for text: {text[:50]}...")
            return self._empty_entities()

        logger.debug(f"Entities received from call_ollama: {entities}")
        # Validate and clean entities
        return self._validate_entities(entities)

    def _empty_entities(self) -> Dict:
        """Return empty entity structure"""
        return {
            "artists": [],
            "songs": [],
            "genres": [],
            "song_indicators": [],
            "sentiment_indicators": [],
            "music_events": [],
            "temporal_references": [],
            "other_entities": []
        }

    def _validate_entities(self, entities: Dict) -> Dict:
        """Validate and clean extracted entities"""
        validated = self._empty_entities()

        for key in validated.keys():
            if key in entities and isinstance(entities[key], list):
                # Clean and deduplicate
                cleaned = []
                for item in entities[key]:
                    if isinstance(item, str) and item.strip():
                        cleaned.append(item.strip())
                validated[key] = list(set(cleaned))  # Remove duplicates

        return validated

    def calculate_confidence(self, entities: Dict, text: str) -> float:
        """Calculate confidence score based on known entities and text match"""
        score = 0.0
        total_checks = 0

        # Check artists against known list
        for artist in entities.get('artists', []):
            total_checks += 1
            if any(known.lower() in artist.lower() or artist.lower() in known.lower()
                   for known in self.config.KNOWN_ARTISTS): # Use config for KNOWN_ARTISTS
                score += 1.0
            elif artist.lower() in text.lower():
                score += 0.8

        # Check genres against known list
        for genre in entities.get('genres', []):
            total_checks += 1
            if any(known.lower() in genre.lower() or genre.lower() in known.lower()
                   for known in self.config.KNOWN_GENRES): # Use config for KNOWN_GENRES
                score += 1.0
            elif genre.lower() in text.lower():
                score += 0.8

        # Check if other entities appear in text
        for entity_type in ['songs', 'song_indicators', 'sentiment_indicators',
                           'music_events', 'temporal_references', 'other_entities']:
            for entity in entities.get(entity_type, []):
                total_checks += 1
                if entity.lower() in text.lower():
                    score += 0.9

        return score / max(total_checks, 1)

    def process_batch(self, batch_df: pd.DataFrame, platform: str) -> List[Dict]:
        """Process a batch of comments"""
        results = []
        logger.info(f"Processing batch_df with {len(batch_df)} rows for platform {platform}.")
        if batch_df.empty:
            logger.warning("batch_df is empty. Returning empty results for this batch.")
            return results

        # Determine text source columns based on platform
        if platform == "youtube":
            text_sources = ['comment_text_en_nllb', 'comment_text']
            id_column = 'comment_pk' # As per CSV fields
            date_column = 'comment_published_at' # As per CSV fields
        elif platform == "reddit":
            text_sources = ['body_clean']
            id_column = 'comment_id' # As per CSV fields
            date_column = 'created_utc_fmt' # As per CSV fields
        else:
            logger.error(f"Unknown platform: {platform}. Cannot determine text source columns.")
            text_sources = [] # Default to empty, will skip rows
            id_column = 'id' # Fallback
            date_column = 'date' # Fallback

        logger.info(f"Using text sources: {text_sources}, id_column: {id_column}, date_column: {date_column} for platform: {platform}")


        for idx, row in batch_df.iterrows():
            try:
                text = None
                for source_col in text_sources:
                    if source_col in row:
                        cell_value = row[source_col]
                        if pd.notna(cell_value):
                            if isinstance(cell_value, str) and cell_value.strip():
                                text = cell_value
                                logger.debug(f"Row {idx}: Found text in column '{source_col}': '{text[:100]}...'")
                                break
                            else:
                                logger.debug(f"Row {idx}: Column '{source_col}' in row. Value: '{str(cell_value)[:50]}...'. It is either not a string or empty after strip.")
                        else:
                            logger.debug(f"Row {idx}: Column '{source_col}' in row, but its value is NA/NaN.")
                    else:
                        logger.debug(f"Row {idx}: Column '{source_col}' not found in row. Available columns: {list(row.index)}")

                if not text:
                    logger.warning(f"Row {idx}: No non-empty text found in any of the tried source columns: {text_sources}. Skipping row. Row data (first 5 columns): {row.head().to_dict()}")
                    continue

                logger.debug(f"Row {idx}: Processing text: '{text[:100]}...'")
                entities = self.extract_entities_from_text(text, platform)
                logger.debug(f"Row {idx}: Extracted entities: {entities}")
                confidence = self.calculate_confidence(entities, text)
                logger.debug(f"Row {idx}: Calculated confidence: {confidence}")

                # Create result record
                # Use platform-specific or default ID and date columns
                record_id = row.get(id_column, idx)
                source_date = row.get(date_column, '')

                result = {
                    'id': record_id,
                    'source_platform': platform,
                    'original_text': text, # This will be the text found (either original or translated)
                    'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                    'source_date': source_date,
                    'confidence_score': confidence,
                    **self._flatten_entities(entities)
                }
                logger.debug(f"Row {idx}: Created result record: {result}")

                results.append(result)

                # Log progress
                if len(results) % 10 == 0: # Log every 10, or adjust as needed
                    logger.info(f"Processed {len(results)}/{len(batch_df)} comments from current batch (Platform: {platform})")

                # Small delay to avoid overwhelming Ollama
                time.sleep(self.config.OLLAMA_REQUEST_DELAY) # Use config for delay

            except Exception as e:
                logger.error(f"Error processing row {idx} (text: '{text[:50]}...'): {e}", exc_info=True)
                continue

        logger.info(f"Finished processing batch for platform {platform}. Total results in this batch: {len(results)}")
        return results

    def _flatten_entities(self, entities: Dict) -> Dict:
        """Flatten entities for CSV storage"""
        flattened = {}

        for entity_type, entity_list in entities.items():
            if entity_list:
                # Store as JSON string for CSV
                flattened[f'entities_{entity_type}'] = json.dumps(entity_list)
                flattened[f'entities_{entity_type}_count'] = len(entity_list)
            else:
                flattened[f'entities_{entity_type}'] = ''
                flattened[f'entities_{entity_type}_count'] = 0

        return flattened

    def save_results(self, results: List[Dict], output_path: str):
        """Save extraction results to CSV"""
        logger.info(f"Attempting to save results to {output_path}")
        if not results:
            logger.warning(f"No results to save for {output_path}. Results list is empty.")
            return

        try:
            df = pd.DataFrame(results)
            logger.info(f"Created DataFrame with {len(df)} rows to save to {output_path}")

            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {Path(output_path).parent}")

            # Save to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully saved {len(results)} entity extractions to {output_path}")
        except Exception as e:
            logger.error(f"Error during save_results to {output_path}: {e}", exc_info=True)
            # Optionally, re-raise the exception if you want the pipeline to hard stop here
            # raise

    def process_file(self, input_path: str, platform: str, date: str) -> str:
        """Process a single input file"""
        logger.info(f"Starting process_file for {platform} data from {input_path} for date {date}")

        if not Path(input_path).exists():
            logger.error(f"Input file not found: {input_path}")
            return None

        # Load data
        try:
            df = pd.read_csv(input_path)
            logger.info(f"Loaded {len(df)} comments from {input_path}")
            if df.empty:
                logger.warning(f"Input file {input_path} is empty. No data to process.")
                # Save an empty result file to avoid downstream errors if that's the desired behavior
                # or return None/error appropriately.
                output_path = self.config.OUTPUT_PATH_ENTITIES.format(date=date, platform=platform)
                self.save_results([], output_path) # Save empty results
                return output_path # Return path to empty file
        except pd.errors.EmptyDataError:
            logger.error(f"Input file {input_path} is empty or malformed (EmptyDataError).")
            output_path = self.config.OUTPUT_PATH_ENTITIES.format(date=date, platform=platform)
            self.save_results([], output_path) # Save empty results
            return output_path
        except Exception as e:
            logger.error(f"Failed to load or parse CSV {input_path}: {e}", exc_info=True)
            return None


        # Process in batches
        all_results = []
        total_batches = (len(df) + self.config.BATCH_SIZE - 1) // self.config.BATCH_SIZE # Use config for BATCH_SIZE
        logger.info(f"Total batches to process: {total_batches} for {len(df)} rows with batch size {self.config.BATCH_SIZE}")

        for i in range(0, len(df), self.config.BATCH_SIZE): # Use config for BATCH_SIZE
            batch_num = (i // self.config.BATCH_SIZE) + 1
            logger.info(f"Processing batch {batch_num}/{total_batches}")

            batch_df = df.iloc[i:i + self.config.BATCH_SIZE]
            logger.info(f"Batch {batch_num}: processing {len(batch_df)} rows.")

            batch_results = self.process_batch(batch_df, platform)
            logger.info(f"Batch {batch_num}: received {len(batch_results)} results from process_batch.")

            if batch_results: # Only extend if there are results
                all_results.extend(batch_results)
            logger.info(f"Batch {batch_num}: all_results now contains {len(all_results)} total items.")

        # Save results
        output_path = self.config.OUTPUT_PATH_ENTITIES.format(date=date, platform=platform) # Use config for OUTPUT_PATH_ENTITIES
        logger.info(f"Finished processing all batches for {input_path}. Total results to save: {len(all_results)}")
        self.save_results(all_results, output_path)

        return output_path

def combine_platform_results(date: str, config: EntityExtractionConfig) -> str: # Add config parameter
    """Combine YouTube and Reddit entity extractions"""
    logger.info("Combining platform results")

    youtube_path = config.OUTPUT_PATH_ENTITIES.format(date=date, platform="youtube") # Use config
    reddit_path = config.OUTPUT_PATH_ENTITIES.format(date=date, platform="reddit") # Use config
    combined_path = config.OUTPUT_PATH_COMBINED.format(date=date) # Use config

    dfs = []

    if Path(youtube_path).exists():
        youtube_df = pd.read_csv(youtube_path)
        dfs.append(youtube_df)
        logger.info(f"Loaded {len(youtube_df)} YouTube entities")

    if Path(reddit_path).exists():
        reddit_df = pd.read_csv(reddit_path)
        dfs.append(reddit_df)
        logger.info(f"Loaded {len(reddit_df)} Reddit entities")

    if not dfs:
        logger.error("No platform data found to combine")
        return None

    # Combine and save
    combined_df = pd.concat(dfs, ignore_index=True)

    # Ensure output directory exists
    Path(combined_path).parent.mkdir(parents=True, exist_ok=True)

    combined_df.to_csv(combined_path, index=False)
    logger.info(f"Saved {len(combined_df)} combined entities to {combined_path}")

    return combined_path

def main(date: str = None):
    """Main entry point for entity extraction"""
    if date is None:
        date = datetime.now().strftime('%Y%m%d')

    logger.info(f"Starting entity extraction for date: {date}")
    config = EntityExtractionConfig() # Create config instance
    extractor = MusicEntityExtractor(config) # Pass config to constructor

    # Process YouTube data
    youtube_input = config.INPUT_PATH_YOUTUBE.format(date=date) # Use config
    youtube_output = extractor.process_file(youtube_input, "youtube", date)

    # Process Reddit data
    reddit_input = config.INPUT_PATH_REDDIT.format(date=date) # Use config
    reddit_output = extractor.process_file(reddit_input, "reddit", date)

    # Combine results
    combined_output = combine_platform_results(date, config) # Pass config

    logger.info("Entity extraction completed")
    logger.info(f"Outputs: {youtube_output}, {reddit_output}, {combined_output}")

if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else None
    main(date)
