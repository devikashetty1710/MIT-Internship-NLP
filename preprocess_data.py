import re
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import string

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

class TextPreprocessor:
    def __init__(self, remove_multilingual_low=True, min_multilingual_threshold=0.05):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.remove_multilingual_low = remove_multilingual_low
        self.min_threshold = min_multilingual_threshold
    
    def remove_non_alphanumeric(self, text):
        """Remove non-alphabetic and non-numeric characters"""
        # Keep spaces, letters, and numbers
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        return text
    
    def remove_special_patterns(self, text):
        """Remove URLs, HTML tags, mentions, hashtags, emojis"""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        # Remove mentions (@username)
        text = re.sub(r'@\w+', '', text)
        # Remove hashtags (keep the text)
        text = re.sub(r'#(\w+)', r'\1', text)
        # Remove emojis and unicode symbols
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize(self, text):
        """Tokenize text into words"""
        return word_tokenize(text.lower())
    
    def remove_stopwords(self, tokens):
        """Remove stopwords"""
        return [token for token in tokens if token not in self.stop_words]
    
    def apply_stemming(self, tokens):
        """Apply Porter Stemming"""
        return [self.stemmer.stem(token) for token in tokens]
    
    def apply_lemmatization(self, tokens):
        """Apply WordNet Lemmatization"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def detect_language_simple(self, text):
        """Simple heuristic to detect if text is primarily English"""
        # Count English letters vs total characters
        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        total_chars = sum(1 for c in text if c.isalpha())
        
        if total_chars == 0:
            return 'en', 0.0
        
        ratio = english_chars / total_chars
        return 'en' if ratio > 0.7 else 'other', ratio
    
    def preprocess(self, text, apply_stemming=False, apply_lemmatization=True):
        """Complete preprocessing pipeline"""
        if not isinstance(text, str):
            return ""
        
        # Remove special patterns (URLs, HTML, mentions, etc.)
        text = self.remove_special_patterns(text)
        
        # Remove non-alphanumeric characters
        text = self.remove_non_alphanumeric(text)
        
        # Check language if removing multilingual
        if self.remove_multilingual_low:
            lang, ratio = self.detect_language_simple(text)
            if ratio < self.min_threshold:
                return ""  # Skip low-confidence multilingual text
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove stopwords
        tokens = self.remove_stopwords(tokens)
        
        # Apply stemming or lemmatization
        if apply_stemming:
            tokens = self.apply_stemming(tokens)
        elif apply_lemmatization:
            tokens = self.apply_lemmatization(tokens)
        
        return ' '.join(tokens)

# Load and preprocess dataset
def load_and_preprocess_dataset(filepath, apply_stemming=False, apply_lemmatization=True):
    """Load dataset and apply preprocessing"""
    df = pd.read_csv(filepath)
    
    preprocessor = TextPreprocessor(remove_multilingual_low=True, min_multilingual_threshold=0.05)
    
    # Apply preprocessing to text column
    df['cleaned_text'] = df['caption'].apply(
        lambda x: preprocessor.preprocess(x, apply_stemming, apply_lemmatization)
    )
    
    # Remove empty rows after preprocessing
    df = df[df['cleaned_text'].str.len() > 0]
    
    # Remove multilingual posts with low English confidence
    if preprocessor.remove_multilingual_low:
        df['lang_ratio'] = df['caption'].apply(
            lambda x: preprocessor.detect_language_simple(x)[1] if isinstance(x, str) else 0
        )
        df = df[df['lang_ratio'] >= preprocessor.min_threshold]
        df = df.drop(columns=['lang_ratio'])
    
    print(f"Original dataset size: {len(df)}")
    print(f"After preprocessing: {len(df)} samples")
    
    return df, preprocessor

# Example usage
if __name__ == "__main__":
    # Load your dataset
    df, preprocessor = load_and_preprocess_dataset(
        'merged_dataset/unified_master_dataset.csv',
        apply_stemming=False,
        apply_lemmatization=True
    )
    
    # Save preprocessed dataset
    df.to_csv('merged_dataset/preprocessed_dataset.csv', index=False)
    print("Preprocessed dataset saved!")