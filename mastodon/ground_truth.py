import pandas as pd
import re


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "mastodon_data.csv"
OUTPUT_FILE = "mastodon_ground_truth.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("GROUND TRUTH VALIDATION")
print("=" * 70)

try:
    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )
except FileNotFoundError:
    print(f"\nERROR: {INPUT_FILE} not found.")
    print("Make sure mastodon_data.csv is in the same folder.")
    exit()

print("\nInput CSV rows:", len(df))
print("Input unique posts:", df["post_id"].nunique())


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "post_id",
    "caption",
    "comment",
    "timestamp",
    "mental_health",
    "category",
    "severity"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    print("\nERROR: Missing columns:", missing_columns)
    exit()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Remove mentions
    text = re.sub(
        r"@\w+",
        " ",
        text
    )

    # Convert hashtags to words
    # #depression -> depression
    text = re.sub(
        r"#(\w+)",
        r"\1",
        text
    )

    # Replace punctuation
    text = re.sub(
        r"[^a-z0-9\s-]",
        " ",
        text
    )

    # Normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# MENTAL HEALTH TERMS
# ============================================================

MENTAL_HEALTH_TERMS = [

    "depression",
    "depressed",
    "depressive",

    "anxiety",
    "anxious",

    "panic",
    "panic attack",
    "panic attacks",

    "stress",
    "stressed",

    "overwhelmed",

    "burnout",
    "burned out",
    "burnt out",

    "trauma",
    "traumatic",
    "ptsd",

    "lonely",
    "loneliness",

    "isolated",
    "isolation",

    "sad",
    "sadness",

    "hopeless",
    "hopelessness",

    "worthless",

    "crying",

    "feeling low",

    "emotional pain",
    "emotional distress",

    "mental breakdown",

    "mental health",
    "mental illness",
    "mental wellbeing",
    "mental wellness",
    "psychological distress",

    "therapy",
    "therapist",
    "counselling",
    "counseling",
    "psychiatrist",

    "ocd",
    "bipolar",
    "schizophrenia",

    "suicide",
    "suicidal",

    "self harm",
    "self-harm",

    "grief",
    "grieving"
]


# ============================================================
# EDUCATION TERMS
# ============================================================

EDUCATION_TERMS = [

    "exam",
    "exams",
    "exam stress",

    "student",
    "students",

    "school",

    "college",

    "university",
    "campus",

    "class",
    "classes",

    "teacher",
    "teachers",

    "professor",
    "professors",

    "assignment",
    "assignments",

    "homework",

    "semester",

    "grade",
    "grades",

    "result",
    "results",

    "academic",
    "academics",

    "education",

    "study",
    "studying",
    "studies",

    "course",
    "degree",

    "failed",
    "failure",
    "fail"
]


# ============================================================
# SOCIAL STATUS TERMS
# ============================================================

SOCIAL_STATUS_TERMS = [

    "job",
    "jobs",

    "job loss",
    "jobloss",

    "work",
    "workplace",

    "career",

    "office",

    "boss",

    "salary",

    "income",

    "money",

    "financial",
    "finance",

    "rent",

    "bill",
    "bills",

    "loan",

    "poverty",

    "homeless",

    "employment",
    "employed",

    "unemployed",
    "unemployment",

    "layoff",
    "laid off",

    "fired",
    "firing",

    "promotion",

    "colleague",
    "colleagues"
]


# ============================================================
# APPEARANCE TERMS
# ============================================================

APPEARANCE_TERMS = [

    "ugly",

    "look",
    "looks",

    "appearance",

    "body",
    "body image",
    "bodyimage",

    "fat",
    "skinny",

    "weight",

    "face",

    "beauty",
    "beautiful",

    "lookism",

    "self esteem",
    "self-esteem",
    "selfesteem",

    "bully",
    "bullied",
    "bullying",

    "fatshaming",
    "fat shaming",

    "bodyshaming",
    "body shaming",

    "attractive",
    "unattractive",

    "acne",

    "hair",
    "skin",

    "height"
]


# ============================================================
# HIGH SEVERITY
# ============================================================

HIGH_SEVERITY_TERMS = [

    "suicide",
    "suicidal",

    "kill myself",
    "killing myself",

    "end my life",
    "ending my life",

    "take my own life",
    "taking my own life",

    "want to die",
    "wanted to die",

    "don't want to live",
    "do not want to live",

    "no reason to live",

    "can't go on",
    "cannot go on",

    "self harm",
    "self-harm",

    "hurt myself",

    "cut myself",
    "cutting myself"
]


# ============================================================
# MEDIUM SEVERITY
# ============================================================

