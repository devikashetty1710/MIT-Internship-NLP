from mastodon import Mastodon
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
INSTANCE = "https://mastodon.social"
ACCESS_TOKEN = "Z51Z4QS4AAoRB2wQWNL0QXYd8OtTGhfB_z7MgczutNA"

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE
)

# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean(text):
    return BeautifulSoup(text or "", "html.parser").get_text()

# -----------------------------
# GET POSTS (FIXED - USE HASHTAG)
# -----------------------------
def get_posts(limit=30):
    try:
        posts = []
        results = mastodon.timeline_hashtag("mentalhealth", limit=40)

        posts.extend(results)

        return posts[:limit]

    except Exception as e:
        print("Error fetching posts:", e)
        return []

# -----------------------------
# GET COMMENTS (SAFE VERSION)
# -----------------------------
def get_comments(post_id):
    try:
        context = mastodon.status_context(post_id)
        return [
            clean(c.get("content", ""))
            for c in context.get("descendants", [])
        ]
    except:
        return []

# -----------------------------
# SCRAPE
# -----------------------------
def scrape():
    data = []

    posts = get_posts(30)
    print("Total posts found:", len(posts))
    if not posts:
        print("No posts found. Try another hashtag.")
        return []

    for p in posts:
        post_id = p.get("id")
        username = p.get("account", {}).get("username", "")
        caption = clean(p.get("content", ""))

        print("Scraping:", username)

        comments = get_comments(post_id)

        data.append({
            "post_id": post_id,
            "username": username,
            "caption": caption,
            "comments": comments,
            "timestamp":datetime.now().isoformat()
        })

    return data

# -----------------------------
# SAVE CSV
# -----------------------------
def save(data):
    rows = []

    for item in data:
        if not item["comments"]:
            rows.append([
                item["post_id"],
                item["username"],
                item["caption"],
                "",
                item["timestamp"]
            ])
        else:
            for c in item["comments"]:
                rows.append([
                    item["post_id"],
                    item["username"],
                    item["caption"],
                    c,
                    item["timestamp"]
                ])

    df = pd.DataFrame(rows, columns=["post_id", "username", "caption", "comment","timestamp"])
    df.to_csv("mastodon_data.csv", index=False)

    print("Saved successfully → mastodon_data.csv")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    dataset = scrape()

    if dataset:
        save(dataset)
    else:
        print("No data collected")