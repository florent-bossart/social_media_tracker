import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import string

# Load spaCy English model
# Make sure to download it first if you haven't: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def clean_text_spacy(text):
    """
    Cleans text using spaCy:
    - Lowercases
    - Removes punctuation
    - Removes stopwords
    - Lemmatizes
    - Removes non-alphabetic tokens
    """
    if pd.isna(text) or not isinstance(text, str):
        return []

    doc = nlp(text)
    cleaned_tokens = []
    for token in doc:
        if (
            not token.is_stop
            and not token.is_punct
            and token.is_alpha  # Keep only alphabetic tokens
            and token.lemma_ != "-PRON-"  # Remove pronouns like 'I', 'you' if desired (spaCy lemmatizes them to -PRON-)
        ):
            cleaned_tokens.append(token.lemma_.lower())
    return cleaned_tokens

def main():
    youtube_file_path = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/20250528_full_youtube_comments_cleaned_nllb_translated.csv"
    reddit_file_path = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/20250530_full_reddit_comments_cleaned.csv"
    output_file_path = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/wordcloud_source_text.txt"

    all_cleaned_words = []

    # Process YouTube data
    print(f"Processing YouTube data from {youtube_file_path}...")
    try:
        yt_df = pd.read_csv(youtube_file_path)
        if "comment_text" in yt_df.columns:
            for text in yt_df["comment_text"]:
                all_cleaned_words.extend(clean_text_spacy(text))
            print(f"Finished processing {len(yt_df)} YouTube comments.")
        else:
            print(f"Warning: 'comment_text' column not found in {youtube_file_path}")
    except FileNotFoundError:
        print(f"Error: YouTube file not found at {youtube_file_path}")
    except Exception as e:
        print(f"An error occurred while processing {youtube_file_path}: {e}")

    # Process Reddit data
    print(f"\nProcessing Reddit data from {reddit_file_path}...")
    try:
        reddit_df = pd.read_csv(reddit_file_path)
        processed_reddit_rows = 0
        if "post_text" in reddit_df.columns:
            for text in reddit_df["post_text"]:
                all_cleaned_words.extend(clean_text_spacy(text))
            processed_reddit_rows = len(reddit_df) # Count rows once
            print(f"Finished processing 'post_text' from {len(reddit_df)} Reddit entries.")
        else:
            print(f"Warning: 'post_text' column not found in {reddit_file_path}")

        if "comment_text" in reddit_df.columns:
            for text in reddit_df["comment_text"]:
                all_cleaned_words.extend(clean_text_spacy(text))
            if processed_reddit_rows == 0: # if post_text wasn't processed
                 processed_reddit_rows = len(reddit_df)
            print(f"Finished processing 'comment_text' from {len(reddit_df)} Reddit entries.")
        else:
            print(f"Warning: 'comment_text' column not found in {reddit_file_path}")

        if processed_reddit_rows > 0:
            print(f"Finished processing Reddit data.")
        else:
            print(f"No relevant text columns found or processed in {reddit_file_path}")


    except FileNotFoundError:
        print(f"Error: Reddit file not found at {reddit_file_path}")
    except Exception as e:
        print(f"An error occurred while processing {reddit_file_path}: {e}")

    # Save the combined cleaned text
    print(f"\nSaving cleaned words to {output_file_path}...")
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            for word in all_cleaned_words:
                f.write(word + "\n") # Write one word per line
        print(f"Successfully saved {len(all_cleaned_words)} cleaned words to {output_file_path}")
        print("You can now use this file as input for your word cloud generator.")
    except Exception as e:
        print(f"An error occurred while saving the output file: {e}")

if __name__ == "__main__":
    main()
