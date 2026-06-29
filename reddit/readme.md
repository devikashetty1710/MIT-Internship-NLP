# Reddit Data Extraction & NLP Preprocessing Pipeline

This subdirectory contains the production-ready implementation of the Reddit ingestion and text-normalization pipeline for the **Mental Illness Risk-Indicator Detection System**. The architecture follows standardized, professional development practices to safely capture, scrub, and structure public mental health discourse records.

---

## What We Did (Summary of Work)

* **Class-Based Architecture:** Refactored the collection scripts into an object-oriented class structure (`RedditRSSScraper` and `RedditPreprocessor`) to guarantee clean modular code that aligns with the project's multi-platform standards.
* **Robust RSS Ingestion & Parsing:** Programmed a secure RSS feed workaround using regular expressions to safely extract target strings (e.g., parsing subreddit names from complex URLs) and securely fetch records without hitting standard API restrictions.
* **Unified Database Mapping:** Linked the stream directly to local storage, writing documents into a dedicated MongoDB collection (`reddit_posts`) mapping cleanly onto our project's standardized Unified Schema (`post_id`, `platform`, `raw_text`).
* **Advanced HTML & Noise Cleansing:** Integrated step-by-step regular expression filters inside the preprocessing block to completely eliminate raw HTML tables, markdown code artifacts (``), structural wrappers (`<div class="md">`), and web hyper-links.
* **Linguistic Isolation & Stopword Scrubbing:** Configured institutional-grade tokenization using `nltk.tokenize.word_tokenize` and a pre-compiled English corpus list to drop high-frequency grammar filler words (like "the", "and", "of") and keep only meaningful context markers.
* **Semantic Lemmatization:** Integrated the NLTK `WordNetLemmatizer` engine to collapse structural variants of text (e.g., transforming plural terms or dynamic verb states like *accounts* $\rightarrow$ *account*, *offering* $\rightarrow$ *offer*) back down to their base dictionary roots.
* **Pipeline Persistence & File Export:** Configured an automatic write transaction that updates a distinct database collection (`cleaned_reddit_posts`) while dropping a complete, non-truncated workspace spreadsheet file (`reddit/cleaned_reddit_posts.csv`) ready for multi-label tag annotation.

---

## Prerequisites

Before executing the pipeline, ensure your active Python environment contains the necessary project dependencies and local databases are live:

1. **Active Virtual Environment:** Ensure your environment sandbox is turned on (`(venv)` should be visible in your terminal sidebar).
2. **Local Database Service:** A local instance of **MongoDB Server** must be running in the background on your machine.
3. **Python Package Dependencies:** The following libraries must be present inside your environment tracking (appended to `requirements.txt`):
   * `feedparser` (For digesting public RSS XML content streams)
   * `pymongo` (The driver bridge mapping operations to MongoDB)
   * `pandas` (For handling structure metrics dataframes)
   * `nltk` (The Natural Language Toolkit ecosystem)
4. **NLTK Corpus Mapping Dependencies:**
   The background tokenizer requires specific dictionary resource tables to run. Ensure you have run these downloads inside your active environment's interactive prompt:
   * `punkt` & `punkt_tab` (Sentence and word parsing logic dependencies)
   * `stopwords` (Standard filler word exclusion directories)
   * `wordnet` (Morphological lemmatization base mappings)

---

## Steps to Run the Pipeline

Always run the commands from the root directory of your project folder (`MENTAL-ILLNESS-NLP`) with your virtual environment active:

### Step 1: Ingest Raw Data (Layer 01 & 02)
Run the automated scraper file to pull public raw data rows directly from the subreddit stream and feed them securely into MongoDB:
```bash
python reddit/reddit_json_scraper.py