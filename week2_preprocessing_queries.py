"""
=============================================================================
  WEEK 2 – Preprocessing Student Queries
  ----------------------------------------
  Implement text preprocessing for student questions:
    1. Lowercasing
    2. Punctuation removal
    3. Tokenization
    4. Stopword removal
    5. Basic spelling normalization
=============================================================================
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# Stopword List (common English words that don't carry meaning for FAQ search)
# ─────────────────────────────────────────────────────────────────────────────
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "i", "me", "my",
    "we", "our", "you", "your", "it", "its", "this", "that", "these",
    "those", "what", "how", "when", "where", "who", "which", "tell",
    "please", "want", "know", "about", "of", "in", "on", "at",
    "to", "for", "with", "by"
}

# ─────────────────────────────────────────────────────────────────────────────
# Spelling Correction Dictionary (common student misspellings)
# ─────────────────────────────────────────────────────────────────────────────
SPELLING_CORRECTIONS = {
    "fess": "fees", "fie": "fees", "coarse": "course", "corse": "course",
    "timin": "timing", "timming": "timing", "addmission": "admission",
    "admision": "admission", "scolarship": "scholarship",
    "scholaship": "scholarship", "hosstel": "hostel", "hostl": "hostel",
    "placment": "placement", "plcement": "placement", "affilated": "affiliated",
    "contcat": "contact", "princpal": "principal", "documnt": "document",
    "semster": "semester", "semestre": "semester", "libary": "library",
    "libraray": "library", "examm": "exam", "timetabel": "timetable"
}


# ─────────────────────────────────────────────────────────────────────────────
# Preprocessing Pipeline Class
# ─────────────────────────────────────────────────────────────────────────────
class Preprocessor:
    """
    5-step NLP preprocessing pipeline for student queries.
    Each step transforms the text progressively and records debug info.
    """

    def process(self, text: str) -> dict:
        """
        Runs the full 5-step pipeline.
        Returns cleaned tokens and a step-by-step debug trace.
        """
        debug = {"original": text}

        # Step 1: Lowercasing
        lowercased = text.lower()
        debug["step1_lowercased"] = lowercased

        # Step 2: Punctuation Removal
        no_punct = re.sub(r'[.,!?;:\'\"()\[\]{}/\\@#$%^&*~`]', '', lowercased)
        debug["step2_no_punct"] = no_punct

        # Step 3: Tokenization (whitespace splitting)
        tokens = no_punct.split()
        debug["step3_tokens"] = list(tokens)

        # Step 4: Stopword Removal
        no_stopwords = [t for t in tokens if t not in STOPWORDS]
        debug["step4_no_stopwords"] = list(no_stopwords)

        # Step 5: Spelling Normalization
        normalized = [SPELLING_CORRECTIONS.get(t, t) for t in no_stopwords]
        debug["step5_normalized"] = list(normalized)

        return {
            "tokens": normalized,
            "debug": debug,
            "original_lowercased": lowercased
        }


# ─────────────────────────────────────────────────────────────────────────────
# FAQ Data (reused from Week 1)
# ─────────────────────────────────────────────────────────────────────────────
FAQ_LIST = [
    {"id": 1, "keywords": ["timing", "timings", "time", "hours", "open", "close"],
     "question": "What are the institute timings?",
     "answer": "We are open Monday to Saturday, 8:00 AM to 6:00 PM."},
    {"id": 2, "keywords": ["course", "courses", "program", "degree", "offer", "branch"],
     "question": "What courses does the institute offer?",
     "answer": "We offer BCA, BBA, B.Sc IT, MBA, and MCA programs."},
    {"id": 3, "keywords": ["fee", "fees", "cost", "tuition", "payment", "charge"],
     "question": "What are the admission fees?",
     "answer": "UG courses: ₹45,000/year. PG courses: ₹60,000/year."},
    {"id": 4, "keywords": ["apply", "admission", "enroll", "join", "register"],
     "question": "How do I apply for admission?",
     "answer": "Visit campus or apply online at www.institute.edu.in"},
    {"id": 5, "keywords": ["last date", "deadline"],
     "question": "What is the last date for admission?",
     "answer": "The last date for admission is 30th June 2025."},
    {"id": 6, "keywords": ["location", "address", "where", "located", "campus"],
     "question": "Where is the institute located?",
     "answer": "123, College Road, Nagpur, Maharashtra - 440001."},
    {"id": 7, "keywords": ["contact", "phone", "number", "call"],
     "question": "What is the contact number?",
     "answer": "Call us at +91-712-2345678 (Mon–Sat, 9AM–5PM)."},
    {"id": 8, "keywords": ["email", "mail"],
     "question": "What is the email address?",
     "answer": "Email us at admissions@institute.edu.in"},
    {"id": 9, "keywords": ["hostel", "accommodation", "stay", "dorm", "room"],
     "question": "Is hostel facility available?",
     "answer": "Yes! Separate hostels for boys and girls with 24/7 security."},
    {"id": 10, "keywords": ["scholarship", "financial", "aid", "merit"],
     "question": "Do you offer scholarships?",
     "answer": "Yes, merit-based and need-based scholarships are available."},
    {"id": 11, "keywords": ["ratio", "student teacher"],
     "question": "What is the student teacher ratio?",
     "answer": "Our student-teacher ratio is 20:1."},
    {"id": 12, "keywords": ["placement", "job", "recruit", "career", "company"],
     "question": "What is the placement record?",
     "answer": "85%+ placement record. Top recruiters include TCS, Infosys, Wipro."},
    {"id": 13, "keywords": ["affiliated", "university", "naac", "accredited"],
     "question": "Is the institute affiliated to any university?",
     "answer": "Yes, affiliated to RTM Nagpur University. NAAC A+ accredited."},
    {"id": 14, "keywords": ["document", "documents", "marksheet", "certificate", "proof"],
     "question": "What documents are needed for admission?",
     "answer": "10th & 12th marksheets, ID proof, passport-size photo, TC."},
    {"id": 15, "keywords": ["principal", "head", "director"],
     "question": "How do I contact the principal?",
     "answer": "Email: principal@institute.edu.in or visit during 10AM–12PM."}
]


def find_answer(tokens: list) -> str:
    """Matches preprocessed tokens against FAQ keywords."""
    best_match = None
    best_score = 0
    for faq in FAQ_LIST:
        score = sum(1 for t in tokens if t in faq["keywords"])
        if score > best_score:
            best_score = score
            best_match = faq

    if best_match and best_score >= 1:
        return f"[FAQ #{best_match['id']}] {best_match['answer']}"
    return ("I'm sorry, I couldn't understand your question. "
            "Try asking about timings, fees, courses, hostel, etc.")


# ─────────────────────────────────────────────────────────────────────────────
# CLI with Preprocessing Debug Display
# ─────────────────────────────────────────────────────────────────────────────
def main():
    preprocessor = Preprocessor()

    print("=" * 60)
    print("  🧹 EduBot – Week 2: Preprocessing Student Queries")
    print("  5-step NLP pipeline: lowercase → punct → tokenize")
    print("                       → stopwords → spelling fix")
    print("=" * 60)
    print("  Type a question (with typos/punctuation!) or 'bye' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["bye", "exit", "quit"]:
            print("EduBot: Goodbye! 👋\n")
            break

        # Run preprocessing
        result = preprocessor.process(user_input)
        debug = result["debug"]

        # Show each preprocessing step
        print("\n  ┌─── Preprocessing Pipeline ──────────────────────────┐")
        print(f"  │ Original:      \"{debug['original']}\"")
        print(f"  │ Step 1 Lower:  \"{debug['step1_lowercased']}\"")
        print(f"  │ Step 2 Punct:  \"{debug['step2_no_punct']}\"")
        print(f"  │ Step 3 Tokens: {debug['step3_tokens']}")
        print(f"  │ Step 4 Stop:   {debug['step4_no_stopwords']}")
        print(f"  │ Step 5 Spell:  {debug['step5_normalized']}")
        print("  └─────────────────────────────────────────────────────┘\n")

        # Use preprocessed tokens for FAQ matching
        answer = find_answer(result["tokens"])
        print(f"EduBot: {answer}\n")


if __name__ == "__main__":
    main()
