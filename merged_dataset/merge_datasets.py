import pandas as pd
import os

# ============================================================
# CONFIGURATION
# ============================================================
# Since this script is now INSIDE the merged_dataset folder, 
# we use "../" to go up one level to the root directory.
REDDIT_FILE = "../reddit/reddit_data.csv"          
BLUESKY_FILE = "../bluesky/bluesky.csv"       
MASTODON_FILE = "../mastodon/mastodon_ground_truth.csv" 

# Output file is now just in the current folder
OUTPUT_FILE = "unified_master_dataset.csv" 

def load_data(filepath, platform_name):
    if not os.path.exists(filepath):
        print(f"CRITICAL ERROR: Could not find {filepath}!")
        print(f"   Please check the folder and update the filename in the script.")
        return pd.DataFrame()
    
    df = pd.read_csv(filepath)
    print(f"Loaded {platform_name}: {len(df)} rows from {filepath}")
    
    # Standardize text column
    text_col = None
    for col in ['caption', 'text', 'body', 'title', 'content']:
        if col in df.columns:
            text_col = col
            break
            
    if text_col:
        if 'title' in df.columns and 'body' in df.columns:
            df['caption'] = df['title'].fillna('') + " " + df['body'].fillna('')
        else:
            df['caption'] = df[text_col]
    else:
        df['caption'] = df.iloc[:, 0]

    # Standardize ID and make unique
    id_col = None
    for col in ['post_id', 'id', 'uri', 'index']:
        if col in df.columns:
            id_col = col
            break
            
    if id_col:
        df['post_id'] = df[id_col].astype(str)
    else:
        df['post_id'] = range(len(df))
        
    df['post_id'] = f"{platform_name.lower()}_" + df['post_id']
    df['platform'] = platform_name
    
    if 'severity' not in df.columns:
        df['severity'] = 'Low'
    if 'category' not in df.columns:
        df['category'] = 'Unknown'
        
    return df[['post_id', 'caption', 'platform', 'severity', 'category']]

print("="*60)
print("  MERGING ALL PLATFORMS ")
print("="*60)

df_reddit = load_data(REDDIT_FILE, "Reddit")
df_bluesky = load_data(BLUESKY_FILE, "Bluesky")
df_mastodon = load_data(MASTODON_FILE, "Mastodon")

merged_df = pd.concat([df_reddit, df_bluesky, df_mastodon], ignore_index=True)
merged_df = merged_df[merged_df['caption'].notna() & (merged_df['caption'].str.strip() != '')]

print(f"\n FINAL MERGED RECORDS: {len(merged_df)}")
print("\nPlatform Distribution:")
print(merged_df['platform'].value_counts())

os.makedirs("merged_dataset", exist_ok=True)
merged_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print(f"\n Successfully saved to: {OUTPUT_FILE}")