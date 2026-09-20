import os
import torch
import numpy as np
import pandas as pd
import warnings
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.linear_model import LogisticRegression
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm

# Suppress the "token length > 512" warning since we handle it manually
warnings.filterwarnings("ignore", message="Token indices sequence length is longer than the specified maximum sequence length")

def head_tail_tokenize(texts, tokenizer, max_len=512, head_len=255, tail_len=255):
    """
    Mentor Requirement: Head and tail truncation (first 256 and last 256 tokens).
    We use 255+255=510 to leave exactly 2 slots for [CLS] and [SEP] tokens.
    """
    input_ids, attention_masks = [], []
    start_tok = tokenizer.cls_token_id if tokenizer.cls_token_id is not None else tokenizer.bos_token_id
    end_tok = tokenizer.sep_token_id if tokenizer.sep_token_id is not None else tokenizer.eos_token_id
    pad_tok = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    for text in texts:
        tokens = tokenizer.encode(str(text), add_special_tokens=False)
        if len(tokens) > (head_len + tail_len):
            tokens = tokens[:head_len] + tokens[-tail_len:]
        tokens = [start_tok] + tokens + [end_tok]
        pad_len = max_len - len(tokens)
        mask = [1] * len(tokens) + [0] * pad_len
        tokens = tokens + [pad_tok] * pad_len
        input_ids.append(tokens)
        attention_masks.append(mask)
    return torch.tensor(input_ids, dtype=torch.long), torch.tensor(attention_masks, dtype=torch.long)

@torch.no_grad()
def extract_features(model_name, texts, batch_size=32):
    """Extract 768-dim embeddings using the frozen model (One-time pass)."""
    print(f"\n1. Extracting embeddings using {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()

    input_ids, attention_masks = head_tail_tokenize(texts, tokenizer)
    dataset = torch.utils.data.TensorDataset(input_ids, attention_masks)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)

    embeddings = []
    for b_ids, b_masks in tqdm(dataloader, desc="Extracting Features"):
        outputs = model(input_ids=b_ids, attention_mask=b_masks)
        # Mean pooling over tokens
        mask_expanded = b_masks.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        sum_embeddings = torch.sum(outputs.last_hidden_state * mask_expanded, 1)
        sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
        mean_pooled = sum_embeddings / sum_mask
        embeddings.append(mean_pooled.cpu().numpy())
    return np.vstack(embeddings)

def run_fast_cv(model_name, df, seeds=[42, 100, 2024], n_splits=5):
    """Run 5-Fold Stratified CV repeated with 3 random seeds using Logistic Regression."""
    features = extract_features(model_name, df['cleaned_text'].values)
    
    # Encode string labels ('Low', 'Medium', 'High') to integers (0, 1, 2)
    le = LabelEncoder()
    y = le.fit_transform(df['severity'].values)
    
    all_metrics = {'accuracy': [], 'precision': [], 'recall': [], 'f1': []}
    
    print(f"2. Running {n_splits}-Fold CV x {len(seeds)} Seeds...")
    for seed in seeds:
        skf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=1, random_state=seed)
        for fold, (train_idx, val_idx) in enumerate(skf.split(features, y)):
            X_train, X_val = features[train_idx], features[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Use class_weight='balanced' to handle the uneven distribution of Low/Medium/High
            clf = LogisticRegression(max_iter=1000, random_state=seed, class_weight='balanced')
            clf.fit(X_train, y_train)
            preds = clf.predict(X_val)
            
            acc = accuracy_score(y_val, preds)
            p, r, f1, _ = precision_recall_fscore_support(y_val, preds, average='macro', zero_division=0)
            
            all_metrics['accuracy'].append(acc)
            all_metrics['precision'].append(p)
            all_metrics['recall'].append(r)
            all_metrics['f1'].append(f1)
            
    return {
        'Model': model_name,
        'Accuracy': f"{np.mean(all_metrics['accuracy']):.4f} ± {np.std(all_metrics['accuracy']):.4f}",
        'Precision (Macro)': f"{np.mean(all_metrics['precision']):.4f} ± {np.std(all_metrics['precision']):.4f}",
        'Recall (Macro)': f"{np.mean(all_metrics['recall']):.4f} ± {np.std(all_metrics['recall']):.4f}",
        'F1-Score (Macro)': f"{np.mean(all_metrics['f1']):.4f} ± {np.std(all_metrics['f1']):.4f}"
    }

if __name__ == "__main__":
    # Load the preprocessed dataset
    df = pd.read_csv('merged_dataset/preprocessed_dataset.csv')
    
    # Models to test (DistilBERT is included as it's faster and smaller)
    models_to_test = ['bert-base-uncased', 'roberta-base', 'distilbert-base-uncased']
    final_report = []
    
    print("="*70)
    print(" STARTING FAST MODEL EVALUATION PIPELINE ")
    print("="*70)
    
    for model in models_to_test:
        metrics = run_fast_cv(model, df)
        final_report.append(metrics)
        
    res_df = pd.DataFrame(final_report)
    
    print("\n" + "="*70)
    print(" FINAL BENCHMARK SUMMARY (5-Fold CV x 3 Seeds, Mean ± Std) ")
    print("="*70)
    print(res_df.to_string(index=False))
    print("="*70)
    
    os.makedirs("eval", exist_ok=True)
    res_df.to_csv("eval/cross_val_results.csv", index=False)
    print("\n Saved final summary table to: eval/cross_val_results.csv")