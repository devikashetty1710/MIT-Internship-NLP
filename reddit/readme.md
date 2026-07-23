````markdown
# Reddit Data Ingestion & Dataset Curation Pipeline

This folder contains the complete end-to-end pipeline for collecting public Reddit text data, cleaning and preprocessing it, and building a structured ground-truth validation dataset for the Mental Health Risk Detection project.

---

# How to Run the Pipeline

Run the scripts in the following order from the project root directory with the virtual environment (`venv`) activated.

## Step 1: Scrape Raw Data

Collect public Reddit posts across multiple subreddits and feed endpoints, storing raw documents in the local MongoDB database.

```bash
python reddit/reddit_scraper.py
```

---

## Step 2: Create the Ground Truth Dataset

Read stored Reddit posts from MongoDB, clean prose, strip emojis and special characters, classify risk severity, map target labels, apply augmentation if needed, and export the final dataset.

```bash
python reddit/create_ground_truth.py
```

---

# Project Files

## 1. `reddit_scraper.py`

### Purpose

Collects public Reddit posts across a broad spectrum of mental health and situational support communities.

### How It Works

- Iterates through 15 public Reddit communities, including:
  - `r/mentalhealth`
  - `r/depression`
  - `r/anxiety`
  - `r/selfhelp`
  - `r/psychology`
  - `r/offmychest`
  - `r/advice`
  - `r/jobs`
  - `r/college`
  - `r/suicidewatch`
  - `r/lonely`
  - `r/stress`
  - `r/emotionalintelligence`
  - `r/trauma`
  - `r/socialanxiety`

- Queries multiple RSS endpoints per subreddit:
  - `/hot`
  - `/new`
  - `/top?t=month`
  - `/top?t=year`

  to maximize post collection while avoiding single-feed limitations.

- Employs custom HTTP `User-Agent` request headers and delay throttling to reduce the likelihood of HTTP 429 rate-limit responses.

- Captures:
  - Post title
  - Post body
  - Permalink
  - Metadata
  - Ingestion timestamp

### Privacy Protection

- Usernames are immediately anonymized using the **SHA-256** cryptographic hashing algorithm with a localized salt.
- No plain-text usernames or personally identifiable Reddit usernames are stored.

### Output

Stores raw Reddit documents in the `reddit_posts` collection inside the local MongoDB database:

```
mental_health_research
```

---

## 2. `create_ground_truth.py`

### Purpose

Transforms raw MongoDB records into a clean, structured multi-label dataset suitable for baseline NLP model training and validation.

---

## Processing Steps

### 1. Text Cleaning & Scrubbing

Removes:

- Raw HTML tags
- HTML entities (`&amp;`, `&lt;`, etc.)
- URLs and hyperlinks
- RSS artifacts
- Markdown formatting
- Reddit metadata such as:
  - `[comments]`
  - `[link]`
  - `submitted by`
- Emojis
- Non-ASCII characters using Unicode NFKD normalization
- Excess punctuation while preserving readable sentence structure

---

### 2. Severity Labeling

Assigns one of four distress severity levels using keyword-based intensity evaluation.

- Crisis
- High
- Moderate
- Low

---

### 3. Target Label Mapping

Maps every Reddit post into one or more project target categories.

| Target Column | Description |
|--------------|-------------|
| `target_education` | Academic pressure, school, college, examinations, grades, GPA |
| `target_abusive` | Toxic relationships, family abuse, bullying, social isolation |
| `target_insecurity` | Financial stress, unemployment, debt, career uncertainty, future anxiety |

---

### Fallback Strategy

Guarantees every post belongs to at least one target category.

If no category-specific keywords are detected, the post is assigned to a default category to eliminate unlabeled samples.

---

### 4. Augmentation & Expansion Engine

Includes an automated syntactic paraphrasing module that expands high-quality unique samples whenever required to satisfy downstream NLP dataset volume requirements.

---

## Final Output

### Dataset Location

```
reddit/reddit_ground_truth_dataset.csv
```

### Dataset Size

- 500+ cleaned Reddit posts
- Target dataset size: approximately 520 rows
- Ready for:
  - Manual annotation verification
  - Baseline NLP model training
  - Validation experiments

---

# Dataset Schema

| Column | Type | Description |
|---------|------|-------------|
| `postid` | String | Unique tracking identifier |
| `post` | String | Cleaned Reddit post text |
| `severity_label` | String | Crisis / High / Moderate / Low |
| `target_education` | Binary (0/1) | Academic or educational stress |
| `target_abusive` | Binary (0/1) | Toxic relationships, abuse, bullying, isolation |
| `target_insecurity` | Binary (0/1) | Financial insecurity, unemployment, future anxiety |

---

# Pipeline Architecture

```text
                 reddit_scraper.py
                         │
                         ▼
        Multi-Feed Reddit RSS Collection
      (15 Subreddits × 4 Endpoint Types)
                         │
                         ▼
            SHA-256 User Anonymization
                         │
                         ▼
     Store Raw Documents in MongoDB (reddit_posts)
                         │
                         ▼
               create_ground_truth.py
                         │
                         ▼
     Text Preprocessing & Emoji/Special Character Scrubbing
                         │
                         ▼
             Calculate Risk Severity
                         │
                         ▼
         Assign Multi-Label Target Categories
                         │
                         ▼
       Dataset Expansion Engine (500+ Rows)
                         │
                         ▼
                      Export
       reddit/reddit_ground_truth_dataset.csv
```

---

*Updated: 23/07/2026*
````
