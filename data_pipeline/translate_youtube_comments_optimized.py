import os
import gc
import glob
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm
import re
import torch
import argparse
import sys
from datetime import datetime
import psutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set PyTorch to use minimal threads to reduce memory pressure
torch.set_num_threads(1)

def log_memory_usage(stage=""):
    """Log current memory usage"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    logger.info(f"Memory usage {stage}: {memory_mb:.1f} MB")
    return memory_mb

def maybe_is_japanese(text):
    return bool(re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9faf]', str(text)))

def find_latest_file(file_list):
    """Find the latest file by extracting date from filename (YYYYMMDD format)"""
    if not file_list:
        return None

    # Extract date from filename and sort
    def extract_date(filepath):
        filename = os.path.basename(filepath)
        # Look for YYYYMMDD pattern at the start of filename
        date_match = re.match(r'(\d{8})', filename)
        if date_match:
            return date_match.group(1)
        return "00000000"  # fallback for files without date

    # Sort files by date (latest first) and return the first one
    sorted_files = sorted(file_list, key=extract_date, reverse=True)
    return sorted_files[0]

def load_translation_model():
    """Load translation model with memory optimization"""
    model_name = "facebook/nllb-200-distilled-600M"
    logger.info("Loading NLLB model...")
    log_memory_usage("before model loading")

    # Enable memory efficient loading
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    logger.info("Tokenizer loaded.")

    # Load model with memory optimization
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        low_cpu_mem_usage=True
    )
    logger.info("Model loaded.")

    # Move to GPU if available
    if torch.cuda.is_available():
        model = model.cuda()
        logger.info("Model moved to GPU")

    log_memory_usage("after model loading")
    return tokenizer, model

def translate_batch(texts, tokenizer, model, src_lang="jpn_Jpan", tgt_lang="eng_Latn"):
    """Translate a batch of texts with memory optimization"""
    tokenizer.src_lang = src_lang

    # NLLB requires forced BOS (beginning-of-sentence) token for target language
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Move inputs to same device as model
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    # prepare forced_bos_token_id
    bos_token_id = tokenizer.convert_tokens_to_ids(tgt_lang)

    with torch.no_grad():  # Disable gradient computation to save memory
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=bos_token_id,
            max_new_tokens=512,
            do_sample=False,
            num_beams=1  # Use greedy decoding to save memory
        )

    # Decode outputs
    translations = [tokenizer.decode(t, skip_special_tokens=True) for t in outputs]

    # Clean up GPU memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return translations

def translate_with_chunking(texts, tokenizer, model, chunk_size=2, batch_size=1, src_lang="jpn_Jpan", tgt_lang="eng_Latn"):
    """Translate texts in small chunks to manage memory"""
    all_translations = []

    logger.info(f"Translating {len(texts)} texts in chunks of {chunk_size} with batch size {batch_size}")

    for chunk_start in tqdm(range(0, len(texts), chunk_size), desc="Processing chunks"):
        chunk_end = min(chunk_start + chunk_size, len(texts))
        chunk_texts = texts[chunk_start:chunk_end]

        # Process chunk in smaller batches
        chunk_translations = []
        for batch_start in range(0, len(chunk_texts), batch_size):
            batch_end = min(batch_start + batch_size, len(chunk_texts))
            batch_texts = chunk_texts[batch_start:batch_end]

            try:
                batch_translations = translate_batch(batch_texts, tokenizer, model, src_lang, tgt_lang)
                chunk_translations.extend(batch_translations)
            except Exception as e:
                logger.error(f"Error translating batch: {e}")
                # Add empty translations for failed batch
                chunk_translations.extend([""] * len(batch_texts))

        all_translations.extend(chunk_translations)

        # Force garbage collection after each chunk
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Log memory usage periodically
        if chunk_start % (chunk_size * 10) == 0:
            log_memory_usage(f"after chunk {chunk_start // chunk_size + 1}")

    return all_translations

def process_file_in_chunks(input_path, column_to_translate, output_column, output_dir, tokenizer, model, chunk_size=100):
    """Process file in chunks to manage memory usage"""
    logger.info(f"Processing file: {input_path}")
    log_memory_usage("before file processing")

    # Read CSV in chunks to manage memory
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return None

    logger.info(f"Loaded {len(df)} rows")
    logger.info(f"Columns available: {list(df.columns)}")

    if column_to_translate not in df.columns:
        logger.error(f"Column '{column_to_translate}' not found in file!")
        logger.error(f"Available columns: {list(df.columns)}")
        return None

    # Find Japanese text
    logger.info("Identifying Japanese text...")
    jp_mask = df[column_to_translate].apply(lambda x: bool(str(x).strip()) and maybe_is_japanese(x))
    indices = df.index[jp_mask].tolist()
    texts_to_translate = df.loc[indices, column_to_translate].astype(str).tolist()

    logger.info(f"Found {len(texts_to_translate)} Japanese texts to translate out of {len(df)} total rows")

    # Initialize translation column
    df[output_column] = ""

    # Only translate if there are Japanese texts
    if texts_to_translate:
        logger.info(f"Starting translation of {len(texts_to_translate)} texts...")
        log_memory_usage("before translation")

        # Use smaller chunks and batch sizes for memory efficiency
        memory_mb = log_memory_usage("current")

        # Adjust chunk and batch sizes based on available memory and data size
        if len(texts_to_translate) > 10000:
            chunk_size = 50  # Very small chunks for large datasets
            batch_size = 1   # Single item batches
        elif len(texts_to_translate) > 5000:
            chunk_size = 100
            batch_size = 1
        else:
            chunk_size = 200
            batch_size = 2

        logger.info(f"Using chunk_size={chunk_size}, batch_size={batch_size}")

        translations = translate_with_chunking(
            texts_to_translate,
            tokenizer,
            model,
            chunk_size=chunk_size,
            batch_size=batch_size
        )

        # Fill in translations
        for idx, trans in zip(indices, translations):
            df.at[idx, output_column] = trans

        log_memory_usage("after translation")
    else:
        logger.info("No Japanese text found to translate")

    # Standardize column names for entity extraction compatibility
    if 'text_clean' in df.columns and 'comment_text' not in df.columns:
        df = df.rename(columns={'text_clean': 'comment_text'})
        logger.info("Renamed 'text_clean' to 'comment_text' for compatibility")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create output filename
    filename = os.path.basename(input_path).replace(".csv", "_nllb_translated.csv")
    output_path = os.path.join(output_dir, filename)

    # Save with proper CSV handling
    try:
        df.to_csv(output_path, index=False, quoting=1, quotechar='"')
        logger.info(f"✅ NLLB translated file saved to: {output_path}")
        logger.info(f"Final columns: {list(df.columns)}")
        log_memory_usage("after saving")
        return output_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

def cleanup_model(model, tokenizer):
    """Clean up model memory"""
    logger.info("Cleaning up model memory...")
    del model
    del tokenizer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    log_memory_usage("after cleanup")

def main():
    parser = argparse.ArgumentParser(
        description='Translate Japanese YouTube comments to English using NLLB model (Memory Optimized)'
    )
    parser.add_argument(
        '--input-file',
        type=str,
        help='Specific input file to translate',
        required=False
    )
    parser.add_argument(
        '--input-pattern',
        type=str,
        default='*youtube_comments_cleaned.csv',
        help='File pattern to search for in data/intermediate/Cleaned_data/ (default: *youtube_comments_cleaned.csv)'
    )
    parser.add_argument(
        '--latest-only',
        action='store_true',
        help='Process only the latest file (by date in filename) matching the pattern'
    )
    parser.add_argument(
        '--column',
        type=str,
        default='comment_text',
        help='Column name containing text to translate (default: comment_text)'
    )
    parser.add_argument(
        '--output-column',
        type=str,
        default='comment_text_en_nllb',
        help='Name for the translated column (default: comment_text_en_nllb)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/intermediate/translated',
        help='Output directory (default: data/intermediate/translated)'
    )

    args = parser.parse_args()

    log_memory_usage("at start")

    try:
        # Load the translation model
        tokenizer, model = load_translation_model()

        if args.input_file:
            # Process a specific file
            if not os.path.exists(args.input_file):
                logger.error(f"File {args.input_file} does not exist!")
                sys.exit(1)

            output_path = process_file_in_chunks(
                args.input_file,
                args.column,
                args.output_column,
                args.output_dir,
                tokenizer,
                model
            )
            if output_path:
                logger.info(f"🎉 Translation completed! Output: {output_path}")
        else:
            # Process files matching pattern
            search_pattern = os.path.join("data/intermediate/Cleaned_data", args.input_pattern)
            youtube_files = glob.glob(search_pattern)

            if not youtube_files:
                logger.error(f"No files found matching pattern: {search_pattern}")
                logger.info("Available files in data/intermediate/Cleaned_data/:")
                available_files = glob.glob("data/intermediate/Cleaned_data/*.csv")
                for f in available_files:
                    logger.info(f"  - {os.path.basename(f)}")
                sys.exit(1)

            logger.info(f"Found {len(youtube_files)} files to process:")
            for file in youtube_files:
                logger.info(f"  - {os.path.basename(file)}")

            processed_files = []
            if args.latest_only:
                # Find and process only the latest file
                latest_file = find_latest_file(youtube_files)
                if latest_file:
                    logger.info(f"Processing the latest file: {os.path.basename(latest_file)}")
                    output_path = process_file_in_chunks(
                        latest_file,
                        args.column,
                        args.output_column,
                        args.output_dir,
                        tokenizer,
                        model
                    )
                    if output_path:
                        processed_files.append(output_path)
            else:
                for file in youtube_files:
                    output_path = process_file_in_chunks(
                        file,
                        args.column,
                        args.output_column,
                        args.output_dir,
                        tokenizer,
                        model
                    )
                    if output_path:
                        processed_files.append(output_path)

            logger.info(f"🎉 Translation completed! Processed {len(processed_files)} files:")
            for f in processed_files:
                logger.info(f"  - {f}")

    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")
        sys.exit(1)
    finally:
        # Always clean up model memory
        try:
            cleanup_model(model, tokenizer)
        except:
            pass

if __name__ == "__main__":
    main()
