import pandas as pd
from textblob import TextBlob

df = pd.read_csv("depressed_dataset.csv")

for text in df["text"]:
    polarity = TextBlob(str(text)).sentiment.polarity

    if polarity < 0:
        sentiment = "Negative"
    elif polarity > 0:
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    print("\nText:")
    print(text[:150])
    print("Sentiment:", sentiment)
    print("Polarity:", polarity)