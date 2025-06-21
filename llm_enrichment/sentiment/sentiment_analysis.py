"""
Sentiment Analysis Module for Japanese Music Social Media Data

This module performs sentiment analysis on social media comments about Japanese music,
integrating with entity extraction results and providing detailed sentiment insights.
"""

import json
import logging
import os
import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any # Ensure Optional is imported
import re

from .sentiment_analysis_config import (
    OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_TIMEOUT,
    SENTIMENT_ANALYSIS_CONFIG, SENTIMENT_ANALYSIS_PROMPTS,
    PROCESSING_CONFIG, OUTPUT_CONFIG, SENTIMENT_OUTPUT_DIR, SENTIMENT_LOG_FILE
)

# Ensure logs directory exists
os.makedirs(os.path.dirname(SENTIMENT_LOG_FILE), exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(SENTIMENT_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Sentiment Analysis class for Japanese music social media comments
    """

    def __init__(self, ollama_host: Optional[str] = None): # MODIFIED: Added ollama_host parameter
        """Initialize the sentiment analyzer"""
        self.model = OLLAMA_MODEL
        self.base_url = ollama_host if ollama_host else OLLAMA_BASE_URL # MODIFIED: Use ollama_host if provided
        self.timeout = OLLAMA_TIMEOUT
        self.sentiment_config = SENTIMENT_ANALYSIS_CONFIG
        self.prompts = SENTIMENT_ANALYSIS_PROMPTS

        # Create output directory if it doesn't exist
        Path(SENTIMENT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(SENTIMENT_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"SentimentAnalyzer initialized with model: {self.model}")

    def call_ollama_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Call Ollama API with retry logic

        Args:
            prompt: The prompt to send to the model
            max_retries: Maximum number of retry attempts

        Returns:
            Response text from the model or None if failed
        """
        for attempt in range(max_retries):
            try:
                logger.debug(f"Calling Ollama API (attempt {attempt + 1}/{max_retries})")

                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistent analysis
                            "top_p": 0.9,
                            "num_predict": 500
                        }
                    },
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    logger.warning(f"Ollama API returned status code: {response.status_code}")

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                time.sleep(PROCESSING_CONFIG["retry_delay"])

        logger.error(f"Failed to get response after {max_retries} attempts")
        return None

    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """
        Extract JSON from model response

        Args:
            response: Raw response from the model

        Returns:
            Parsed JSON dictionary or None if parsing failed
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")

        return None

    def analyze_basic_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Perform basic sentiment analysis using rule-based approach as fallback

        Args:
            text: Text to analyze

        Returns:
            Dictionary with basic sentiment analysis results
        """
        text_lower = text.lower()

        # Count sentiment indicators
        positive_count = sum(1 for word in self.sentiment_config["sentiment_categories"]["positive"]
                           if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_config["sentiment_categories"]["negative"]
                           if word in text_lower)

        # Determine overall sentiment
        if positive_count > negative_count:
            overall_sentiment = "positive"
            sentiment_strength = min(10, 5 + positive_count)
        elif negative_count > positive_count:
            overall_sentiment = "negative"
            sentiment_strength = min(10, 5 + negative_count)
        else:
            overall_sentiment = "neutral"
            sentiment_strength = 5

        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_strength": sentiment_strength,
            "confidence": 0.5,  # Lower confidence for rule-based
            "sentiment_aspects": {
                "artist_sentiment": "none",
                "music_quality_sentiment": "none",
                "performance_sentiment": "none",
                "personal_experience_sentiment": "none"
            },
            "emotional_indicators": [],
            "sentiment_reasoning": "Rule-based fallback analysis"
        }

    def analyze_sentiment_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Perform sentiment analysis using LLM

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment analysis results or None if failed
        """
        prompt = self.prompts["main_prompt"].format(text=text)

        response = self.call_ollama_api(prompt)
        if not response:
            logger.warning("Failed to get LLM response for sentiment analysis")
            return None

        sentiment_data = self.extract_json_from_response(response)
        if not sentiment_data:
            logger.warning("Failed to extract JSON from LLM response")
            return None

        # Validate required fields
        required_fields = ["overall_sentiment", "sentiment_strength", "confidence"]
        if not all(field in sentiment_data for field in required_fields):
            logger.warning("Missing required fields in sentiment analysis response")
            return None

        return sentiment_data

    def analyze_comparative_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze comparative sentiment in text (e.g., "X is better than Y")

        Args:
            text: Text to analyze

        Returns:
            Dictionary with comparative sentiment analysis or None
        """
        # Check if text contains comparison indicators
        comparison_indicators = ["better than", "worse than", "vs", "compared to", "over", "instead of"]
        if not any(indicator in text.lower() for indicator in comparison_indicators):
            return None

        prompt = self.prompts["comparative_sentiment_prompt"].format(text=text)

        response = self.call_ollama_api(prompt)
        if not response:
            return None

        comparative_data = self.extract_json_from_response(response)
        return comparative_data

    def calculate_confidence_score(self, sentiment_data: Dict[str, Any], text: str) -> float:
        """
        Calculate confidence score for sentiment analysis

        Args:
            sentiment_data: Sentiment analysis results
            text: Original text

        Returns:
            Confidence score between 0 and 1
        """
        base_confidence = sentiment_data.get("confidence", 0.5)

        # Adjust confidence based on text length
        text_length = len(text.split())
        if text_length < 5:
            length_penalty = 0.2
        elif text_length > 50:
            length_penalty = 0.1
        else:
            length_penalty = 0.0

        # Adjust confidence based on sentiment strength
        sentiment_strength = sentiment_data.get("sentiment_strength", 5)
        if sentiment_strength in [1, 2, 9, 10]:  # Very strong sentiments
            strength_boost = 0.1
        else:
            strength_boost = 0.0

        final_confidence = max(0.0, min(1.0, base_confidence - length_penalty + strength_boost))
        return final_confidence

    def process_comments_batch(self, comments_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process a batch of comments for sentiment analysis using bulk processing

        Args:
            comments_df: DataFrame with comments to analyze

        Returns:
            DataFrame with sentiment analysis results
        """
        results = []

        # Prepare data for bulk analysis
        texts_for_analysis = []
        valid_rows = []

        for idx, row in comments_df.iterrows():
            text = row.get('original_text', '') or row.get('translated_text', '')
            if text and str(text).strip():
                texts_for_analysis.append({
                    'id': row.get('id', idx),
                    'text': str(text).strip(),
                    'row': row
                })
                valid_rows.append(row)
            else:
                logger.warning(f"No valid text found for row {idx}")

        if not texts_for_analysis:
            logger.warning("No valid texts found for processing")
            return pd.DataFrame()

        # Process in bulk chunks
        bulk_size = PROCESSING_CONFIG.get("bulk_size", 10)
        total_comments = len(texts_for_analysis)

        logger.info(f"Processing {total_comments} comments in chunks of {bulk_size}")

        for i in range(0, total_comments, bulk_size):
            chunk = texts_for_analysis[i:i+bulk_size]
            chunk_size = len(chunk)

            logger.info(f"Processing bulk chunk {i//bulk_size + 1}: comments {i+1}-{i+chunk_size}")

            # Prepare bulk data
            texts_with_ids = [{'id': item['id'], 'text': item['text']} for item in chunk]

            # Try bulk LLM analysis
            bulk_results = self.analyze_sentiment_bulk(texts_with_ids)

            # Create a mapping of IDs to bulk results
            bulk_results_map = {}
            if bulk_results and len(bulk_results) == chunk_size:
                for result in bulk_results:
                    bulk_results_map[result.get('comment_id')] = result
                logger.info(f"Bulk analysis succeeded for {len(bulk_results)} comments in chunk")
            else:
                logger.info(f"Bulk analysis failed or incomplete for chunk (got {len(bulk_results) if bulk_results else 0} results for {chunk_size} comments)")

            # Process each comment in the chunk
            for item in chunk:
                comment_id = item['id']
                text = item['text']
                row = item['row']

                # Try to get result from bulk analysis
                if comment_id in bulk_results_map:
                    bulk_sentiment = bulk_results_map[comment_id]
                    sentiment_data = {
                        'overall_sentiment': bulk_sentiment.get('overall_sentiment', 'neutral'),
                        'sentiment_strength': bulk_sentiment.get('sentiment_strength', 5),
                        'confidence': bulk_sentiment.get('confidence', 0.7),
                        'sentiment_aspects': bulk_sentiment.get('sentiment_aspects', {}),
                        'emotional_indicators': bulk_sentiment.get('emotional_indicators', []),
                        'sentiment_reasoning': bulk_sentiment.get('sentiment_reasoning', 'Bulk LLM analysis')
                    }
                else:
                    # Fallback to individual LLM analysis
                    sentiment_data = self.analyze_sentiment_llm(text)

                    # Final fallback to rule-based if individual LLM also fails
                    if not sentiment_data:
                        logger.info(f"Using rule-based fallback for comment {comment_id}")
                        sentiment_data = self.analyze_basic_sentiment(text)

                # Analyze comparative sentiment if enabled (still individual for now)
                comparative_data = None
                if PROCESSING_CONFIG["enable_comparative_analysis"]:
                    comparative_data = self.analyze_comparative_sentiment(text)

                # Calculate final confidence
                final_confidence = self.calculate_confidence_score(sentiment_data, text)

                # Prepare result row
                result_row = {
                    'id': comment_id,
                    'source_platform': row.get('source_platform', 'unknown'),
                    'original_text': text,
                    'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                    'overall_sentiment': sentiment_data.get('overall_sentiment', 'neutral'),
                    'sentiment_strength': sentiment_data.get('sentiment_strength', 5),
                    'confidence_score': final_confidence,
                    'sentiment_reasoning': sentiment_data.get('sentiment_reasoning', ''),

                    # Aspect sentiments
                    'artist_sentiment': sentiment_data.get('sentiment_aspects', {}).get('artist_sentiment', 'none'),
                    'music_quality_sentiment': sentiment_data.get('sentiment_aspects', {}).get('music_quality_sentiment', 'none'),
                    'performance_sentiment': sentiment_data.get('sentiment_aspects', {}).get('performance_sentiment', 'none'),
                    'personal_experience_sentiment': sentiment_data.get('sentiment_aspects', {}).get('personal_experience_sentiment', 'none'),

                    # Emotional indicators
                    'emotional_indicators': json.dumps(sentiment_data.get('emotional_indicators', [])),
                    'emotional_indicators_count': len(sentiment_data.get('emotional_indicators', [])),

                    # Comparative analysis
                    'has_comparison': comparative_data is not None,
                    'comparison_type': comparative_data.get('comparison_type', '') if comparative_data else '',
                    'favorable_entities': json.dumps(comparative_data.get('favorable_entities', [])) if comparative_data else '',
                    'unfavorable_entities': json.dumps(comparative_data.get('unfavorable_entities', [])) if comparative_data else '',
                    'comparison_sentiment': comparative_data.get('comparison_sentiment', '') if comparative_data else ''
                }

                results.append(result_row)

            # Small delay between bulk chunks to prevent overwhelming the API
            if i + bulk_size < total_comments:
                time.sleep(0.5)  # Reduced delay since we're processing in bulk

        return pd.DataFrame(results)

    def save_results(self, results_df: pd.DataFrame, output_filename: str) -> str:
        """
        Save sentiment analysis results to CSV

        Args:
            results_df: DataFrame with results
            output_filename: Name for the output file

        Returns:
            Path to the saved file
        """
        output_path = Path(SENTIMENT_OUTPUT_DIR) / output_filename

        # Ensure all columns are properly formatted for PostgreSQL
        for col in results_df.columns:
            if results_df[col].dtype == 'object':
                results_df[col] = results_df[col].astype(str).replace('nan', '')

        results_df.to_csv(output_path, index=False)
        logger.info(f"Sentiment analysis results saved to: {output_path}")

        return str(output_path)

    def analyze_file(self, input_file_path: str, output_filename: Optional[str] = None) -> str:
        """
        Analyze sentiment for all comments in a file

        Args:
            input_file_path: Path to input CSV file
            output_filename: Optional custom output filename

        Returns:
            Path to the output file
        """
        logger.info(f"Starting sentiment analysis for file: {input_file_path}")

        # Load input data
        df = pd.read_csv(input_file_path)
        logger.info(f"Loaded {len(df)} rows for sentiment analysis")

        # Generate output filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{timestamp}_sentiment_analysis.csv"

        # Process in batches
        batch_size = PROCESSING_CONFIG["batch_size"]
        all_results = []

        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} (rows {i+1}-{min(i+batch_size, len(df))})")

            batch_results = self.process_comments_batch(batch_df)
            all_results.append(batch_results)

        # Combine all results
        final_results = pd.concat(all_results, ignore_index=True)

        # Save results
        output_path = self.save_results(final_results, output_filename)

        # Log summary statistics
        sentiment_counts = final_results['overall_sentiment'].value_counts()
        logger.info(f"Sentiment analysis complete. Results summary:")
        for sentiment, count in sentiment_counts.items():
            logger.info(f"  {sentiment}: {count} ({count/len(final_results)*100:.1f}%)")

        avg_confidence = final_results['confidence_score'].mean()
        logger.info(f"Average confidence score: {avg_confidence:.3f}")

        return output_path

    def analyze_sentiment_bulk(self, comments_list: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """
        Perform bulk sentiment analysis using LLM for multiple comments at once

        Args:
            comments_list: List of comment dictionaries with 'id' and 'text' keys

        Returns:
            List of sentiment analysis results or None if failed
        """
        if not comments_list:
            return []

        # Format comments for the bulk prompt
        formatted_comments = []
        for i, comment in enumerate(comments_list):
            comment_id = comment.get('id', f'comment_{i+1}')
            text = comment.get('text', '')
            formatted_comments.append(f"Comment ID: {comment_id}\nText: {text}\n")

        comments_text = "\n".join(formatted_comments)
        prompt = self.prompts["bulk_prompt"].format(comments=comments_text)

        response = self.call_ollama_api(prompt, max_retries=2)  # Fewer retries for bulk to fail fast
        if not response:
            logger.warning("Failed to get LLM response for bulk sentiment analysis")
            return None

        # DEBUG: Log the raw response to understand the format
        logger.info(f"Raw bulk analysis response: {response[:500]}...")

        # Try to extract JSON array from response
        try:
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                logger.info(f"Extracted JSON string: {json_str[:200]}...")
                bulk_results = json.loads(json_str)

                # Validate that we got results for all comments
                if isinstance(bulk_results, list) and len(bulk_results) == len(comments_list):
                    logger.info(f"Bulk analysis successful: {len(bulk_results)} results")
                    return bulk_results
                else:
                    logger.warning(f"Bulk analysis returned {len(bulk_results) if isinstance(bulk_results, list) else 0} results, expected {len(comments_list)}")
                    return None
            else:
                logger.warning("No JSON array found in bulk analysis response")
                return None

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from bulk analysis response: {e}")
            logger.info(f"Problematic JSON: {json_str[:300] if 'json_str' in locals() else 'N/A'}...")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing bulk analysis response: {e}")
            return None

def main():
    """Main function for testing sentiment analysis"""
    analyzer = SentimentAnalyzer()

    # Test with a sample
    test_text = "YOASOBI is amazing! I love their music so much, especially Yoru ni Kakeru. Best J-pop duo ever!"

    print("Testing sentiment analysis...")
    result = analyzer.analyze_sentiment_llm(test_text)

    if result:
        print("LLM Analysis Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("LLM analysis failed, trying rule-based:")
        result = analyzer.analyze_basic_sentiment(test_text)
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
