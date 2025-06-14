import os
import glob
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm
import re
import torch
import argparse
import sys
from datetime import datetime

torch.set_num_threads(2)  # or 1

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
    model_name = "facebook/nllb-200-distilled-600M"
    print("Loading NLLB model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("Tokenizer loaded.")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    print("Model loaded.")
    return tokenizer, model

def translate(texts, tokenizer, model, batch_size=4, src_lang="jpn_Jpan", tgt_lang="eng_Latn"):
    translated = []
    tokenizer.src_lang = src_lang
    for i in tqdm(range(0, len(texts), batch_size), desc="Translating"):
        batch = texts[i:i+batch_size]
        # NLLB requires forced BOS (beginning-of-sentence) token for target language
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
        # prepare forced_bos_token_id
        bos_token_id = tokenizer.convert_tokens_to_ids(tgt_lang)
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=bos_token_id
        )
        translated += [tokenizer.decode(t, skip_special_tokens=True) for t in outputs]
    return translated

def process_file(input_path, column_to_translate, output_column, output_dir, tokenizer, model):
    print(f"\nProcessing file: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} rows")
    print(f"Columns available: {list(df.columns)}")

    if column_to_translate not in df.columns:
        print(f"❌ Error: Column '{column_to_translate}' not found in file!")
        print(f"Available columns: {list(df.columns)}")
        return None

    # Find Japanese text
    jp_mask = df[column_to_translate].apply(lambda x: bool(str(x).strip()) and maybe_is_japanese(x))
    indices = df.index[jp_mask].tolist()
    texts_to_translate = df.loc[indices, column_to_translate].astype(str).tolist()

    print(f"Found {len(texts_to_translate)} Japanese texts to translate out of {len(df)} total rows")

    # Only translate non-empty Japanese text
    if texts_to_translate:
        print(f"Translating {len(texts_to_translate)} texts...")
        translations = translate(texts_to_translate, tokenizer, model)
        # Initialize new column as original (or empty)
        df[output_column] = ""
        # Fill in only translated rows
        for idx, trans in zip(indices, translations):
            df.at[idx, output_column] = trans
    else:
        print("No Japanese text found to translate")
        df[output_column] = ""

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Create output filename (_nllb_translated.csv)
    filename = os.path.basename(input_path).replace(".csv", "_nllb_translated.csv")
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False, quoting=1, quotechar='"')  # Maintain proper CSV quoting
    print(f"✅ NLLB translated file saved to: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(
        description='Translate Japanese YouTube comments to English using NLLB model'
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
        default='comment_clean',
        help='Column name containing text to translate (default: comment_clean)'
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

    try:
        # Load the translation model
        tokenizer, model = load_translation_model()

        if args.input_file:
            # Process a specific file
            if not os.path.exists(args.input_file):
                print(f"❌ Error: File {args.input_file} does not exist!")
                sys.exit(1)

            output_path = process_file(
                args.input_file,
                args.column,
                args.output_column,
                args.output_dir,
                tokenizer,
                model
            )
            if output_path:
                print(f"\n🎉 Translation completed! Output: {output_path}")
        else:
            # Process files matching pattern
            search_pattern = os.path.join("data/intermediate/Cleaned_data", args.input_pattern)
            youtube_files = glob.glob(search_pattern)

            if not youtube_files:
                print(f"❌ No files found matching pattern: {search_pattern}")
                print("\nAvailable files in data/intermediate/Cleaned_data/:")
                available_files = glob.glob("data/intermediate/Cleaned_data/*.csv")
                for f in available_files:
                    print(f"  - {os.path.basename(f)}")
                sys.exit(1)

            print(f"Found {len(youtube_files)} files to process:")
            for file in youtube_files:
                print(f"  - {os.path.basename(file)}")

            processed_files = []
            if args.latest_only:
                # Find and process only the latest file
                latest_file = find_latest_file(youtube_files)
                if latest_file:
                    print(f"Processing the latest file: {os.path.basename(latest_file)}")
                    output_path = process_file(
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
                    output_path = process_file(
                        file,
                        args.column,
                        args.output_column,
                        args.output_dir,
                        tokenizer,
                        model
                    )
                    if output_path:
                        processed_files.append(output_path)

            print(f"\n🎉 Translation completed! Processed {len(processed_files)} files:")
            for f in processed_files:
                print(f"  - {f}")

    except Exception as e:
        print(f"❌ Error during translation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
