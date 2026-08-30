import os
import torch
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.linear_model import LogisticRegression
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm

# Set PyTorch to use available CPU threads for faster extraction
torch.set_num_threads(os.cpu_count() or 4)

def head_tail_tokenize(texts, tokenizer, max_len=512, head_len=255, tail_len=255):
    """
    Mentor Requirement: Head and tail truncation (first 256 and last 256 tokens).
    CRITICAL FIX: BERT/RoBERTa max length is strictly 512. 
    We cap text tokens at 510 (255 + 255) to leave exactly 2 slots for [CLS] and [SEP].
    """
    input_ids, attention_masks = [], []
    start_tok = tokenizer.cls_token_id if tokenizer.cls_token_id is not None else tokenizer.bos_token_id
    end_tok = tokenizer.sep_token_id if tokenizer.sep_token_id is not None else tokenizer.eos_token_id
    pad_tok = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    for text in texts:
        # Encode without special tokens first to count accurately
        tokens = tokenizer.encode(str(text), add_special_tokens=False)
        
        # If tokens exceed 510, truncate to 255 head + 255 tail
        if len(tokens) > 510:
            tokens = tokens[:head_len] + tokens[-tail_len:]
            
        # Add special tokens ([CLS] at start, [SEP] at end) -> Total max 512
        tokens = [start_tok] + tokens + [end_tok]
        
        # Padding to max_len (512)
        pad_len = max_len - len(tokens)
        mask = [1] * len(tokens) + [0] * pad_len
        tokens = tokens + [pad_tok] * pad_len

        input_ids.append(tokens)
        attention_masks.append(mask)

    return torch.tensor(input_ids, dtype=torch.long), torch.tensor(attention_masks, dtype=torch.long)

@torch.no_grad()
def extract_transformer_features(model_name, texts, batch_size=32):
    print(f"\n1. Extracting 768-dim embeddings using {model_name} (One-time pass)...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()

    input_ids, attention_masks = head_tail_tokenize(texts, tokenizer)
    dataset = torch.utils.data.TensorDataset(input_ids, attention_masks)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)

    embeddings = []
    for b_ids, b_masks in tqdm(dataloader, desc="Extracting Features"):
        outputs = model(input_ids=b_ids, attention_mask=b_masks)
        
        # Use mean pooling over tokens
        mask_expanded = b_masks.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        sum_embeddings = torch.sum(outputs.last_hidden_state * mask_expanded, 1)
        sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
        mean_pooled = sum_embeddings / sum_mask
        embeddings.append(mean_pooled.cpu().numpy())

    return np.vstack(embeddings)

def run_fast_cross_validation(model_name, df, seeds=[42, 100, 2024], n_splits=5):
    # Step 1: Extract features once (cached for speed)
    features = extract_transformer_features(model_name, df['caption'].values)

    unique_labels = sorted(df['severity'].unique())
    label2id = {l: i for i, l in enumerate(unique_labels)}
    df['label_id'] = df['severity'].map(label2id)
    y = df['label_id'].values

    print(f"2. Running {n_splits}-Fold Stratified CV x {len(seeds)} Seeds on cached {model_name} features...")
    results = []

    for seed in seeds:
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        for fold, (train_idx, val_idx) in enumerate(skf.split(features, y)):
            X_train, y_train = features[train_idx], y[train_idx]
            X_val, y_val = features[val_idx], y[val_idx]

            clf = LogisticRegression(max_iter=1000, random_state=seed)
            clf.fit(X_train, y_train)
            pred_labels = clf.predict(X_val)

            acc = accuracy_score(y_val, pred_labels)
            p, r, f1, _ = precision_recall_fscore_support(
                y_val, pred_labels, average='macro', zero_division=0
            )
            results.append({
                'seed': seed, 
                'fold': fold + 1, 
                'accuracy': acc, 
                'precision': p, 
                'recall': r, 
                'f1': f1
            })

    res_df = pd.DataFrame(results)
    
    # Mentor Requirement: Report mean and standard deviations
    return {
        'Model': model_name,
        'Accuracy': f"{res_df['accuracy'].mean():.4f} ± {res_df['accuracy'].std():.4f}",
        'Precision (Macro)': f"{res_df['precision'].mean():.4f} ± {res_df['precision'].std():.4f}",
        'Recall (Macro)': f"{res_df['recall'].mean():.4f} ± {res_df['recall'].std():.4f}",
        'F1-Score (Macro)': f"{res_df['f1'].mean():.4f} ± {res_df['f1'].std():.4f}"
    }

if __name__ == "__main__":
    DATASET_PATH = "merged_dataset/unified_master_dataset.csv"
    
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print(f"Error: {DATASET_PATH} not found.")
        exit()

    print("="*60)
    print(" STARTING MODEL EVALUATION PIPELINE ")
    print("="*60)

    bert_metrics = run_fast_cross_validation("bert-base-uncased", df)
    roberta_metrics = run_fast_cross_validation("roberta-base", df)

    final_report = pd.DataFrame([bert_metrics, roberta_metrics])

    print("\n" + "="*70)
    print(" FINAL BENCHMARK SUMMARY (5-Fold CV x 3 Seeds, Mean ± Std) ")
    print("="*70)
    print(final_report.to_string(index=False))
    print("="*70)

    os.makedirs("eval", exist_ok=True)
    final_report.to_csv("eval/cross_val_results.csv", index=False)
    print("\nSaved final summary table to: eval/cross_val_results.csv")