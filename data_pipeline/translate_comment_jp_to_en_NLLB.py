import os
import glob
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm
import re
import torch
torch.set_num_threads(2)  # or 1

def maybe_is_japanese(text):
    return bool(re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9faf]', str(text)))

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
    df = pd.read_csv(input_path)
    jp_mask = df[column_to_translate].apply(lambda x: bool(str(x).strip()) and maybe_is_japanese(x))
    indices = df.index[jp_mask].tolist()
    texts_to_translate = df.loc[indices, column_to_translate].astype(str).tolist()

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
        df[output_column] = ""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Create output filename (_nllb_translated.csv)
    filename = os.path.basename(input_path).replace(".csv", "_nllb_translated.csv")
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False)
    print(f"NLLB translated file saved to: {output_path}")

if __name__ == "__main__":
    input_folder = "data/intermediate"
    output_folder = os.path.join(input_folder, "translated")
    reddit_files = glob.glob(os.path.join(input_folder, "*full_reddit_comments_cleaned.csv"))
    youtube_files = glob.glob(os.path.join(input_folder, "*full_youtube_comments_cleaned.csv"))

    tokenizer, model = load_translation_model()
    # No need to translate reddit comments, all are in English.
    # for file in reddit_files:
    #    print(f"Processing {file} ...")
    #    process_file(file, "body_clean", "body_clean_en_nllb", output_folder, tokenizer, model)
    for file in youtube_files:
        print(f"Processing {file} ...")
        process_file(file, "comment_text", "comment_text_en_nllb", output_folder, tokenizer, model)
