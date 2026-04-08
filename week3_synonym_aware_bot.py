"""
=============================================================================
  WEEK 3 – Synonym-Aware FAQ Bot
  --------------------------------
  Extend the FAQ bot so that semantically similar queries (e.g., "fees",
  "tuition", "payment") map to the same answer using a synonym dictionary
  or keyword groups.
=============================================================================
"""

import re

# ─────────────────────  Preprocessing (from Week 2)  ─────────────────────

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "i", "me", "my",
    "we", "our", "you", "your", "it", "its", "this", "that", "these",
    "those", "what", "how", "when", "where", "who", "which", "tell",
    "please", "want", "know", "about", "of", "in", "on", "at",
    "to", "for", "with", "by"
}

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


class Preprocessor:
    def process(self, text: str) -> dict:
        lowercased = text.lower()
        no_punct = re.sub(r'[.,!?;:\'\"()\[\]{}/\\@#$%^&*~`]', '', lowercased)
        tokens = no_punct.split()
        no_stopwords = [t for t in tokens if t not in STOPWORDS]
        normalized = [SPELLING_CORRECTIONS.get(t, t) for t in no_stopwords]
        return {"tokens": normalized, "original_lowercased": lowercased}


# ─────────────────────  FAQ Corpus  ──────────────────────────────────────

FAQ_CORPUS = [
    {"id": 1,  "q": "What are the institute timings?",          "a": "We are open Monday to Saturday, 8:00 AM to 6:00 PM."},
    {"id": 2,  "q": "What courses does the institute offer?",   "a": "We offer BCA, BBA, B.Sc IT, MBA, and MCA programs."},
    {"id": 3,  "q": "What are the admission fees?",             "a": "UG courses: ₹45,000/year. PG courses: ₹60,000/year."},
    {"id": 4,  "q": "How do I apply for admission?",            "a": "Visit campus or apply online at www.institute.edu.in"},
    {"id": 5,  "q": "What is the last date for admission?",     "a": "The last date for admission is 30th June 2025."},
    {"id": 6,  "q": "Where is the institute located?",          "a": "123, College Road, Nagpur, Maharashtra - 440001."},
    {"id": 7,  "q": "What is the contact number?",              "a": "Call us at +91-712-2345678 (Mon–Sat, 9AM–5PM)."},
    {"id": 8,  "q": "What is the email address?",               "a": "Email us at admissions@institute.edu.in"},
    {"id": 9,  "q": "Is hostel facility available?",            "a": "Yes! Separate hostels for boys and girls with 24/7 security."},
    {"id": 10, "q": "Do you offer scholarships?",               "a": "Yes, merit-based and need-based scholarships are available."},
    {"id": 11, "q": "What is the student teacher ratio?",       "a": "Our student-teacher ratio is 20:1."},
    {"id": 12, "q": "What is the placement record?",            "a": "85%+ placement record. Top recruiters include TCS, Infosys, Wipro."},
    {"id": 13, "q": "Is the institute affiliated to any university?", "a": "Yes, affiliated to RTM Nagpur University. NAAC A+ accredited."},
    {"id": 14, "q": "What documents are needed for admission?", "a": "10th & 12th marksheets, ID proof, passport-size photo, TC."},
    {"id": 15, "q": "How do I contact the principal?",          "a": "Email: principal@institute.edu.in or visit during 10AM–12PM."}
]


