from googleapiclient.discovery import build
from pymongo import MongoClient
import pandas as pd

# -------------------- CONFIGURATION --------------------
API_KEY = "AIzaSyAwb2wvVA_1lSp1VT70R4Y2jSR3dsNLfM4"

video_urls = [
    "https://www.youtube.com/watch?v=XiCrniLQGYc",
    "https://www.youtube.com/watch?v=-eBUcBfkVCo",
    "https://www.youtube.com/watch?v=shG0ezBeeJc",
    "https://www.youtube.com/watch?v=FwAeYQHjxd8"
]

COMMENTS_PER_VIDEO = 70
OUTPUT_FILE = "youtube_comments.csv"
# -------------------------------------------------------

# Create YouTube API object
youtube = build("youtube", "v3", developerKey=API_KEY)

all_comments = []

# Get comments from all videos
for url in video_urls:

    video_id = url.split("v=")[1]

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=COMMENTS_PER_VIDEO,
        textFormat="plainText"
    )

    response = request.execute()

    print(f"Processing video: {video_id}")

    for item in response["items"]:

        comment = item["snippet"]["topLevelComment"]["snippet"]

        data = {
           'video_id': video_id,
           'author': comment['authorDisplayName'],
           'comment_id': item['snippet']['topLevelComment']['id'],
           'comment_text': comment['textDisplay'],
           'like_count': comment['likeCount'],
           'published_at': comment['publishedAt'],
           'comment_link': f"https://www.youtube.com/watch?v={video_id}&lc={item['snippet']['topLevelComment']['id']}"

        }

        all_comments.append(data)

# Save to CSV
df = pd.DataFrame(all_comments)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"{len(all_comments)} comments saved to {OUTPUT_FILE}")

# Store in MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client["mental_health_db"]
collection = db["comments"]

collection.insert_many(all_comments)

print(f"{len(all_comments)} comments stored in MongoDB successfully!")