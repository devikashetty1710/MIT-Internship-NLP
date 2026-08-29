from mastodon import Mastodon
import pandas as pd
from bs4 import BeautifulSoup
from langdetect import detect
from dotenv import load_dotenv
import os
import re
import time


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

INSTANCE = os.getenv("INSTANCE")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

OUTPUT_FILE = "mastodon_data.csv"

# Target = UNIQUE POSTS
TARGET_UNIQUE_POSTS = 500

# Number of API pages to examine for each hashtag
MAX_PAGES_PER_HASHTAG = 15

# Number of posts per API request
POSTS_PER_PAGE = 40

# Delay between Mastodon API requests
REQUEST_DELAY = 1


# ============================================================
# MASTODON CONNECTION
# ============================================================

if not INSTANCE:
    raise ValueError(
        "INSTANCE is missing from your .env file."
    )

if not ACCESS_TOKEN:
    raise ValueError(
        "ACCESS_TOKEN is missing from your .env file."
    )

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE
)


# ============================================================
# TARGETED HASHTAGS
#
# We intentionally prioritize hashtags that combine:
# mental health + a possible reason.
#
# Broad hashtags are kept, but placed later.
# ============================================================

SEARCH_HASHTAGS = [

    # ========================================================
    # EDUCATION + MENTAL HEALTH
    # ========================================================

    "examstress",
    "examstress",
    "studentmentalhealth",
    "studentanxiety",
    "studentstress",
    "academicstress",
    "academicpressure",
    "schoolstress",
    "schoolanxiety",
    "collegeanxiety",
    "collegepressure",
    "college stress",
    "exam anxiety",
    "academic anxiety",
    "educationstress",

    # ========================================================
    # SOCIAL STATUS + MENTAL HEALTH
    # ========================================================

    "jobstress",
    "workstress",
    "careerstress",
    "jobloss",
    "unemploymentstress",
    "financialstress",
    "workplaceanxiety",
    "workplace stress",
    "financialanxiety",
    "jobanxiety",
    "career anxiety",
    "employmentstress",

    # ========================================================
    # APPEARANCE + MENTAL HEALTH
    # ========================================================

    "bodyimage",
    "bodydysmorphia",
    "bodyshaming",
    "fatshaming",
    "lookism",
    "appearanceanxiety",
    "selfesteem",
    "lowselfesteem",
    "appearance",
    "appearancebullying",

    # ========================================================
    # HIGH-SEVERITY MENTAL HEALTH
    # ========================================================

    "suicide",
    "suicidal",
    "selfharm",
    "selfinjury",
    "suicideprevention",

    # ========================================================
    # GENERAL MENTAL HEALTH
    #
    # These are intentionally placed later because they
    # produce more posts without an identifiable reason.
    # ========================================================

    "depression",
    "anxiety",
    "mentalhealth",
    "mentalhealthawareness",
    "mentalwellness",
    "burnout",
    "loneliness",
    "trauma",
    "panicattack",
    "stress"
]


# ============================================================
# MENTAL HEALTH TERMS
# ============================================================

MENTAL_HEALTH_TERMS = [

    # Mental health
    "mental health",
    "mental illness",
    "mental wellbeing",
    "mental wellness",
    "psychological distress",

    # Depression
    "depression",
    "depressed",
    "depressive",

    # Anxiety
    "anxiety",
    "anxious",

    # Panic
    "panic",
    "panic attack",
    "panic attacks",

    # Stress
    "stress",
    "stressed",
    "overwhelmed",
    "overwhelming",

    # Burnout
    "burnout",
    "burned out",
    "burnt out",

    # Trauma
    "trauma",
    "traumatic",
    "ptsd",

    # Loneliness
    "lonely",
    "loneliness",
    "isolated",
    "isolation",

    # Emotional distress
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

    # Treatment
    "therapy",
    "therapist",
    "counselling",
    "counseling",
    "psychiatrist",
    "psychologist",

    # Conditions
    "ocd",
    "bipolar",
    "schizophrenia",

    # Suicide / self-harm
    "suicide",
    "suicidal",
    "self harm",
    "self-harm",
    "selfharm",
    "self injury",
    "self-injury",

    # Grief
    "grief",
    "grieving"
]


# ============================================================
# STRONG EDUCATION TERMS
#
# These indicate that the mental-health issue is actually
# connected to education.
# ============================================================

