import pandas as pd

data = [
    ["I feel lonely every day", "caption"],
    ["Nobody understands me", "comment"]
]

df = pd.DataFrame(data, columns=["text", "type"])

df.to_csv("dataset.csv", index=False)

print("dataset.csv created successfully")