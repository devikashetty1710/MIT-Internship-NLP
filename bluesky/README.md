# Bluesky Mental Health Post Scraper

## Project Description

This project collects mental health related posts from the Bluesky social media platform using the AT Protocol API. The collected posts are stored in MongoDB, cleaned using Natural Language Processing (NLP) techniques, and converted into a structured dataset for mental health analysis.

The final dataset contains:
- Post ID
- Caption
- Timestamp
- Mental Health label
- Category
- Severity

## Features

- Collects mental health related posts from Bluesky
- Stores collected data in MongoDB
- Removes duplicate posts
- Cleans text by removing URLs, emojis and special characters
- Assigns severity levels (High, Medium, Low)
- Categorizes posts into:
  - Education
  - Social Status
  - Appearance
- Exports the final dataset as a CSV file

## Project Structure
bluesky/
├── bluesky_scraper.py
├── ground_truth_generator.py
├── bluesky.csv
├── README.md
├── requirements.txt


## Technologies Used

- Python
- Bluesky AT Protocol API
- MongoDB
- Pandas
- Regular Expressions (re)
- HTML Parser (html)

## Output

The project generates:

- bluesky.csv

containing the processed mental health dataset.

