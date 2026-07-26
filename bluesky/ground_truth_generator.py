import pandas as pd
import re
import html
from pymongo import MongoClient

# MongoDB Connection
mongo = MongoClient("mongodb://localhost:27017/")

db = mongo["mental_health"]

collection = db["bluesky_posts"]

print("✅ Connected to MongoDB")

# Read all posts
posts = list(collection.find())

print(f"Total Posts Found: {len(posts)}")



def clean_text(text):
    # Convert HTML entities
    text = html.unescape(text)

    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)

    # Remove HTML tags
    text = re.sub(r"<.*?>", "", text)

    # Remove emojis
    text = re.sub(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "]+",
        "",
        text
    )

    # Remove special characters (keep letters, numbers and basic punctuation)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?']", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

cleaned_posts = []

for post in posts:
    text = post.get("text", "")
    cleaned = clean_text(text)

    if cleaned:
        cleaned_posts.append({
            "postid": post.get("postid", ""),
            "post": cleaned,
            "topic": post.get("topic", "")
        })

print(f"Cleaned Posts: {len(cleaned_posts)}")



# Weighted Keywords

keyword_weights = {
    "suicidal": 50,
    "abuse": 40,
    "trauma": 40,
    "toxic": 30,
    "depressed": 30,
    "anxiety": 20,
    "worthless": 3,
    "hopeless": 30,
    "lonely": 20,
    "sad": 10,
    "stressed": 10,
    "fail": 20,
    "broke": 20
}

def calculate_score(text):

    score = 0

    text = text.lower()

    for keyword, weight in keyword_weights.items():

        if keyword in text:
            score += weight

    return score

filtered_posts = []

for post in cleaned_posts:

    score = calculate_score(post["post"])

    if score > 0:

        filtered_posts.append({
            "postid": post["postid"],
            "post": post["post"],
            "topic": post["topic"],
            "score": score
        })

print(f"Filtered Posts: {len(filtered_posts)}")

def assign_severity(score):

    if score >= 40:
        return "High"

    elif score >= 20:
        return "Medium"

    else:
        return "Low"
    
severity_posts = []

for post in filtered_posts:

    severity = assign_severity(post["score"])

    severity_posts.append({
    "postid": post["postid"],
    "post": post["post"],
    "topic": post["topic"],
    "score": post["score"],
    "severity": severity
})

print(f"Severity Assigned: {len(severity_posts)}")



def get_category(topic):

    if topic == "Education":
        return "Education"

    elif topic == "Family_Abuse":
        return "Social Status"

    elif topic == "Social_Status":
        return "Social Status"

    elif topic == "Financial":
        return "Appearance"

    elif topic == "Self_Worth":
        return "Appearance"

    else:
        return "Appearance"



final_posts = []

post_id = 1

for post in severity_posts:

    final_posts.append({
        "post_id": post["postid"],
        "caption": post["post"],
        "timestamp": "",
        "mental_health": "Yes",
        "category": get_category(post["topic"]),
        "severity": post["severity"]
    })

print(f"Final Dataset Size: {len(final_posts)}")



df = pd.DataFrame(final_posts)

# Save in Sir's required format
df.to_csv("bluesky.csv", index=False)

print("✅ bluesky.csv exported successfully!")