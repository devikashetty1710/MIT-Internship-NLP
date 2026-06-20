# Mental Health Risk Detection on Social Media using NLP

[cite_start]A relationship-aware NLP pipeline designed to collect public discourse data, analyze indicators of distress, attribute contextual domains, and grade signal severity[cite: 6]. 

## 📌 Project Architecture
* [cite_start]**Layer 01 & 02:** Data Collection via public RSS feeds and local document storage using MongoDB[cite: 181, 182, 560].
* [cite_start]**Layer 03:** Text preprocessing, PII cleaning, tokenization, and initial emotion feature extraction[cite: 184, 221, 222].
* [cite_start]**Layer 04:** Cause attribution and multi-tier clinical severity grading[cite: 185, 188].

---

## 🛠️ Prerequisites & Installation

### 1. Database Infrastructure
[cite_start]You must have **MongoDB Community Server** and **MongoDB Compass** installed on your local system[cite: 552].

[cite_start]To start the database daemon on Windows, open PowerShell as an **Administrator** and execute[cite: 554]:
```bash
net start mongoDB