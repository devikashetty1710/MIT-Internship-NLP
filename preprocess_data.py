
import re
import pandas as pd
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Make language detection consistent
DetectorFactory.seed = 0

# Download required NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')


class TextPreprocessor:

    def __init__(self):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        self.stop_words = set(stopwords.words('english'))

        # Preserve important negation words
        self.stop_words -= {'no', 'not', 'nor', 'never'}

    def is_english(self, text):
        """Check whether the original text is English"""

        if not isinstance(text, str) or len(text.strip()) < 5:
            return False

        try:
            return detect(text) == 'en'
        except LangDetectException:
            return False

    def remove_special_patterns(self, text):
        """Remove URLs, HTML tags, mentions and emojis"""

        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'@\w+', '', text)

        # Keep hashtag text
        text = re.sub(r'#(\w+)', r'\1', text)

        # Remove emojis and non-ASCII symbols
        text = text.encode('ascii', 'ignore').decode('ascii')

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def remove_non_alphanumeric(self, text):
        """Keep only English letters, numbers and spaces"""

        return re.sub(r"[^a-zA-Z0-9\s']", ' ', text)

    def tokenize(self, text):
        return word_tokenize(text.lower())

    def remove_stopwords(self, tokens):
        return [
            token for token in tokens
            if token not in self.stop_words
        ]

    def apply_stemming(self, tokens):
        return [
            self.stemmer.stem(token)
            for token in tokens
        ]

    def apply_lemmatization(self, tokens):
        return [
            self.lemmatizer.lemmatize(token)
            for token in tokens
        ]

    def preprocess(self, text, apply_stemming=False,
                   apply_lemmatization=True):

        if not isinstance(text, str):
            return ""

        # Check language before removing non-English characters
        if not self.is_english(text):
            return ""

        text = self.remove_special_patterns(text)
        text = self.remove_non_alphanumeric(text)

        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)

        if apply_stemming:
            tokens = self.apply_stemming(tokens)
        elif apply_lemmatization:
            tokens = self.apply_lemmatization(tokens)

        return ' '.join(tokens)


def load_and_preprocess_dataset(
        filepath,
        apply_stemming=False,
        apply_lemmatization=True):

    df = pd.read_csv(filepath, encoding='utf-8-sig')

    original_size = len(df)

    preprocessor = TextPreprocessor()

    # Keep only English records
    df = df[df['caption'].apply(preprocessor.is_english)].copy()

    english_size = len(df)

    # Clean English captions
    df['cleaned_text'] = df['caption'].apply(
        lambda x: preprocessor.preprocess(
            x,
            apply_stemming,
            apply_lemmatization
        )
    )

    # Remove empty cleaned records
    df = df[df['cleaned_text'].str.strip() != ''].copy()

    print(f"Original dataset size: {original_size}")
    print(f"English records: {english_size}")
    print(f"After preprocessing: {len(df)}")
    print(f"Removed records: {original_size - len(df)}")

    return df, preprocessor


if __name__ == "__main__":

    df, preprocessor = load_and_preprocess_dataset(
        'merged_dataset/unified_master_dataset.csv',
        apply_stemming=False,
        apply_lemmatization=True
    )

    df.to_csv(
        'merged_dataset/preprocessed_dataset.csv',
        index=False,
        encoding='utf-8-sig'
    )

    print("\nPreprocessed dataset saved successfully!")
