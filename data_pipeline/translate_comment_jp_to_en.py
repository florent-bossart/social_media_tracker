import sys
import pandas as pd
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm

MODEL_NAME = "Helsinki-NLP/opus-mt-ja-en"
tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
model = MarianMTModel.from_pretrained(MODEL_NAME)

def translate(text):
    if not isinstance(text, str) or not text.strip():
        return text
    batch = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
    gen = model.generate(**batch)
    return tokenizer.decode(gen[0], skip_special_tokens=True)

def translate_column(df, source_col, target_col):
    translations = []
    for text in tqdm(df[source_col], desc=f"Translating {source_col}"):
        try:
            translations.append(translate(text))
        except Exception as e:
            print(f"Error translating: {e}")
            translations.append("")
    df[target_col] = translations
    return df

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python translate_comments_file.py <input_csv> <source_column> <output_csv>")
        print("Example: python translate_comments_file.py reddit_comments_cleaned.csv body_clean reddit_comments_translated.csv")
        sys.exit(1)

    infile = sys.argv[1]
    source_col = sys.argv[2]
    outfile = sys.argv[3]

    df = pd.read_csv(infile)
    df = translate_column(df, source_col, source_col + "_en")
    df.to_csv(outfile, index=False)
    print(f"Translated file written to {outfile}")
