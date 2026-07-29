import html
import os
import random
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
import feedparser
import pandas as pd


class RedditRSSScraper:

  def __init__(self):
    # Unique Custom User-Agent to avoid Reddit 429 rate-limiting
    self.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36 MIT_MH_NLP_Research/1.0"
        )
    }

  def clean_and_format_text(self, text):
    """Deep text cleaning pipeline to ensure readable, clean text for NLP."""
    if not text or pd.isna(text):
      return ""

    # 1. Unescape HTML entities (e.g., &amp; -> &, &lt; -> <)
    text = html.unescape(str(text))

    # 2. Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # 3. Remove URLs and Web Links
    text = re.sub(r"http[s]?://\S+|www\.\S+", "", text)

    # 4. Remove Emojis & Non-ASCII / Weird Special Characters
    # Keeps standard punctuation, numbers, letters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # 5. Remove unwanted Reddit layout clutter (e.g. "submitted by /u/...", "[link]", "[comments]")
    text = re.sub(
        r"submitted by\s+/u/\S+|\[link\]|\[comments\]",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # 6. Normalize punctuation and remove leftover orphan symbols
    text = re.sub(r"[\r\n\t]+", " ", text)  # Replace line breaks with space
    text = re.sub(
        r"[^\w\s.,!?\'\"]", " ", text
    )  # Keep standard prose characters
    text = re.sub(r"\s+", " ", text).strip()  # Collapse multiple spaces into one

    return text

  def map_category(self, subreddit, text):
    """Categorizes the post into one of the target schema domains."""
    text_lower = text.lower()
    sub_lower = subreddit.lower()

    if sub_lower in ["college", "jobs", "advice", "school"] or any(
        k in text_lower
        for k in ["fail", "exam", "grade", "school", "semester", "degree", "gpa"]
    ):
      return "Education"
    elif sub_lower in [
        "offmychest",
        "trauma",
        "relationships",
        "family",
    ] or any(
        k in text_lower
        for k in ["abuse", "parents", "family", "relationship", "toxic", "beaten"]
    ):
      return "Social Status"
    elif any(
        k in text_lower for k in ["body", "looks", "ugly", "weight", "height"]
    ):
      return "Appearance"
    else:
      return "Insecurity"

  def calculate_severity(self, text):
    """Estimates the distress severity level based on keyword density."""
    text_lower = text.lower()
    high_words = [
        "suicide",
        "kill myself",
        "end my life",
        "dying",
        "cannot go on",
        "abuse",
        "trauma",
    ]
    medium_words = [
        "depressed",
        "anxiety",
        "failing",
        "lonely",
        "struggling",
        "hopeless",
        "stress",
    ]

    if any(word in text_lower for word in high_words):
      return "High"
    elif any(word in text_lower for word in medium_words):
      return "Medium"
    return "Low"

  def fetch_feed_data(self, rss_url, retries=2):
    """Fetches RSS feeds with automatic 429 rate-limit backoff."""
    posts = []
    for attempt in range(retries + 1):
      try:
        req = urllib.request.Request(rss_url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=12) as response:
          xml_data = response.read()
          feed = feedparser.parse(xml_data)

          for entry in feed.entries:
            raw_content = entry.get("summary", "") or entry.get("title", "")
            if not raw_content:
              continue

            raw_id = (
                entry.get("id", "").split("/")[-1]
                if "/" in entry.get("id", "")
                else entry.get("id")
            )
            link = entry.get("link", "")

            # Extract subreddit name
            sub_match = re.search(r"/r/([^/\n?#]+)", link, re.IGNORECASE)
            sub_name = sub_match.group(1).lower() if sub_match else "unknown"

            # Perform text cleaning
            clean_title = self.clean_and_format_text(entry.get("title", ""))
            clean_body = self.clean_and_format_text(raw_content)

            # Combine title and content neatly
            if clean_title and clean_title not in clean_body:
              caption = f"{clean_title}. {clean_body}"
            else:
              caption = clean_body

            # Skip entries that resulted in empty text after cleaning
            if not caption or len(caption) < 15:
              continue

            pub_date = entry.get("published", "")
            timestamp_str = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S+00:00")
                if not pub_date
                else pub_date
            )

            post_doc = {
                "post_id": f"REDDIT_{raw_id}",
                "caption": caption,
                "comment": "",  # Blank column to align with Bluesky/Mastodon schema
                "timestamp": timestamp_str,
                "mental_health": "Yes",
                "category": self.map_category(sub_name, caption),
                "severity": self.calculate_severity(caption),
            }
            posts.append(post_doc)
        break  # Successfully fetched, exit retry loop

      except urllib.error.HTTPError as e:
        if e.code == 429:
          wait_time = (attempt + 1) * 5
          print(
              f"  [!] HTTP 429 Rate Limit hit. Pausing for {wait_time} seconds..."
          )
          time.sleep(wait_time)
        else:
          print(f"  [!] Failed to pull {rss_url}: {e}")
          break
      except Exception as e:
        print(f"  [!] Failed to process {rss_url}: {e}")
        break

    return posts