MEDIUM_SEVERITY_TERMS = [

    "depression",
    "depressed",

    "anxiety",
    "anxious",

    "panic",
    "panic attack",

    "burnout",
    "burned out",
    "burnt out",

    "trauma",
    "ptsd",

    "hopeless",
    "hopelessness",

    "grief",
    "grieving",

    "lonely",
    "loneliness",

    "overwhelmed",

    "mental breakdown",

    "emotional distress"
]


# ============================================================
# LOW SEVERITY
# ============================================================

LOW_SEVERITY_TERMS = [

    "stress",
    "stressed",

    "worried",
    "worry",

    "nervous",

    "tired",

    "sad",
    "sadness",

    "upset",

    "frustrated",
    "frustration",

    "feeling low",

    "exam stress",
    "work stress"
]


# ============================================================
# NEWS SOURCES
# ============================================================

NEWS_SOURCES = [

    "bbc",
    "cnn",
    "reuters",
    "theguardian",
    "guardian",
    "npr",

    "nbc news",
    "abc news",
    "cbs news",

    "associated press",
    "ap news",

    "yahoo news",

    "times of india",
    "hindustan times",
    "indian express",
    "deccan herald",
    "the hindu",

    "new indian express",

    "ndtv",
    "news18",
    "times now",

    "mathrubhumi",

    "wion",

    "al jazeera",

    "sky news",

    "fox news"
]


# ============================================================
# ARTICLE / NEWS LANGUAGE
# ============================================================

ARTICLE_TERMS = [

    "according to",
    "according to reports",

    "researchers found",
    "researchers say",

    "study finds",
    "study shows",

    "new study",

    "research shows",
    "research suggests",

    "psychologists found",
    "psychologists say",

    "experts say",
    "experts warn",

    "officials said",
    "officials say",

    "reported that",
    "reports that",

    "reportedly",

    "the report",

    "the study",

    "a new report",

    "a new study",

    "in a statement",

    "statement said",

    "published",

    "read more",

    "full story",

    "source:",

    "article:",

    "breaking news",

    "breaking",

    "latest news",

    "news report",

    "news article",

    "press release",

    "journalists",

    "reporters"
]


# ============================================================
# PROMOTIONAL TERMS
# ============================================================

PROMOTIONAL_TERMS = [

    "buy now",
    "shop now",

    "sign up",
    "signup",

    "register now",

    "enroll now",

    "book now",

    "limited offer",

    "discount",

    "sale",

    "subscribe",

    "follow us",

    "visit our website",

    "available now",

    "learn more",

    "click here",

    "click the link",

    "link in bio",

    "join our course",

    "our course",

    "online course",

    "course available",

    "webinar",

    "workshop",

    "training",

    "coaching",

    "consultation",

    "consulting",

    "free course",

    "paid course",

    "enrol",

    "enrollment",

    "book a session",

    "book your session"
]


# ============================================================
# PERSONAL EXPERIENCE INDICATORS
# ============================================================

PERSONAL_EXPERIENCE_TERMS = [

    "i feel",
    "i'm feeling",
    "i am feeling",

    "i've been",
    "i have been",

    "i was",
    "i am",
    "i'm",

    "my anxiety",
    "my depression",
    "my stress",
    "my mental health",

    "my experience",

    "i struggle",
    "i struggle with",

    "i suffer",
    "i need help",

    "i can't",
    "i cannot",

    "feeling anxious",
    "feeling depressed",
    "feeling stressed",
    "feeling lonely",

    "i feel worthless",

    "i hate myself"
]


# ============================================================
# TERM MATCHING
# ============================================================

def contains_term(text, terms):

    text = text.lower()

    for term in terms:

        pattern = (
            r"\b"
            + re.escape(term.lower())
            + r"\b"
        )

        if re.search(pattern, text):
            return True

    return False


# ============================================================
# COUNT TERMS
# ============================================================

def count_terms(text, terms):

    text = text.lower()

    count = 0

    for term in terms:

        pattern = (
            r"\b"
            + re.escape(term.lower())
            + r"\b"
        )

        count += len(
            re.findall(pattern, text)
        )

    return count


# ============================================================
# MENTAL HEALTH CHECK
# ============================================================

def is_mental_health_related(text):

    if not text.strip():
        return False

    return contains_term(
        text,
        MENTAL_HEALTH_TERMS
    )


# ============================================================
# NEWS / ARTICLE CHECK
# ============================================================

def is_news_or_article(text):

    text = text.lower()

    # Direct news source
    for source in NEWS_SOURCES:

        if source in text:
            return True

    # Article indicators
    article_matches = 0

    for term in ARTICLE_TERMS:

        if term in text:
            article_matches += 1

    # Multiple article indicators
    if article_matches >= 2:
        return True

    return False


# ============================================================
# PROMOTIONAL CHECK
# ============================================================

def is_promotional(text):

    text = text.lower()

    promotional_matches = 0

    for term in PROMOTIONAL_TERMS:

        if term in text:
            promotional_matches += 1

    # Strong promotional language
    if promotional_matches >= 2:
        return True

    return False


