import pandas as pd
import re
import os

# Create eval folder if it doesn't exist
os.makedirs("eval", exist_ok=True)

# Load master dataset
DATASET_PATH = "merged_dataset/unified_master_dataset.csv"

try:
    df = pd.read_csv(DATASET_PATH)
except FileNotFoundError:
    print(f"Error: {DATASET_PATH} not found. Please check the path.")
    exit()

print("="*60)
print(" DATASET ANNOTATION AUDIT SUMMARY ")
print("="*60)

# 1. Row count & null checks
print(f"Total Records: {len(df)}")
print("\nMissing Values in Key Columns:")
print(df[['caption', 'severity']].isnull().sum())

# 2. Class distribution
print("\nSeverity Class Distribution:")
print(df['severity'].value_counts())

# 3. Quality Check: Define keyword patterns
high_risk_keywords = [
    r'\bsuicide\b', r'\bkill myself\b', r'\bend my life\b', 
    r'\bself harm\b', r'\bhelpline\b', r'\boverdose\b'
]
distress_keywords = [
    r'\bdepressed\b', r'\banxiety\b', r'\bhopeless\b', 
    r'\bworthless\b', r'\bstruggle\b', r'\bmental health\b'
]

pattern_high_risk = '|'.join(high_risk_keywords)
pattern_distress = '|'.join(distress_keywords)

df['caption_clean'] = df['caption'].fillna('').astype(str).str.lower()

# --- CHECK 1: False Negatives ---
# Flag 'Low' severity posts containing critical high-risk keywords
suspicious_low = df[
    (df['severity'].str.lower() == 'low') & 
    (df['caption_clean'].str.contains(pattern_high_risk, regex=True, na=False))
]

print(f"\n[!] Flagged {len(suspicious_low)} 'Low' severity posts containing HIGH-RISK keywords.")
if not suspicious_low.empty:
    audit_file_low = "eval/flagged_false_negatives.csv"
    suspicious_low[['post_id', 'caption', 'severity', 'platform']].to_csv(audit_file_low, index=False)
    print(f"    ➔ Exported to: {audit_file_low} (Review these manually!)")
else:
    print("    All 'Low' labels passed the high-risk keyword sanity check.")

# --- CHECK 2: False Positives ---
# Flag 'High' or 'Medium' severity posts containing ZERO distress keywords
no_distress = ~df['caption_clean'].str.contains(pattern_distress, regex=True, na=False)
suspicious_high = df[
    (df['severity'].str.lower().isin(['high', 'medium'])) & 
    (no_distress)
]

print(f"\n[!] Flagged {len(suspicious_high)} 'High/Medium' severity posts with ZERO distress keywords.")
if not suspicious_high.empty:
    audit_file_high = "eval/flagged_false_positives.csv"
    suspicious_high[['post_id', 'caption', 'severity', 'platform']].to_csv(audit_file_high, index=False)
    print(f"    ➔ Exported to: {audit_file_high} (Review these manually!)")
else:
    print("    All 'High/Medium' labels contain expected distress keywords.")

print("\n" + "="*60)
print(" Audit complete. Please review flagged CSVs in the 'eval/' folder.")
print("="*60)