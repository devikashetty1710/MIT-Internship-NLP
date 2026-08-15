import pandas as pd
import re
import os

# Create eval folder if it doesn't exist
os.makedirs("eval", exist_ok=True)

# Load master dataset
DATASET_PATH = "merged_dataset/unified_master_dataset.csv"
df = pd.read_csv(DATASET_PATH)

print("="*50)
print(" DATASET ANNOTATION AUDIT SUMMARY ")
print("="*50)

# 1. Row count & null checks
print(f"Total Records: {len(df)}")
print("\nMissing Values:")
print(df[['caption', 'severity']].isnull().sum())

# 2. Class distribution
print("\nSeverity Class Distribution:")
print(df['severity'].value_counts())

# 3. Quality Check: Flag 'Low' severity posts containing high-risk keywords
high_risk_keywords = [
    r'\bsuicide\b', r'\bkill myself\b', r'\bend my life\b', 
    r'\bself harm\b', r'\bhelpline\b', r'\boverdose\b'
]
pattern = '|'.join(high_risk_keywords)

df['caption_clean'] = df['caption'].fillna('').astype(str).str.lower()
suspicious_low = df[(df['severity'].str.lower() == 'low') & (df['caption_clean'].str.contains(pattern, regex=True))]

print(f"\n[!] Flagged {len(suspicious_low)} 'Low' severity posts containing critical high-risk keywords.")

if not suspicious_low.empty:
    audit_file = "eval/flagged_low_severity_posts.csv"
    suspicious_low[['post_id', 'caption', 'severity']].to_csv(audit_file, index=False)
    print(f"Exported flagged rows for manual review to: {audit_file}")
else:
    print("All 'Low' labels passed the keyword sanity check successfully.")