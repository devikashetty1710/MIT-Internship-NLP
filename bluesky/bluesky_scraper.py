from atproto import Client
from pymongo import MongoClient
import pandas as pd
import re
import html


# Bluesky Login

client = Client()

HANDLE = "d-ishashetty.bsky.social"
APP_PASSWORD = "27ih-wych-ugnw-f5df"

client.login(HANDLE, APP_PASSWORD)

print("✅ Successfully logged in to Bluesky!")


# MongoDB Connection

mongo_client = MongoClient("mongodb://localhost:27017/")

db = mongo_client["mental_health"]

collection = db["bluesky_posts"]

print("✅ MongoDB Connected Successfully!")


# search topics

topics = {
    "Education": [
        "I failed my semester",
        "I failed my exams",
        "exam anxiety",
        "academic burnout",
        "college depression",
        "I want to drop out",
        "I can't study anymore",
        "I feel like a failure because of college",
        "school stress",
        "education ruined my mental health"
    ],

    "Family_Abuse": [
        "my parents abuse me",
        "toxic family",
        "emotional abuse",
        "domestic violence",
        "family trauma",
        "my parents hate me",
        "abusive relationship",
        "toxic marriage",
        "childhood trauma",
        "family pressure"
        "My family doesn't support me",
        "My home is toxic",
        "I don't feel safe at home",
        "My parents constantly fight",
        "I'm scared of my parents",
        "My family controls me",
        "I grew up in an abusive home",
        "My childhood was traumatic",
        "My parents never listen",
        "I feel trapped at home"
            ],

    "Financial": [
        "I lost my job",
        "I am unemployed",
        "financial stress",
        "I cannot pay my bills",
        "money anxiety",
        "I am drowning in debt",
        "salary is not enough",
        "I can't afford food",
        "financial depression",
        "job loss anxiety"
        "I'm struggling financially",
        "I can't pay rent",
        "I'm worried about money",
        "I lost all my savings",
        "I have no income",
        "I'm living paycheck to paycheck",
        "I'm financially exhausted",
        "I can't afford healthcare",
        "I'm worried about my future",
        "I'm broke and stressed"

    ],

    "Self_Worth": [
        "I feel worthless",
        "I hate myself",
        "I feel hopeless",
        "I am a failure",
        "I have no future",
        "I feel empty",
        "I don't deserve to live",
        "I have no purpose",
        "low self esteem",
        "I am useless"
        "I hate my life",
       "I feel broken",
       "I don't matter",
       "I feel invisible",
        "I'm mentally exhausted",
        "I feel like giving up",
        "I have no motivation",
        "I feel unwanted",
        "I'm tired of everything",
        "I don't know what to do anymore"
    ],

    "Social_Status": [
        "I have no friends",
        "I feel lonely",
        "everyone ignores me",
        "social anxiety",
        "I feel left out",
        "I feel isolated",
        "nobody understands me",
        "I have nobody to talk to",
        "I feel invisible",
        "social rejection"
    ]
}
post_id = 1

all_posts = []

for topic, queries in topics.items():

    topic_posts = []

    for query in queries:
        try:
            result = client.app.bsky.feed.search_posts(
                params={
                    "q": query,
                    "limit": 100
                }
            )

            for post in result.posts:

                if len(topic_posts) >= 100:
                    break

                text = post.record.text.strip()
                if len(text.split()) < 8:
                 continue

                if not text:
                    continue

                # Skip duplicate posts
                if any(p["text"] == text for p in topic_posts):
                    continue

                topic_posts.append({
                "postid": f"BSKY_{post_id:03}",
                "topic": topic,
                "query": query,
                "text": text
                })

                post_id += 1
            if len(topic_posts) >= 100:
                break

        except Exception as e:
            print(f"Error while searching '{query}': {e}")

    print(f"{topic}: {len(topic_posts)} posts collected")

    all_posts.extend(topic_posts)

print(f"\nTotal Posts Collected: {len(all_posts)}")


# Save all posts
# Remove duplicates across all topics
unique_posts = []
seen = set()

for post in all_posts:
    text = post["text"].strip().lower()

    if text not in seen:
        seen.add(text)
        unique_posts.append(post)

print(f"\nUnique Posts Collected: {len(unique_posts)}")

collection.delete_many({})
collection.insert_many(unique_posts)

print("✅ Unique posts saved successfully to MongoDB!")