EDUCATION_STRONG = [

    "exam stress",
    "exam anxiety",
    "exam pressure",
    "exams are stressing",
    "stressed about exams",
    "anxious about exams",
    "anxiety about exams",

    "academic stress",
    "academic pressure",
    "academic anxiety",

    "school stress",
    "school pressure",
    "school anxiety",

    "college stress",
    "college pressure",
    "college anxiety",

    "university stress",
    "university pressure",
    "university anxiety",

    "study stress",
    "study pressure",
    "study anxiety",

    "assignment stress",
    "assignment pressure",

    "grade stress",
    "grades stress",
    "grade anxiety",
    "grades anxiety",

    "exam results",
    "academic failure",

    "failed my exam",
    "failed an exam",
    "failing exams",

    "student mental health",
    "student anxiety",
    "student stress",

    "school mental health",
    "college mental health",

    "academic burnout",
    "study burnout"
]


# ============================================================
# WEAKER EDUCATION TERMS
#
# These alone are NOT enough to classify something as
# Education.
# ============================================================

EDUCATION_WEAK = [

    "exam",
    "exams",
    "student",
    "students",
    "school",
    "college",
    "university",
    "campus",
    "class",
    "classes",
    "teacher",
    "professor",
    "assignment",
    "homework",
    "semester",
    "grade",
    "grades",
    "academic",
    "education",
    "study",
    "studying"
]


# ============================================================
# STRONG SOCIAL STATUS TERMS
# ============================================================

SOCIAL_STRONG = [

    "job loss",
    "jobloss",
    "lost my job",
    "losing my job",
    "unemployment",
    "unemployed",

    "unemployment stress",
    "job stress",
    "jobstress",
    "work stress",
    "workstress",

    "career stress",
    "career pressure",
    "career anxiety",

    "workplace stress",
    "workplace anxiety",

    "financial stress",
    "financial anxiety",
    "financial problems",

    "money problems",
    "money stress",

    "rent stress",
    "housing stress",

    "layoff",
    "laid off",

    "fired from my job",
    "lost my job",

    "work pressure",
    "workplace pressure",

    "employment stress",
    "job anxiety"
]


# ============================================================
# WEAKER SOCIAL STATUS TERMS
# ============================================================

SOCIAL_WEAK = [

    "job",
    "jobs",
    "work",
    "workplace",
    "career",
    "office",
    "boss",
    "salary",
    "income",
    "money",
    "financial",
    "rent",
    "bill",
    "bills",
    "loan",
    "poverty",
    "homeless",
    "employment",
    "unemployed",
    "layoff",
    "promotion",
    "colleague"
]


# ============================================================
# STRONG APPEARANCE TERMS
# ============================================================

APPEARANCE_STRONG = [

    "body image",
    "bodyimage",
    "body dysmorphia",
    "bodydysmorphia",

    "appearance anxiety",
    "appearanceanxiety",

    "appearance issues",
    "appearance problems",

    "body shaming",
    "bodyshaming",

    "fat shaming",
    "fatshaming",

    "lookism",

    "low self esteem",
    "lowselfesteem",

    "self esteem",
    "self-esteem",

    "bullied for my appearance",
    "bullied because of my appearance",

    "bullied for my weight",
    "bullied because of my weight",

    "hate my body",
    "hate my appearance",

    "insecure about my body",
    "insecure about my appearance",

    "insecure about my weight",

    "ugly and depressed",
    "ugly and anxious",

    "appearance bullying",

    "weight anxiety",
    "weight insecurity"
]


# ============================================================
# WEAKER APPEARANCE TERMS
# ============================================================

APPEARANCE_WEAK = [

    "ugly",
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
    "acne",
    "hair",
    "skin",
    "height",
    "attractive",
    "unattractive"
]


# ============================================================
# HIGH SEVERITY TERMS
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

    "wish i was dead",
    "wish i were dead",

    "don't want to live",
    "do not want to live",

    "no reason to live",

    "can't go on",
    "cannot go on",

    "self harm",
    "self-harm",
    "selfharm",

    "self injury",
    "self-injury",
    "selfinjury",

    "hurt myself",
    "hurting myself",

    "cut myself",
    "cutting myself"
]


# ============================================================
# MEDIUM SEVERITY TERMS
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
    "overwhelming",

    "mental breakdown",

    "emotional distress"
]


# ============================================================
# LOW SEVERITY TERMS
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

    "feeling low"
]


