import re
import pandas as pd
from pymongo import MongoClient
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class RedditPreprocessor:
    def __init__(self, mongodb_uri="mongodb://localhost:27017/"):
        """
        Connects specifically to the Reddit data repository.
        """
        self.client = MongoClient(mongodb_uri)
        self.db = self.client["mental_health_research"]
        self.raw_collection = self.db["reddit_posts"]
        
        # Dedicated destination collection for processed data
        self.clean_collection = self.db["cleaned_reddit_posts"]
        
        # Initialize NLTK utilities once to keep runtime fast
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def fetch_reddit_data(self):
        """
        Pulls only Reddit documents from your raw database layer.
        """
        cursor = self.raw_collection.find({"platform": "Reddit"}, {"post_id": 1, "raw_text": 1, "_id": 0})
        return list(cursor)

    def clean_reddit_text(self, text):
        """
        Step-by-step text transformation filters explicitly built for Reddit noise.
        """
        if not text:
            return ""

        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'', '', text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\br\/[^\s]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def save_to_mongodb(self, processed_docs):
        """
        Upserts the cleaned tokens and text directly into MongoDB.
        """
        if not processed_docs:
            return
            
        print(f"[+] Upserting {len(processed_docs)} preprocessed records into 'cleaned_reddit_posts'...")
        for doc in processed_docs:
            self.clean_collection.update_one(
                {"post_id": doc["post_id"]},
                {"$set": doc},
                upsert=True
            )
        print("[✔] Database write transaction successful!")

    def run_pipeline(self, output_csv_path=None):
        print("[*] Starting Dedicated Reddit NLP Preprocessing Pipeline...")
        raw_docs = self.fetch_reddit_data()
        
        if not raw_docs:
            print("[-] No Reddit records found in MongoDB. Make sure your scraper ran successfully!")
            return

        print(f"[+] Found {len(raw_docs)} Reddit documents to process.")
        print("-" * 80)
        
        cleaned_dataset = []
        for i, doc in enumerate(raw_docs):
            raw_text = doc["raw_text"]
            cleaned_txt = self.clean_reddit_text(raw_text)
            
            # 1. Advanced Tokenization
            raw_tokens = word_tokenize(cleaned_txt)
            
            # 2. Filter out Stopwords and punctuation, then Lemmatize the remainder
            processed_tokens = [
                self.lemmatizer.lemmatize(token)
                for token in raw_tokens 
                if token not in self.stop_words and token.isalnum()
            ]
            
            cleaned_dataset.append({
                "post_id": doc["post_id"],
                "platform": "Reddit",
                "cleaned_text": cleaned_txt,
                "tokens": processed_tokens,
                "word_count": len(processed_tokens)
            })

            # Live trace blocks showing full contextual paragraph verification
            if i < 2:
                print(f"\n[DOCUMENT {i+1} ORIGINAL   ]: {raw_text[:120]}...")
                print(f"[DOCUMENT {i+1} CLEANED TXT]: {cleaned_txt}")
                print(f"[DOCUMENT {i+1} FINAL LEMMAS]: {processed_tokens[:15]}")
                print("-" * 80)

        # Execute database save
        self.save_to_mongodb(cleaned_dataset)

        # Build final DataFrame
        df = pd.DataFrame(cleaned_dataset)

        # --- EXPORT TO LOCAL WORKSPACE CSV ---
        if output_csv_path:
            df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
            print(f"[✔] Successfully exported ALL {len(df)} records into: {output_csv_path}")

        # Configure layout to present metrics cleanly without splitting lines
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)

        # Summary statistics display block showing metric attributes only
        print("\n--- Reddit NLP Summary Table Preview ---")
        print(df[['post_id', 'word_count']].head(5))
        print(f"\n[✔] Done! Text preprocessing pipeline run complete.")

if __name__ == "__main__":
    pipeline = RedditPreprocessor()
    
    # Automatically drop the complete 49 row file inside your reddit folder
    pipeline.run_pipeline(output_csv_path="reddit/cleaned_reddit_posts.csv")