def load_ground_truth_fallback():
  """Loads local ground truth CSV if available to guarantee 500+ items."""
  scraper = RedditRSSScraper()
  fallback_files = ["reddit_ground_truth_dataset.csv", "cleaned_reddit_posts.csv"]
  fallback_posts = []

  for file_name in fallback_files:
    if os.path.exists(file_name):
      try:
        gt_df = pd.read_csv(file_name)
        for idx, row in gt_df.iterrows():
          post_text = row.get("post", row.get("raw_text", ""))
          clean_text = scraper.clean_and_format_text(post_text)

          if not clean_text or len(clean_text) < 15:
            continue

          pid = row.get("postid", f"REDDIT_GT_{idx}")
          sev = row.get("severity_label", "Medium")
          if sev == "Moderate":
            sev = "Medium"

          cat = "Insecurity"
          if row.get("target_education") == 1:
            cat = "Education"
          elif row.get("target_abusive") == 1:
            cat = "Social Status"

          fallback_posts.append({
              "post_id": str(pid),
              "caption": clean_text,
              "comment": "",
              "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S+00:00"),
              "mental_health": "Yes",
              "category": cat,
              "severity": sev,
          })
      except Exception as e:
        print(f"  [!] Note: Could not parse fallback dataset {file_name}: {e}")

  return fallback_posts


def main():
  scraper = RedditRSSScraper()

  target_subreddits = [
      "mentalhealth",
      "anxiety",
      "depression",
      "selfhelp",
      "psychology",
      "offmychest",
      "advice",
      "jobs",
      "college",
      "suicidewatch",
      "lonely",
      "stress",
      "emotionalintelligence",
      "trauma",
      "socialanxiety",
      "relationships",
      "family",
      "needafriend",
      "mentalillness",
  ]

  feed_types = [
      "hot/.rss",
      "new/.rss",
      "top/.rss?t=month",
      "top/.rss?t=year",
      "top/.rss?t=all",
  ]

  print(
      "[*] Scraping and cleaning Reddit RSS feeds (Target: 500+ clean"
      " posts)..."
  )
  all_extracted_posts = []
  seen_ids = set()

  # 1. Scrape live RSS
  for sub in target_subreddits:
    if len(all_extracted_posts) >= 550:
      print("\n[✔] Target goal of 500+ clean posts reached!")
      break

    print(
        f"---> Ingesting r/{sub} (Current Clean Count:"
        f" {len(all_extracted_posts)})..."
    )

    for feed in feed_types:
      if len(all_extracted_posts) >= 550:
        break

      rss_url = f"https://www.reddit.com/r/{sub}/{feed}"
      posts = scraper.fetch_feed_data(rss_url)

      new_added = 0
      for p in posts:
        if p["post_id"] not in seen_ids:
          seen_ids.add(p["post_id"])
          all_extracted_posts.append(p)
          new_added += 1

      if new_added > 0:
        print(f"  [+] Ingested {new_added} clean posts from /{feed}")

      time.sleep(random.uniform(2.5, 3.5))

  # 2. Fallback: If live scraper got < 500 posts due to rate limits, load local ground truth
  if len(all_extracted_posts) < 500:
    print(
        f"\n[*] Live feed total is {len(all_extracted_posts)}. Ingesting"
        " fallback dataset to reach 500+..."
    )
    fallback_data = load_ground_truth_fallback()
    for fp in fallback_data:
      if fp["post_id"] not in seen_ids:
        seen_ids.add(fp["post_id"])
        all_extracted_posts.append(fp)

  # 3. Save to target location
  df = pd.DataFrame(all_extracted_posts)

  target_columns = [
      "post_id",
      "caption",
      "comment",
      "timestamp",
      "mental_health",
      "category",
      "severity",
  ]

  if not df.empty:
    df = df[target_columns]

    output_dir = "reddit"
    os.makedirs(output_dir, exist_ok=True)
    output_filepath = os.path.join(output_dir, "reddit_data.csv")

    df.to_csv(output_filepath, index=False)
    print(
        f"\n[✔] SUCCESS! Saved {len(df)} clean posts to '{output_filepath}'."
    )
    print("\nSample Cleaned Prose:")
    print(df[["post_id", "caption", "category", "severity"]].head(3))
  else:
    print("\n[!] No posts were retrieved.")


if __name__ == "__main__":
  main()