# ============================================================
# NEWS / ARTICLE TERMS
# ============================================================

NEWS_TERMS = [

    "breaking news",
    "latest news",
    "news article",

    "researchers found",
    "researchers have found",
    "research shows",
    "research has shown",

    "study finds",
    "study found",
    "new study",

    "according to a study",
    "according to researchers",
    "according to reports",

    "psychologists examine",
    "psychologists found",
    "psychologists say",

    "scientists found",
    "scientists say",

    "university researchers",
    "research team",

    "press release",

    "read more",
    "source:",

    "original title",

    "published",

    "journal",

    "article:",
    "news:",

    "report:",
    "reports:"
]


# ============================================================
# PROMOTIONAL TERMS
# ============================================================

PROMOTIONAL_TERMS = [

    "buy now",
    "shop now",
    "limited offer",
    "special offer",
    "discount",

    "sign up",
    "signup",
    "register now",

    "enroll",
    "enrol",

    "my course",
    "our course",

    "online course",
    "course available",

    "join my course",

    "book a session",
    "book your session",

    "book now",

    "coaching",
    "coach with me",

    "workshop",
    "webinar",

    "consultation",

    "learn more",

    "click here",

    "visit my website",

    "visit our website",

    "available here",

    "subscribe",

    "follow us",

    "dm me for",

    "dm me if",

    "link in bio",

    "get your copy",

    "download now"
]


# ============================================================
# PERSONAL EXPERIENCE TERMS
#
# These help distinguish personal experiences from articles.
# ============================================================

