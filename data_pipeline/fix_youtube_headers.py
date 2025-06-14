#!/usr/bin/env python3
"""
Fix CSV column headers for YouTube translated files to match entity extraction expectations.
Renames:
- text_clean → comment_text
- text_clean_en_nllb → comment_text_en_nllb
"""

import pandas as pd
import argparse
import os
import sys

def fix_headers(input_file, output_file=None):
    """Fix column headers in the translated YouTube CSV file"""

    if not os.path.exists(input_file):
        print(f"❌ Error: Input file {input_file} does not exist!")
        return False

    print(f"📖 Reading file: {input_file}")
    df = pd.read_csv(input_file)

    print(f"Current columns: {list(df.columns)}")

    # Define column mappings
    column_mappings = {
        'text_clean': 'comment_text',
        'text_clean_en_nllb': 'comment_text_en_nllb'
    }

    # Rename columns
    df_renamed = df.rename(columns=column_mappings)

    print(f"New columns: {list(df_renamed.columns)}")

    # Determine output file path
    if output_file is None:
        # Replace the file in place
        output_file = input_file

    # Save with proper CSV quoting
    df_renamed.to_csv(output_file, index=False, quoting=1, quotechar='"')
    print(f"✅ Fixed headers saved to: {output_file}")

    return True

def main():
    parser = argparse.ArgumentParser(
        description='Fix CSV column headers for YouTube translated files'
    )
    parser.add_argument(
        'input_file',
        help='Path to the translated YouTube CSV file'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: overwrite input file)',
        default=None
    )

    args = parser.parse_args()

    try:
        success = fix_headers(args.input_file, args.output)
        if success:
            print("🎉 Column headers fixed successfully!")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