# ─────────────────────────────────────────────────────────────────────────────
# SYNONYM GROUPS – maps semantically similar words to a canonical topic
# ─────────────────────────────────────────────────────────────────────────────
SYNONYM_GROUPS = {
    "fees":        ["fees", "fee", "cost", "costs", "tuition", "payment",
                    "charge", "charges", "price", "pricing", "amount", "pay",
                    "expense", "expenses"],
    "timing":      ["timing", "timings", "time", "times", "hours", "hour",
                    "schedule", "open", "opening", "close", "closing",
                    "working", "office"],
    "courses":     ["course", "courses", "program", "programs", "degree",
                    "degrees", "branch", "branches", "stream", "streams",
                    "subject", "subjects", "offer", "offered", "available",
                    "study", "studying"],
    "admission":   ["admission", "admissions", "apply", "application", "enroll",
                    "enrollment", "join", "joining", "register", "registration",
                    "form", "forms", "process", "procedure", "eligibility"],
    "contact":     ["contact", "contacts", "phone", "number", "call", "email",
                    "mail", "address", "reach", "helpline", "support", "connect"],
    "location":    ["location", "address", "located", "place", "where", "campus",
                    "situated", "find", "directions", "map", "area", "city"],
    "hostel":      ["hostel", "hostels", "accommodation", "stay", "dormitory",
                    "dorm", "room", "rooms", "boarding", "lodge", "lodging",
                    "pg", "housing", "residence"],
    "scholarship": ["scholarship", "scholarships", "financial", "aid", "stipend",
                    "grant", "grants", "merit", "waiver", "concession",
                    "discount", "free", "sponsored", "fund", "funding"],
    "placement":   ["placement", "placements", "job", "jobs", "career", "careers",
                    "recruit", "recruitment", "company", "companies", "hire",
                    "hiring", "employ", "employment", "package", "salary",
                    "lpa", "ctc"],
    "exam":        ["exam", "exams", "examination", "test", "tests", "assessment",
                    "marks", "grade", "grades", "result", "results", "score",
                    "scores", "paper", "papers", "pattern", "syllabus"],
    "timetable":   ["timetable", "timetables", "class", "classes", "lecture",
                    "lectures", "period", "periods", "routine", "calendar",
                    "session", "sessions"],
    "library":     ["library", "books", "book", "read", "reading", "study",
                    "resources", "digital", "e-library", "journals", "reference"],
    "principal":   ["principal", "director", "head", "hod", "faculty", "teacher",
                    "professor", "staff", "administration", "admin"],
    "documents":   ["document", "documents", "certificate", "certificates",
                    "marksheet", "marksheets", "required", "submit",
                    "submission", "proof", "id", "photo", "passport"],
    "affiliation": ["affiliated", "affiliation", "university", "board",
                    "recognized", "approved", "accredited", "naac", "ugc", "aicte"]
}

# Map each topic to the FAQ id that answers it
TOPIC_TO_FAQ = {
    "fees": 3, "timing": 1, "courses": 2, "admission": 4,
    "contact": 7, "location": 6, "hostel": 9, "scholarship": 10,
    "placement": 12, "principal": 15, "documents": 14,
    "affiliation": 13, "exam": 11, "timetable": 11, "library": 11
}


# ─────────────────────────────────────────────────────────────────────────────
# Synonym-Aware Matcher
# ─────────────────────────────────────────────────────────────────────────────
class SynonymMatcher:
    """Matches user tokens to topics using the synonym dictionary."""

    def match_topics(self, tokens: list) -> list:
        """Returns list of matched topic names."""
        matched = set()
        for token in tokens:
            for topic, synonyms in SYNONYM_GROUPS.items():
                if token in synonyms:
                    matched.add(topic)
        return list(matched)

    def get_answer(self, tokens: list) -> dict:
        """
        Uses synonym-aware matching to find the best FAQ answer.
        If multiple topics match, combines their answers.
        """
        topics = self.match_topics(tokens)

        if not topics:
            return {
                "answer": ("I'm sorry, I couldn't match your question. "
                           "Try asking about fees, hostel, placements, etc."),
                "matched_topics": [],
                "confidence": "low"
            }

        # Gather answers from matched topics
        answers = []
        for topic in topics:
            faq_id = TOPIC_TO_FAQ.get(topic)
            if faq_id:
                faq = next((f for f in FAQ_CORPUS if f["id"] == faq_id), None)
                if faq:
                    answers.append(faq["a"])

        if not answers:
            return {
                "answer": "I found a topic match but no FAQ answer. Please contact us.",
                "matched_topics": topics,
                "confidence": "low"
            }

        combined = " | ".join(dict.fromkeys(answers))  # deduplicate preserving order
        confidence = "high" if len(topics) == 1 else "medium"

        return {
            "answer": combined,
            "matched_topics": topics,
            "confidence": confidence
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI Chat Loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    preprocessor = Preprocessor()
    matcher = SynonymMatcher()

    print("=" * 60)
    print("  🔗 EduBot – Week 3: Synonym-Aware FAQ Bot")
    print("  Try synonyms like 'tuition', 'payment', 'dorm', 'job'")
    print("=" * 60)
    print("  Type a question or 'bye' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["bye", "exit", "quit"]:
            print("EduBot: Goodbye! 👋\n")
            break

        # Preprocess
        prep = preprocessor.process(user_input)
        tokens = prep["tokens"]

        # Synonym matching
        result = matcher.get_answer(tokens)

        # Display
        print(f"\n  Tokens:          {tokens}")
        print(f"  Matched Topics:  {result['matched_topics']}")
        print(f"  Confidence:      {result['confidence']}")
        print(f"\nEduBot: {result['answer']}\n")


if __name__ == "__main__":
    main()