# ============================================================
# PERSONAL EXPERIENCE CHECK
# ============================================================

def has_personal_experience(text):

    text = text.lower()

    for term in PERSONAL_EXPERIENCE_TERMS:

        if term in text:
            return True

    return False


# ============================================================
# CATEGORY SCORING
# ============================================================

def get_category_scores(text):

    return {

        "Education":
            count_terms(
                text,
                EDUCATION_TERMS
            ),

        "Social Status":
            count_terms(
                text,
                SOCIAL_STATUS_TERMS
            ),

        "Appearance":
            count_terms(
                text,
                APPEARANCE_TERMS
            )
    }


# ============================================================
# CATEGORY
# ============================================================

def categorize_reason(text):

    scores = get_category_scores(text)

    maximum = max(
        scores.values()
    )

    # No category evidence
    if maximum == 0:
        return None

    winners = [
        category
        for category, score
        in scores.items()
        if score == maximum
    ]

    # One clear winner
    if len(winners) == 1:
        return winners[0]

    # Tie breaking
    priority = [
        "Education",
        "Social Status",
        "Appearance"
    ]

    for category in priority:

        if category in winners:
            return category

    return None


# ============================================================
# SEVERITY
# ============================================================

def determine_severity(text):

    # High severity first
    if contains_term(
        text,
        HIGH_SEVERITY_TERMS
    ):
        return "High"

    # Medium severity
    if contains_term(
        text,
        MEDIUM_SEVERITY_TERMS
    ):
        return "Medium"

    # Low severity
    if contains_term(
        text,
        LOW_SEVERITY_TERMS
    ):
        return "Low"

    # Mental-health post without
    # explicit severity indicator
    return "Low"


# ============================================================
# PREPARE TEXT
# ============================================================

df["caption_clean"] = (
    df["caption"]
    .fillna("")
    .apply(normalize_text)
)

df["comment_clean"] = (
    df["comment"]
    .fillna("")
    .apply(normalize_text)
)


# ============================================================
# VALIDATION
# ============================================================

valid_rows = []

removed_empty = 0
removed_language = 0
removed_news = 0
removed_promotional = 0
removed_not_mental = 0
removed_no_category = 0


print()
print("=" * 70)
print("VALIDATING RECORDS")
print("=" * 70)


# ============================================================
# PROCESS EACH ROW
# ============================================================

for index, row in df.iterrows():

    caption = row["caption_clean"]
    comment = row["comment_clean"]

    # --------------------------------------------------------
    # Caption must exist
    # --------------------------------------------------------

    if not caption.strip():

        removed_empty += 1
        continue


    # --------------------------------------------------------
    # IMPORTANT:
    # Use caption as the PRIMARY source.
    # Comments are supporting information.
    # --------------------------------------------------------

    primary_text = caption

    supporting_text = (
        caption + " " + comment
    ).strip()


    # --------------------------------------------------------
    # NEWS / ARTICLE
    #
    # Check the caption primarily.
    # --------------------------------------------------------

    if is_news_or_article(primary_text):

        removed_news += 1
        continue


    # --------------------------------------------------------
    # PROMOTIONAL
    # --------------------------------------------------------

    if is_promotional(primary_text):

        removed_promotional += 1
        continue


    # --------------------------------------------------------
    # MENTAL HEALTH
    #
    # Check caption first.
    # --------------------------------------------------------

    if not is_mental_health_related(primary_text):

        # A comment alone should NOT turn
        # an unrelated post into a mental-health post.

        removed_not_mental += 1
        continue


    # --------------------------------------------------------
    # CATEGORY
    #
    # Caption is the primary evidence.
    # --------------------------------------------------------

    category = categorize_reason(
        primary_text
    )

    # If caption does not contain enough
    # category evidence, use the comment
    # only as supporting context.

    if category is None:

        category = categorize_reason(
            supporting_text
        )


    # --------------------------------------------------------
    # NO OTHER CATEGORY
    # --------------------------------------------------------

    if category is None:

        removed_no_category += 1
        continue


    # --------------------------------------------------------
    # SEVERITY
    #
    # Caption first.
    # Comment can support severity.
    # --------------------------------------------------------

    severity = determine_severity(
        primary_text
    )

    # If caption has no severity indicator,
    # check supporting comment.

    if severity == "Low":

        comment_severity = determine_severity(
            comment
        )

        if comment_severity == "High":
            severity = "High"

        elif comment_severity == "Medium":
            severity = "Medium"


    # --------------------------------------------------------
    # ADD VALIDATED ROW
    # --------------------------------------------------------

    valid_rows.append({

        "post_id":
            row["post_id"],

        "caption":
            row["caption"],

        "comment":
            row["comment"],

        "timestamp":
            row["timestamp"],

        "mental_health":
            "Yes",

        "category":
            category,

        "severity":
            severity
    })


