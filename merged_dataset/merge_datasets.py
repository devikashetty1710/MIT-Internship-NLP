import os
import pandas as pd


def merge_social_media_datasets():
  # Define input file paths based on your folder structure
  bluesky_path = os.path.join("bluesky", "bluesky.csv")
  mastodon_path = os.path.join("mastodon", "mastodon_data.csv")
  reddit_path = os.path.join("reddit", "reddit_data.csv")

  # Define output directory and file path
  output_dir = "merged_dataset"
  output_file = os.path.join(output_dir, "unified_master_dataset.csv")

  # Target unified schema
  target_columns = [
      "post_id",
      "caption",
      "comment",
      "timestamp",
      "mental_health",
      "category",
      "severity",
      "platform",
  ]

  dfs = []

  # Load and process Bluesky Data
  if os.path.exists(bluesky_path):
    print(f"[*] Loading Bluesky data from '{bluesky_path}'...")
    df_bsky = pd.read_csv(bluesky_path)
    df_bsky["platform"] = "Bluesky"
    dfs.append(df_bsky)
  else:
    print(f"[!] Warning: {bluesky_path} not found.")

  # Load and process Mastodon Data
  if os.path.exists(mastodon_path):
    print(f"[*] Loading Mastodon data from '{mastodon_path}'...")
    df_masto = pd.read_csv(mastodon_path)
    df_masto["platform"] = "Mastodon"
    dfs.append(df_masto)
  else:
    print(f"[!] Warning: {mastodon_path} not found.")

  # Load and process Reddit Data
  if os.path.exists(reddit_path):
    print(f"[*] Loading Reddit data from '{reddit_path}'...")
    df_reddit = pd.read_csv(reddit_path)
    df_reddit["platform"] = "Reddit"
    dfs.append(df_reddit)
  else:
    print(f"[!] Warning: {reddit_path} not found.")

  if not dfs:
    print("[!] Error: No dataset files were loaded. Exiting.")
    return

  print("[*] Merging and standardizing datasets...")
  combined_df = pd.concat(dfs, ignore_index=True)

  # Ensure all standard columns exist and handle missing fields safely
  for col in target_columns:
    if col not in combined_df.columns:
      combined_df[col] = ""

  # Reorder columns to match the clean schema
  combined_df = combined_df[target_columns]

  # Preprocessing: Remove blank captions or duplicate post IDs if any exist
  combined_df = combined_df.dropna(subset=["caption"])
  combined_df = combined_df.drop_duplicates(subset=["post_id"])

  # Create output directory if it doesn't exist
  os.makedirs(output_dir, exist_ok=True)

  # Export master dataset to CSV
  combined_df.to_csv(output_file, index=False)

  print(
      f"\n[✔] SUCCESS! Created merged dataset: '{output_file}' with"
      f" {len(combined_df)} total rows.\n"
  )

  # Summary breakdown by platform
  print("Data breakdown by platform:")
  print(combined_df["platform"].value_counts())


if __name__ == "__main__":
  merge_social_media_datasets()