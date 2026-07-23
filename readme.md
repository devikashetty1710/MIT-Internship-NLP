# Mental Health Risk Indicator Detection Pipeline

This project builds an end-to-end data engineering and NLP pipeline that collects public social media text, protects user privacy, cleans formatting noise, and generates structured ground-truth datasets for identifying situational risk indicators.

---

# Problem Statement

People often share personal struggles, emotional distress, and life challenges on public online discussion platforms. While this information can support NLP research, it presents several challenges:

1. Public posts are highly unstructured and contain HTML, emojis, hyperlinks, markdown artifacts, and other noisy text.
2. Plain-text usernames introduce unnecessary privacy risks when storing collected data.
3. Data collected from multiple communities exists in fragmented formats and requires consolidation before analysis.
4. Machine learning models require clean, standardized, and consistently labeled datasets to effectively learn patterns associated with situational risk indicators.

---

# Solution Overview

To address these challenges, we developed a multi-stage data engineering pipeline that transforms raw public text into a structured dataset suitable for downstream NLP tasks.

The pipeline performs the following operations:

- **Multi-Source Data Collection:** Collects publicly available posts from multiple online discussion communities.
- **Privacy Preservation:** Anonymizes all usernames using irreversible SHA-256 hashing before storage.
- **Centralized Storage:** Stores raw documents inside a local MongoDB database.
- **Text Preprocessing:** Removes HTML tags, URLs, markdown artifacts, emojis, special characters, and formatting noise.
- **Automatic Label Generation:** Assigns distress severity levels and maps each post into predefined target categories.
- **Ground-Truth Dataset Creation:** Produces a structured CSV dataset ready for annotation, analysis, and baseline NLP model development.

```text
[ Data Collection ]
          │
          ▼
[ MongoDB Database ]
          │
          ▼
[ Scrubbing & Anonymization ]
          │
          ▼
[ Ground-Truth Dataset Generation ]
          │
          ▼
[ Master Ground-Truth CSV ]
```

---

# Work Completed Before Mentor Review

Before presenting the project to our mentor, the following baseline pipeline had already been implemented:

- Configured a Python virtual environment (`venv`) for dependency management.
- Installed and configured MongoDB Community Server for document storage.
- Developed an initial Reddit RSS-based scraper for collecting public posts.
- Created a preliminary ground-truth dataset containing approximately **115–125** cleaned samples.
- Implemented basic keyword-based distress severity classification.
- Added an initial category mapping pipeline for target label generation.

This provided a functional proof of concept demonstrating the complete data collection and preprocessing workflow.

---

# Mentor Feedback 

After reviewing the baseline implementation, mentor suggested expanding and strengthening the dataset preparation process before beginning NLP model development.


---

# Mentor Recommendations

Based on the feedback, the following improvements were incorporated into the pipeline.

## 1. Increase Dataset Size

The original dataset was insufficient for meaningful NLP experimentation.

**Improvement:**

- Expanded scraping across additional communities and feed endpoints.
- Increased the final dataset to **500+ cleaned posts**, providing a stronger foundation for model training and evaluation.

---

## 2. Merge All Data Sources

Instead of maintaining separate datasets, all collected posts were consolidated into a single unified dataset.

**Improvement:**

- Combined data collected from multiple subreddits and RSS feeds.
- Standardized the schema across all records.
- Generated one centralized master dataset for downstream processing.

---

## 3. Ensure Complete Category Coverage

Every sample should belong to at least one predefined target category.

**Improvement:**

- Enhanced keyword matching logic.
- Implemented a fallback assignment strategy to eliminate unlabeled rows.
- Guaranteed that every record receives at least one target label.

---

## 4. Improve Text Preprocessing

Noise removal was expanded beyond basic cleaning.

**Improvement:**

The preprocessing pipeline now removes:

- HTML tags
- HTML entities
- URLs and hyperlinks
- Markdown artifacts
- RSS formatting
- Emojis
- Unicode symbols
- Non-ASCII characters
- Excess punctuation and formatting noise

while preserving meaningful sentence structure for NLP processing.

---

*Updated: 23/07/2026*

