import os
import glob
import pandas as pd
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm
import re
import torch
torch.set_num_threads(2)  # or 1

def maybe_is_japanese(text):
    return bool(re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9faf]', str(text)))

def load_translation_model():
    model_name = "Helsinki-NLP/opus-mt-ja-en"
    print("Loading model...")
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    print("Model loaded.")
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def translate(texts, tokenizer, model, batch_size=4):
    translated = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Translating"):
        batch = texts[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
        outputs = model.generate(**inputs)
        translated += [tokenizer.decode(t, skip_special_tokens=True) for t in outputs]
    return translated

def process_file(input_path, column_to_translate, output_column, output_dir, tokenizer, model):
    df = pd.read_csv(input_path)
    jp_mask = df[column_to_translate].apply(lambda x: bool(str(x).strip()) and maybe_is_japanese(x))
    indices = df.index[jp_mask].tolist()
    texts_to_translate = df.loc[indices, column_to_translate].astype(str).tolist()

    # Only translate non-empty Japanese text
    if texts_to_translate:
        translations = translate(texts_to_translate, tokenizer, model)
        # Initialize new column as original (or empty)
        df[output_column] = ""
        # Fill in only translated rows
        print(f"Translating {len(texts_to_translate)} texts...")
        for idx, trans in zip(indices, translations):
            df.at[idx, output_column] = trans
    else:
        df[output_column] = ""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Create output filename
    filename = os.path.basename(input_path).replace(".csv", "_translated.csv")
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False)
    print(f"Translated file saved to: {output_path}")

if __name__ == "__main__":
    input_folder = "data/intermediate"
    output_folder = os.path.join(input_folder, "translated")
    reddit_files = glob.glob(os.path.join(input_folder, "*_reddit_comments_cleaned.csv"))
    youtube_files = glob.glob(os.path.join(input_folder, "*_youtube_comments_cleaned.csv"))

    tokenizer, model = load_translation_model()

    for file in reddit_files:
        print(f"Processing {file} ...")
        process_file(file, "body_clean", "body_clean_en", output_folder, tokenizer, model)
    for file in youtube_files:
        print(f"Processing {file} ...")
        process_file(file, "text_clean", "text_clean_en", output_folder, tokenizer, model)
