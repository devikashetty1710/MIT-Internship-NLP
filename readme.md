# Mental Health Risk Indicator Detection Pipeline

This project builds an end-to-end data engineering and NLP pipeline that collects public social media text, protects user privacy, cleans formatting noise, and generates structured ground-truth datasets for identifying situational risk indicators.

---

## Problem Statement

People often share personal struggles, emotional distress, and life challenges on public online discussion platforms. While this information can support NLP research, it presents several challenges:

1. Public posts are highly unstructured and contain HTML, emojis, hyperlinks, markdown artifacts, and other noisy text.
2. Plain-text usernames introduce unnecessary privacy risks when storing collected data.
3. Data collected from multiple communities exists in fragmented formats and requires consolidation before analysis.
4. Machine learning models require clean, standardized, and consistently labeled datasets to effectively learn patterns associated with situational risk indicators.

---

## Solution Overview

To address these challenges, we developed a multi-stage data engineering pipeline that transforms raw public text into a structured dataset suitable for downstream NLP tasks.

The pipeline performs the following operations:

- **Multi-Source Data Collection:** Collects publicly available posts from multiple online discussion communities (Reddit, Bluesky, and Mastodon).
- **Privacy Preservation:** Anonymizes all usernames using irreversible SHA-256 hashing before storage.
- **Centralized Storage:** Stores raw documents inside a local MongoDB database.
- **Text Preprocessing:** Removes HTML tags, URLs, markdown artifacts, emojis, special characters, and formatting noise.
- **Automatic Label Generation:** Assigns distress severity levels and maps each post into predefined target categories.
- **Ground-Truth Dataset Creation:** Produces a structured CSV dataset ready for annotation, analysis, and baseline NLP model development.

## Work Completed Before Mentor Review

Before presenting the project to our mentor, the following baseline pipeline had already been implemented:
Configured a Python virtual environment (venv) for dependency management.
Installed and configured MongoDB Community Server for document storage.
Developed an initial Reddit RSS-based scraper for collecting public posts.
Created a preliminary ground-truth dataset containing approximately 115–125 cleaned samples.
Implemented basic keyword-based distress severity classification.
Added an initial category mapping pipeline for target label generation.
This provided a functional proof of concept demonstrating the complete data collection and preprocessing workflow.

## Mentor Feedback & Recommendations
After reviewing the baseline implementation, our mentor suggested expanding and strengthening the dataset preparation process before beginning NLP model development. Based on the feedback, the following improvements were incorporated into the pipeline:

1. Increase Dataset Size
The original dataset was insufficient for meaningful NLP experimentation.
Improvement: Expanded scraping across additional communities and feed endpoints, increasing the final dataset to 1,500+ cleaned posts, providing a stronger foundation for model training and evaluation.

2. Merge All Data Sources
Instead of maintaining separate datasets, all collected posts were consolidated into a single unified dataset.
Improvement: Combined data collected from Reddit, Bluesky, and Mastodon. Standardized the schema across all records to generate one centralized master dataset (unified_master_dataset.csv) for downstream processing.

3. Ensure Complete Category Coverage
Every sample should belong to at least one predefined target category.
Improvement: Enhanced keyword matching logic and implemented a fallback assignment strategy to eliminate unlabeled rows, guaranteeing that every record receives at least one target label.

4. Improve Text Preprocessing
Noise removal was expanded beyond basic cleaning. The preprocessing pipeline now removes HTML tags, HTML entities, URLs, markdown artifacts, RSS formatting, emojis, Unicode symbols, non-ASCII characters, and excess punctuation while preserving meaningful sentence structure.

## Advanced NLP Pipeline & Model Evaluation (Latest Updates)

Following the dataset consolidation, the following advanced NLP tasks were executed as per the mentor's latest guidelines:

5. Annotation Audit and Quality Assurance
To ensure the reliability of our ground-truth labels, an automated annotation audit script (audit_annotations.py) was developed.

False Negative Check: Scanned all posts labeled as Low severity for critical high-risk keywords (e.g., suicide, self-harm, overdose).
Result: 0 false negatives were found, confirming the safety and accuracy of critical labeling.
False Positive Check: Flagged High and Medium severity posts that lacked standard distress keywords for manual human review, ensuring conversational distress indicators were correctly validated.

6. Head and Tail Truncation for Long Texts
Social media posts often exceed the standard input limits of transformer models.

Implementation: For posts exceeding 500 words, we implemented a strict head-and-tail truncation strategy.
Logic: The script retains the first 256 tokens and the last 256 tokens of the text.
This ensures that both the introductory context and the concluding sentiment of the post are preserved while strictly adhering to the 512-token maximum limit of BERT and RoBERTa architectures.
The approach leaves exactly 2 slots for the [CLS] and [SEP] tokens.

7. Model Benchmarking: BERT and RoBERTa
We evaluated two foundational transformer models to establish a baseline for mental health risk indicator detection:

Models: bert-base-uncased and roberta-base.
Methodology: To ensure robust and unbiased evaluation, we utilized 5-Fold Stratified Cross-Validation, repeated with 3 distinct random seeds (42, 100, 2024).
This resulted in 15 independent evaluation runs per model.
Metrics Reported: Mean and Standard Deviation for Accuracy, Precision, Recall, and Macro F1-Score.

## Final Benchmark Results
| Model | Accuracy (Mean ± Std) | Precision (Macro) | Recall (Macro) | F1-Score (Macro) |
|---|---:|---:|---:|---:|
| **BERT (base-uncased)** | 0.7215 ± 0.0245 | 0.7226 ± 0.0298 | 0.7135 ± 0.0261 | 0.7166 ± 0.0268 |
| **RoBERTa (base)** | **0.7378 ± 0.0282** | **0.7427 ± 0.0305** | **0.7299 ± 0.0282** | **0.7341 ± 0.0281** |
Conclusion: RoBERTa outperformed BERT across all reported metrics, demonstrating higher efficacy in capturing the nuanced, conversational distress patterns present in social media text.

Updated: 30/08/2026