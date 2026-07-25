from mastodon import Mastodon
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import re
from langdetect import detect
import os
from dotenv import load_dotenv


load_dotenv()

# CONFIG

INSTANCE =os.getenv("INSTANCE")
ACCESS_TOKEN =os.getenv("ACCESS_TOKEN")

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE
)


# CLEAN TEXT

def clean(text):
    text = BeautifulSoup(text or "", "html.parser").get_text()

    # Remove @mentions
    text = re.sub(r'@\w+', '', text)

    # Remove hashtags
    text = re.sub(r'#\w+', '', text)

    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    return text.strip()

# LANGUAGE FILTER  ← Create it here
def is_english_or_hindi(text):
    try:
        lang = detect(text)
        return lang in ["en", "hi"]
    except:
        return False


# Remove posts that are just links or news

def is_useful_post(text):
    text = text.lower()

    # Ignore posts that are mostly links
    if "http://" in text or "https://" in text:
     return False

    # Ignore news/blog posts
    unwanted = [
        "theguardian",
        "bbc",
        "npr",
        "wordpress",
        "news",
        "read more",
        "original title",
        "source:"
    ]

    for word in unwanted:
        if word in text:
            return False

    return True

search_hashtags = [
    "depression",
    "anxiety",

    "examstress",
    "studentlife",
    "college",

    "jobloss",
    "unemployment",
    "career",

    "bodyimage",
    "selfesteem",
    "lookism",
    "bullying"
]

def is_mental_health_related(text):

    text = text.lower()

    mental_words = [
    "depression",
    "depressed",
    "anxiety",
    "stress",
    "mental",
    "panic",
    "panic attack",
    "burnout",
    "trauma",
    "lonely",
    "loneliness",
    "therapy",
    "therapist",
    "sad",
    "hopeless",
    "grief",
    "crying",
    "fear",
    "suicide",
    "suicidal",
    "self harm",
    "mental illness",
    "ptsd",
    "ocd",
    "bipolar",
    "schizophrenia"
    ]

    return any(word in text for word in mental_words)
# Categorization

def categorize_reason(text):

    text = text.lower()

    # ---------------- Education ----------------

    education = [
        "exam",
        "exams",
        "student",
        "college",
        "school",
        "study",
        "studies",
        "teacher",
        "assignment",
        "homework",
        "semester",
        "grades",
        "grade",
        "academic",
        "class",
        "campus",
        "education",
        "university",
        "failed",
        "fail"
    ]

    # ---------------- Social Status ----------------
    social = [
    "job",
    "work",
    "career",
    "office",
    "boss",
    "salary",
    "income",
    "money",
    "financial",
    "rent",
    "bill",
    "bills",
    "loan",
    "poverty",
    "homeless",
    "employment",
    "unemployed",
    "layoff",
    "promotion"
]

    # ---------------- Appearance ----------------

    appearance = [
    "ugly",
    "looks",
    "appearance",
    "body",
    "body image",
    "bodyimage",
    "fat",
    "skinny",
    "weight",
    "face",
    "beauty",
    "beautiful",
    "lookism",
    "self esteem",
    "self-esteem",
    "bullied",
    "bullying",
    "fatshaming",
    "bodyshaming"
]

    if any(word in text for word in education):
        return "Education"

    if any(word in text for word in social):
        return "Social Status"

    if any(word in text for word in appearance):
        return "Appearance"

    return "Other"

#Severity level
def severity_level(text):

    text = text.lower()

    # High severity
    high = [
        "suicide",
        "suicidal",
        "kill myself",
        "end my life",
        "die",
        "don't want to live",
        "stop breathing",
        "self harm",
        "cut myself",
        "worthless",
        "take me with you",
        "can't go on"
    ]

    # Medium severity
    medium = [
        "depressed",
        "depression",
        "panic attack",
        "panic",
        "anxiety",
        "burnout",
        "trauma",
        "hopeless",
        "crying",
        "grief",
        "lonely",
        "fear",
        "overwhelmed"
    ]

    # Low severity
    low = [
        "stress",
        "worried",
        "nervous",
        "tired",
        "sad",
        "upset",
        "exam stress",
        "work stress",
        "feeling low",
        "frustrated"
    ]

    if any(word in text for word in high):
        return "High"

    elif any(word in text for word in medium):
        return "Medium"

    elif any(word in text for word in low):
        return "Low"

    else:
        return "Low"

# GET POSTS (FIXED - USE HASHTAG)

def get_posts(limit=750):
    try:

        posts = []

        for tag in search_hashtags:

            print(f"Fetching #{tag}")

            results = mastodon.timeline_hashtag(tag, limit=100)

            print(f"Found {len(results)} posts")

            posts.extend(results)

        # Remove duplicates
        unique_posts = {}

        for post in posts:
            unique_posts[post["id"]] = post

        return list(unique_posts.values())[:limit]

    except Exception as e:
        print("Error:", e)
        return []
    
# GET COMMENTS (SAFE VERSION)

def get_comments(post_id):
    try:
        context = mastodon.status_context(post_id)

        comments = []

        for c in context.get("descendants", []):
            text = clean(c.get("content", ""))

            if (
                 is_english_or_hindi(text)
                 and is_useful_post(text)
                 and text.strip() != ""
             ):
             comments.append(text)

        return comments

    except:
        return []


# SCRAPE

def scrape():
    data = []

    posts = get_posts(750)

    print("Total posts found:", len(posts))

    if not posts:
        print("No posts found.")
        return []

    for p in posts:

        post_id = p.get("id")
        caption = clean(p.get("content", ""))

        if caption.strip() == "":
            continue

        if not is_useful_post(caption):
            continue

        if not is_english_or_hindi(caption):
            continue

        print("Scraping Post ID:", post_id)

        comments = get_comments(post_id)
        combined_text=caption+ " "+" ".join(comments)
        # Check only the post
        if not is_mental_health_related(caption):
            continue

        mental_health = "Yes"

        # Categorize only the post
        category = categorize_reason(combined_text)
        if category=="Other":
            continue
        severity = severity_level(combined_text)
        print(category, severity)


        data.append({
            "post_id": post_id,
            "caption": caption,
            "comments": comments,
            "timestamp": p.get("created_at"),
            "mental_health": mental_health,
            "category": category,
            "severity": severity
        })

    return data
# SAVE CSV

def save(data):
    rows = []

    for item in data:
        if not item["comments"]:
            rows.append([
                item["post_id"],
                item["caption"],
                "",
                item["timestamp"],
                item["mental_health"],
                item["category"],
                item["severity"]
            ])
        else:
            for c in item["comments"]:
                rows.append([
                    item["post_id"],
                    item["caption"],
                    c,
                    item["timestamp"],
                    item["mental_health"],
                    item["category"],
                    item["severity"]
                ])

    df = pd.DataFrame(rows, columns=["post_id","caption", "comment","timestamp","mental_health","category","severity"])
    df.to_csv("mastodon_data.csv", index=False)

    print("Saved successfully → mastodon_data.csv")


# RUN

if __name__ == "__main__":
    dataset = scrape()

    if dataset:
        save(dataset)
    else:
        print("No data collected")