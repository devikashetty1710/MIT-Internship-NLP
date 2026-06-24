## Project Context

This project builds an automated **data and text processing pipeline** to study public mental health conversations across social media platforms like Reddit, YouTube, and Mastodon. 

### Key Goals of the Project:
* **Distress Monitoring (Not Medical Diagnosis):** The system is built strictly as a risk-indicator tool. It is designed to look at public text data to pick up on patterns of situational distress rather than trying to diagnose any single individual clinically.
* **Protecting Privacy:** To ensure anonymity, all personal tags and direct usernames are immediately scrubbed out and destroyed using a secure mathematical code (one-way hashing) before any text data is saved to our local database tier.
* **Understanding Root Causes:** The data pipeline helps our research team automatically categorize posts by looking for specific contextual stress triggers—such as relationship distress, loneliness (social isolation), academic pressure, or financial struggles.

### How the Data Flows through the Project Layers:

1. **The Collection Stage (Layers 01 & 02):** Specialized, object-oriented scrapers target public feeds and streams. They automatically standardize the unstructured data into a uniform structure (`post_id`, `platform`, `raw_text`) and store it securely in a local **MongoDB database**.
2. **The NLP Normalization Engine (Layer 03):** Web text is incredibly messy. This stage uses advanced Natural Language Processing (NLP) rules to scrub away HTML junk tags, strip out generic filler words (like "the", "and", "is"), and reduce complex words back down to their base dictionary roots (lemmatization). 
3. **The Categorization Set (Layer 04):** The pristine, filtered keywords are automatically exported into structured spreadsheets (`.csv`). This gives our team a complete, non-truncated framework to manually verify behavioral domains and train machine learning models to detect severity levels accurately.