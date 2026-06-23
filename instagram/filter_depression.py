import pandas as pd

df = pd.read_csv("dataset.csv")

keywords = [
    "depressed",
    "depression",
    "sad",
    "lonely",
    "alone",
    "hopeless",
    "worthless",
    "anxiety",
    "frustrating",
    "frustrated",
    "cry",
    "grief",
    "stuck",
    "empty",
    "tired"
]

filtered = []

for text in df["text"]:
    text_lower = str(text).lower()

    for word in keywords:
        if word in text_lower:
            filtered.append(text)
            break

result = pd.DataFrame(filtered, columns=["text"])

result.to_csv("depressed_dataset.csv", index=False)

print("Depressed rows found:", len(result))
print("Saved to depressed_dataset.csv")