PERSONAL_TERMS = [

    "i feel",
    "i'm feeling",
    "i am feeling",

    "i have",
    "i've",

    "i am",
    "i'm",

    "my anxiety",
    "my depression",
    "my stress",
    "my mental health",

    "my panic",
    "my trauma",
    "my burnout",

    "i struggle",
    "i'm struggling",
    "i am struggling",

    "i suffer",
    "i'm suffering",

    "i can't cope",
    "i cannot cope",

    "i can't handle",
    "i cannot handle",

    "i feel overwhelmed",
    "i feel lonely",

    "i've been crying",
    "i have been crying",

    "i feel hopeless",
    "i feel worthless",

    "i want to die",
    "i don't want to live",

    "i need help",

    "i started therapy",
    "i'm in therapy",
    "i am in therapy"
]


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = BeautifulSoup(
        text or "",
        "html.parser"
    ).get_text(" ")

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Remove @mentions
    text = re.sub(
        r"@\w+",
        " ",
        text
    )

    # Keep hashtag words
    #
    # #depression -> depression
    # #examstress -> examstress

    text = re.sub(
        r"#(\w+)",
        r"\1",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# NORMALIZE FOR MATCHING
# ============================================================

def normalize_for_matching(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# LANGUAGE FILTER
# ============================================================

def is_english_or_hindi(text):

    if not text:
        return False

    words = text.split()

    if len(words) < 4:
        return False

    try:

        language = detect(text)

        return language in [
            "en",
            "hi"
        ]

    except:

        return False


# ============================================================
# EXACT TERM MATCH
# ============================================================

def contains_term(text, terms):

    text = normalize_for_matching(
        text
    )

    for term in terms:

        pattern = (
            r"\b"
            + re.escape(
                term.lower()
            )
            + r"\b"
        )

        if re.search(
            pattern,
            text
        ):

            return True

    return False


# ============================================================
# COUNT TERMS
# ============================================================

def count_terms(text, terms):

    text = normalize_for_matching(
        text
    )

    score = 0

    for term in terms:

        pattern = (
            r"\b"
            + re.escape(
                term.lower()
            )
            + r"\b"
        )

        score += len(
            re.findall(
                pattern,
                text
            )
        )

    return score


# ============================================================
# MENTAL HEALTH CHECK
# ============================================================

def is_mental_health_related(text):

    return contains_term(
        text,
        MENTAL_HEALTH_TERMS
    )


# ============================================================
# NEWS CHECK
# ============================================================

def is_news_or_article(text):

    text = normalize_for_matching(
        text
    )

    for term in NEWS_TERMS:

        if term.lower() in text:

            return True

    return False


# ============================================================
# PROMOTIONAL CHECK
# ============================================================

def is_promotional(text):

    text = normalize_for_matching(
        text
    )

    for term in PROMOTIONAL_TERMS:

        if term.lower() in text:

            return True

    return False


# ============================================================
# CATEGORY SCORES
#
# Strong terms get more weight.
# Weak terms alone are not enough.
# ============================================================

def category_scores(text):

    education_strong = count_terms(
        text,
        EDUCATION_STRONG
    )

    education_weak = count_terms(
        text,
        EDUCATION_WEAK
    )

    social_strong = count_terms(
        text,
        SOCIAL_STRONG
    )

    social_weak = count_terms(
        text,
        SOCIAL_WEAK
    )

    appearance_strong = count_terms(
        text,
        APPEARANCE_STRONG
    )

    appearance_weak = count_terms(
        text,
        APPEARANCE_WEAK
    )


    return {

        "Education":
            (education_strong * 3)
            + education_weak,

        "Social Status":
            (social_strong * 3)
            + social_weak,

        "Appearance":
            (appearance_strong * 3)
            + appearance_weak
    }


# ============================================================
# CATEGORY
#
# IMPORTANT:
# A weak word such as "student" alone is NOT enough.
# We require either:
#
#   strong contextual evidence
# OR
#   at least two weak indicators.
# ============================================================

def categorize_reason(text):

    scores = category_scores(
        text
    )

    strong_scores = {

        "Education":
            count_terms(
                text,
                EDUCATION_STRONG
            ),

        "Social Status":
            count_terms(
                text,
                SOCIAL_STRONG
            ),

        "Appearance":
            count_terms(
                text,
                APPEARANCE_STRONG
            )
    }


    # --------------------------------------------------------
    # First preference:
    # strong contextual evidence
    # --------------------------------------------------------

    strongest = max(
        strong_scores.values()
    )

    if strongest > 0:

        winners = [

            category
            for category, score
            in strong_scores.items()
            if score == strongest
        ]

        if len(winners) == 1:

            return winners[0]


        # If multiple strong categories occur,
        # compare complete scores.

        complete_max = max(
            scores.values()
        )

        complete_winners = [

            category
            for category, score
            in scores.items()
            if score == complete_max
        ]

        if len(complete_winners) == 1:

            return complete_winners[0]

        return None


    # --------------------------------------------------------
    # No strong evidence.
    #
    # Count weak indicators.
    # --------------------------------------------------------

    weak_counts = {

        "Education":
            count_terms(
                text,
                EDUCATION_WEAK
            ),

        "Social Status":
            count_terms(
                text,
                SOCIAL_WEAK
            ),

        "Appearance":
            count_terms(
                text,
                APPEARANCE_WEAK
            )
    }


    maximum = max(
        weak_counts.values()
    )

    # A single weak word is not sufficient.
    if maximum < 2:

        return None


    winners = [

        category
        for category, count
        in weak_counts.items()
        if count == maximum
    ]


    if len(winners) == 1:

        return winners[0]


    return None


# ============================================================
# SEVERITY
# ============================================================

def determine_severity(text):

    # High has absolute priority.
    if contains_term(
        text,
        HIGH_SEVERITY_TERMS
    ):

        return "High"


    # Medium
    if contains_term(
        text,
        MEDIUM_SEVERITY_TERMS
    ):

        return "Medium"


    # Low
    if contains_term(
        text,
        LOW_SEVERITY_TERMS
    ):

        return "Low"


    # If the post is mental-health-related but doesn't
    # contain a severity keyword, use Low rather than
    # inventing a higher severity.
    return "Low"


# ============================================================
# GET POSTS USING PAGINATION
# ============================================================

def get_posts():

    unique_posts = {}

    print()
    print("=" * 70)
    print("COLLECTING MASTODON POSTS")
    print("=" * 70)


    for tag_number, tag in enumerate(
        SEARCH_HASHTAGS,
        start=1
    ):

        print()
        print(
            f"[{tag_number}/{len(SEARCH_HASHTAGS)}] "
            f"Fetching #{tag}"
        )

        max_id = None


        for page in range(
            1,
            MAX_PAGES_PER_HASHTAG + 1
        ):

            try:

                if max_id:

                    results = mastodon.timeline_hashtag(
                        tag,
                        limit=POSTS_PER_PAGE,
                        max_id=max_id
                    )

                else:

                    results = mastodon.timeline_hashtag(
                        tag,
                        limit=POSTS_PER_PAGE
                    )


            except Exception as e:

                print(
                    f"Error fetching #{tag}: {e}"
                )

                break


            if not results:

                print(
                    "No more posts available."
                )

                break


            print(
                f"  Page {page}: "
                f"{len(results)} posts"
            )


            for post in results:

                post_id = post.get(
                    "id"
                )

                if post_id:

                    unique_posts[
                        post_id
                    ] = post


            print(
                f"  Total unique candidates: "
                f"{len(unique_posts)}"
            )


            # ------------------------------------------------
            # Pagination
            # ------------------------------------------------

            new_max_id = results[-1].get(
                "id"
            )

            if not new_max_id:

                break


            if new_max_id == max_id:

                break


            max_id = new_max_id


            time.sleep(
                REQUEST_DELAY
            )


        # ----------------------------------------------------
        # Don't stop at 500 candidates.
        #
        # We need enough candidates to obtain 500 VALID posts.
        # Continue searching until all hashtags/pages have
        # been explored.
        # ----------------------------------------------------


    print()
    print(
        "Total unique candidate posts:",
        len(unique_posts)
    )

    return list(
        unique_posts.values()
    )


# ============================================================
# GET COMMENTS
# ============================================================

def get_comments(post_id):

    comments = []

    try:

        context = mastodon.status_context(
            post_id
        )

        descendants = context.get(
            "descendants",
            []
        )


        for reply in descendants:

            text = clean_text(
                reply.get(
                    "content",
                    ""
                )
            )


            if not text:

                continue


            if not is_english_or_hindi(
                text
            ):

                continue


            # Remove obvious article/promotional comments
            if is_news_or_article(
                text
            ):

                continue


            if is_promotional(
                text
            ):

                continue


            comments.append(
                text
            )


    except Exception as e:

        print(
            f"  Comment error: {e}"
        )


    # Remove duplicate comments
    return list(
        dict.fromkeys(
            comments
        )
    )


# ============================================================
# PROCESS POSTS
# ============================================================

def scrape():

    posts = get_posts()

    print()
    print("=" * 70)
    print("PROCESSING CANDIDATE POSTS")
    print("=" * 70)


    data = []


    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    rejected_empty = 0
    rejected_language = 0
    rejected_news = 0
    rejected_promotional = 0
    rejected_not_mental = 0
    rejected_category = 0


    category_counts = {

        "Education": 0,
        "Social Status": 0,
        "Appearance": 0
    }


    severity_counts = {

        "High": 0,
        "Medium": 0,
        "Low": 0
    }


    # --------------------------------------------------------
    # Process each candidate
    # --------------------------------------------------------

    for number, post in enumerate(
        posts,
        start=1
    ):

        print()
        print(
            f"[{number}/{len(posts)}]"
        )


        post_id = post.get(
            "id"
        )

        print(
            "Post ID:",
            post_id
        )


        # ====================================================
        # CAPTION
        # ====================================================

        caption = clean_text(
            post.get(
                "content",
                ""
            )
        )


        if not caption:

            rejected_empty += 1

            print(
                "Rejected: empty"
            )

            continue


        # ====================================================
        # LANGUAGE
        # ====================================================

        if not is_english_or_hindi(
            caption
        ):

            rejected_language += 1

            print(
                "Rejected: language"
            )

            continue


        # ====================================================
        # NEWS
        # ====================================================

        if is_news_or_article(
            caption
        ):

            rejected_news += 1

            print(
                "Rejected: news/article"
            )

            continue


        # ====================================================
        # PROMOTIONAL
        # ====================================================

        if is_promotional(
            caption
        ):

            rejected_promotional += 1

            print(
                "Rejected: promotional"
            )

            continue


        # ====================================================
        # MENTAL HEALTH CHECK
        #
        # IMPORTANT:
        # We check the caption first.
        # This prevents an unrelated comment from turning
        # an unrelated post into a mental-health post.
        # ====================================================

        if not is_mental_health_related(
            caption
        ):

            rejected_not_mental += 1

            print(
                "Rejected: not mental-health-related"
            )

            continue


        # ====================================================
        # CATEGORY
        #
        # Category comes primarily from the caption.
        # Comments are NOT used to invent the reason.
        # ====================================================

        category = categorize_reason(
            caption
        )


        if category is None:

            rejected_category += 1

            print(
                "Rejected: no identifiable category"
            )

            continue


        # ====================================================
        # SEVERITY
        #
        # Primary severity is based on caption.
        # ====================================================

        severity = determine_severity(
            caption
        )


        # ====================================================
        # COMMENTS
        #
        # Comments are collected after the post passes
        # the primary validation.
        # ====================================================

        comments = get_comments(
            post_id
        )


        # ====================================================
        # ACCEPT
        # ====================================================

        data.append({

            "post_id":
                post_id,

            "caption":
                caption,

            "comments":
                comments,

            "timestamp":
                post.get(
                    "created_at"
                ),

            "mental_health":
                "Yes",

            "category":
                category,

            "severity":
                severity
        })


        category_counts[
            category
        ] += 1


        severity_counts[
            severity
        ] += 1


        print(
            "✓ ACCEPTED"
        )

        print(
            "Category:",
            category
        )

        print(
            "Severity:",
            severity
        )

        print(
            "Comments:",
            len(comments)
        )


        # ====================================================
        # STOP ONLY AFTER 500 VALID UNIQUE POSTS
        # ====================================================

        if len(data) >= TARGET_UNIQUE_POSTS:

            print()
            print(
                "=" * 70
            )

            print(
                "500+ VALID UNIQUE POSTS REACHED!"
            )

            print(
                "=" * 70
            )

            break


    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("SCRAPING SUMMARY")
    print("=" * 70)


    print(
        "Candidate posts:",
        len(posts)
    )

    print(
        "Accepted unique posts:",
        len(data)
    )

    print(
        "Rejected - empty:",
        rejected_empty
    )

    print(
        "Rejected - language:",
        rejected_language
    )

    print(
        "Rejected - news/article:",
        rejected_news
    )

    print(
        "Rejected - promotional:",
        rejected_promotional
    )

    print(
        "Rejected - not mental-health-related:",
        rejected_not_mental
    )

    print(
        "Rejected - no category:",
        rejected_category
    )


    print()
    print(
        "CATEGORY DISTRIBUTION"
    )

    print(
        "-" * 40
    )

    print(
        category_counts
    )


    print()
    print(
        "SEVERITY DISTRIBUTION"
    )

    print(
        "-" * 40
    )

    print(
        severity_counts
    )


    return data


# ============================================================
# SAVE DATASET
# ============================================================

def save(data):

    rows = []


    for item in data:

        comments = item[
            "comments"
        ]


        # ----------------------------------------------------
        # No comments
        # ----------------------------------------------------

        if not comments:

            rows.append({

                "post_id":
                    item["post_id"],

                "caption":
                    item["caption"],

                "comment":
                    "",

                "timestamp":
                    item["timestamp"],

                "mental_health":
                    item["mental_health"],

                "category":
                    item["category"],

                "severity":
                    item["severity"]
            })


        # ----------------------------------------------------
        # Has comments
        # ----------------------------------------------------

        else:

            for comment in comments:

                rows.append({

                    "post_id":
                        item["post_id"],

                    "caption":
                        item["caption"],

                    "comment":
                        comment,

                    "timestamp":
                        item["timestamp"],

                    "mental_health":
                        item["mental_health"],

                    "category":
                        item["category"],

                    "severity":
                        item["severity"]
                })


    df = pd.DataFrame(
        rows,
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


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    df = df.drop_duplicates(
        subset=[
            "post_id",
            "comment"
        ]
    )


    # ========================================================
    # FINAL SAFETY FILTER
    #
    # There must NEVER be "Other".
    # ========================================================

    df = df[
        df["category"].isin([
            "Education",
            "Social Status",
            "Appearance"
        ])
    ]


    df["mental_health"] = "Yes"


    df = df[
        df["severity"].isin([
            "High",
            "Medium",
            "Low"
        ])
    ]


    # ========================================================
    # SAVE
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 70)
    print("DATASET SAVED SUCCESSFULLY")
    print("=" * 70)


    print(
        "File:",
        OUTPUT_FILE
    )

    print(
        "Total CSV rows:",
        len(df)
    )

    print(
        "Unique posts:",
        df["post_id"].nunique()
    )


    print()
    print(
        "CATEGORY DISTRIBUTION"
    )

    print(
        df["category"].value_counts()
    )


    print()
    print(
        "SEVERITY DISTRIBUTION"
    )

    print(
        df["severity"].value_counts()
    )


    print()
    print(
        "MENTAL HEALTH DISTRIBUTION"
    )

    print(
        df["mental_health"].value_counts()
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    dataset = scrape()


    if dataset:

        save(dataset)

    else:

        print()
        print(
            "No valid mental-health posts were collected."
        )