# ============================================================
# CREATE DATAFRAME
# ============================================================

ground_truth = pd.DataFrame(

    valid_rows,

    columns=[
        "post_id",
        "caption",
        "comment",
        "timestamp",
        "mental_health",
        "category",
        "severity"
    ]
)


# ============================================================
# REMOVE DUPLICATE POST + COMMENT
# ============================================================

duplicate_rows = 0

if not ground_truth.empty:

    before = len(
        ground_truth
    )

    ground_truth = (
        ground_truth
        .drop_duplicates(
            subset=[
                "post_id",
                "comment"
            ]
        )
    )

    duplicate_rows = (
        before
        - len(ground_truth)
    )


# ============================================================
# FINAL SAFETY CHECK
# ============================================================

if not ground_truth.empty:

    ground_truth = ground_truth[
        ground_truth["category"].isin([
            "Education",
            "Social Status",
            "Appearance"
        ])
    ]

    ground_truth["mental_health"] = "Yes"

    ground_truth = ground_truth[
        ground_truth["severity"].isin([
            "Low",
            "Medium",
            "High"
        ])
    ]


# ============================================================
# SAVE
# ============================================================

ground_truth.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 70)
print("GROUND TRUTH CREATED")
print("=" * 70)

print(
    "\nOriginal CSV rows:",
    len(df)
)

print(
    "Original unique posts:",
    df["post_id"].nunique()
)

print(
    "Final ground-truth rows:",
    len(ground_truth)
)

print(
    "Final unique posts:",
    ground_truth["post_id"].nunique()
    if not ground_truth.empty
    else 0
)

print()
print("REMOVAL SUMMARY")
print("-" * 40)

print(
    "Removed - empty:",
    removed_empty
)

print(
    "Removed - language:",
    removed_language
)

print(
    "Removed - news/article:",
    removed_news
)

print(
    "Removed - promotional:",
    removed_promotional
)

print(
    "Removed - not mental-health-related:",
    removed_not_mental
)

print(
    "Removed - no valid category:",
    removed_no_category
)

print(
    "Removed - duplicate rows:",
    duplicate_rows
)


# ============================================================
# CATEGORY DISTRIBUTION
# ============================================================

print()
print("=" * 70)
print("FINAL CATEGORY DISTRIBUTION")
print("=" * 70)

if not ground_truth.empty:

    print(
        ground_truth["category"]
        .value_counts()
    )

else:

    print("No valid records.")


# ============================================================
# SEVERITY DISTRIBUTION
# ============================================================

print()
print("=" * 70)
print("FINAL SEVERITY DISTRIBUTION")
print("=" * 70)

if not ground_truth.empty:

    print(
        ground_truth["severity"]
        .value_counts()
    )

else:

    print("No valid records.")


# ============================================================
# MENTAL HEALTH DISTRIBUTION
# ============================================================

print()
print("=" * 70)
print("MENTAL HEALTH DISTRIBUTION")
print("=" * 70)

if not ground_truth.empty:

    print(
        ground_truth["mental_health"]
        .value_counts()
    )

else:

    print("No valid records.")


# ============================================================
# FINAL DATASET CHECK
# ============================================================

print()
print("=" * 70)
print("FINAL DATASET CHECK")
print("=" * 70)

if ground_truth.empty:

    print("WARNING: Ground-truth dataset is empty.")

else:

    other_count = (
        ground_truth[
            ground_truth["category"] == "Other"
        ].shape[0]
    )

    non_yes_count = (
        ground_truth[
            ground_truth["mental_health"] != "Yes"
        ].shape[0]
    )

    invalid_category = (
        ground_truth[
            ~ground_truth["category"].isin([
                "Education",
                "Social Status",
                "Appearance"
            ])
        ].shape[0]
    )

    invalid_severity = (
        ground_truth[
            ~ground_truth["severity"].isin([
                "Low",
                "Medium",
                "High"
            ])
        ].shape[0]
    )

    print(
        "Other category:",
        other_count
    )

    print(
        "Non-mental-health rows:",
        non_yes_count
    )

    print(
        "Invalid category rows:",
        invalid_category
    )

    print(
        "Invalid severity rows:",
        invalid_severity
    )

    if (
        other_count == 0
        and
        non_yes_count == 0
        and
        invalid_category == 0
        and
        invalid_severity == 0
    ):

        print()
        print(
            "✓ DATASET PASSED STRUCTURAL VALIDATION"
        )

    else:

        print()
        print(
            "⚠ DATASET NEEDS REVIEW"
        )


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 70)
print(
    f"Saved successfully → {OUTPUT_FILE}"
)
print("=" * 70)