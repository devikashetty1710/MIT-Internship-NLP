# Reddit Data Ingestion & Dataset Curation Pipeline

This folder contains the complete end-to-end pipeline for collecting public Reddit text data, cleaning and preprocessing it, and building a structured ground-truth validation dataset for the Mental Health Risk Detection project.

---

# How to Run the Pipeline

Run the scripts in the following order from the project root directory with the virtual environment (`venv`) activated.

## Step 1: Scrape Raw Data

Collect public Reddit posts and store them in the local database.

```bash
python reddit/reddit_scraper.py
```

## Step 2: Create the Ground Truth Dataset

Read the stored Reddit posts, clean the text, classify severity, generate target labels, and export the final dataset.

```bash
python reddit/create_ground_truth.py
```

---

# Project Files

## 1. `reddit_scraper.py`

### Purpose

Collects public Reddit posts from multiple mental health-related communities.

### How It Works

- Iterates through 11 public Reddit communities, including:
  - `r/mentalhealth`
  - `r/depression`
  - `r/anxiety`
  - and other related subreddits.
- Uses Reddit's public RSS feeds, avoiding the need for API credentials.
- Fetches post title, content, metadata, and timestamps.

### Privacy Protection

- Usernames are immediately anonymized using the SHA-256 hashing algorithm.
- No personally identifiable usernames are stored.

### Output

Stores all collected posts in the `reddit_posts` collection of the local database.

---

## 2. `create_ground_truth.py`

### Purpose

Transforms the raw Reddit posts into a clean, structured dataset suitable for validation and downstream machine learning tasks.

### Processing Steps

#### Text Cleaning

Removes:

- URLs
- HTML entities
- RSS artifacts
- `[comments]`
- `[link]`
- Extra whitespace
- Other unnecessary formatting noise

#### Severity Labeling

Assigns one of four severity levels using a weighted keyword scoring approach:

- Crisis
- High
- Moderate
- Low

#### Target Label Mapping

Maps each post into one or more project target categories.

| Target Column | Description |
|--------------|-------------|
| `target_education` | Academic pressure, school, college, exams, grades |
| `target_abusive` | Toxic relationships, family abuse, bullying, social isolation |
| `target_insecurity` | Financial stress, unemployment, future uncertainty |

#### Fallback Strategy

If a post receives a high severity score but does not match any predefined target category, the script automatically assigns it to the most appropriate category to avoid unlabeled records.

---

# Final Output

## Dataset Location

```
reddit/reddit_ground_truth_dataset.csv
```

## Dataset Size

- Approximately 115 unique cleaned posts
- Ready for manual validation and model development

## Dataset Schema

| Column | Description |
|---------|-------------|
| `postid` | Unique identifier for each Reddit post |
| `post` | Cleaned post text |
| `severity_label` | Risk severity (Crisis, High, Moderate, Low) |
| `target_education` | 1 if the post relates to academic stress, otherwise 0 |
| `target_abusive` | 1 if the post relates to abuse, toxic relationships, or isolation, otherwise 0 |
| `target_insecurity` | 1 if the post relates to financial insecurity, unemployment, or future anxiety, otherwise 0 |

---

# Pipeline Summary

```
reddit_scraper.py
        │
        ▼
Collect Reddit RSS Posts
        │
        ▼
Anonymize User Information
        │
        ▼
Store Raw Posts (reddit_posts)
        │
        ▼
create_ground_truth.py
        │
        ▼
Clean & Normalize Text
        │
        ▼
Calculate Severity Labels
        │
        ▼
Assign Target Categories
        │
        ▼
Export
reddit_ground_truth_dataset.csv
```
*Updated: 17/07/2026*