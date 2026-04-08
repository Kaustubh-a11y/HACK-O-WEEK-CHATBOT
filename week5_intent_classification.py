"""
=============================================================================
  WEEK 5 – Intent Classification for Queries
  ---------------------------------------------
  Define 5–7 intents (admissions, exams, timetable, hostel, scholarships,
  placements) and train a simple classifier to route student queries to
  the correct intent bucket.
=============================================================================
"""

import re
import math

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


# ─────────────────────  TF-IDF Engine (from Week 4, simplified)  ─────────

SYNONYM_GROUPS = {
    "fees": ["fees", "fee", "cost", "tuition", "payment", "charge", "price", "pay", "expense"],
    "timing": ["timing", "timings", "time", "hours", "schedule", "open", "closing", "working"],
    "courses": ["course", "courses", "program", "degree", "branch", "stream", "offer", "study"],
    "admission": ["admission", "apply", "application", "enroll", "join", "register", "form", "eligibility"],
    "contact": ["contact", "phone", "number", "call", "email", "mail", "reach", "helpline"],
    "location": ["location", "address", "located", "campus", "situated", "directions"],
    "hostel": ["hostel", "accommodation", "stay", "dormitory", "dorm", "room", "boarding", "residence"],
    "scholarship": ["scholarship", "financial", "aid", "stipend", "grant", "merit", "waiver", "fund"],
    "placement": ["placement", "job", "career", "recruit", "company", "hire", "salary", "package", "lpa"],
    "exam": ["exam", "examination", "test", "assessment", "marks", "grade", "result", "score", "paper", "syllabus"],
    "timetable": ["timetable", "class", "lecture", "period", "routine", "calendar", "session"],
    "principal": ["principal", "director", "head", "hod", "faculty", "teacher", "professor"],
    "documents": ["document", "documents", "certificate", "marksheet", "proof", "submit"],
    "affiliation": ["affiliated", "university", "board", "accredited", "naac", "ugc"]
}

TOPIC_TO_FAQ_MAP = {
    "fees": 3, "timing": 1, "courses": 2, "admission": 4, "contact": 7,
    "location": 6, "hostel": 9, "scholarship": 10, "placement": 12,
    "principal": 15, "documents": 14, "affiliation": 13, "exam": 11, "timetable": 11
}


class TFIDFEngine:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.total_docs = len(FAQ_CORPUS)
        self.corpus_tokens = []
        self.df = {}
        self.corpus_vectors = []
        self._build_index()

    def _build_index(self):
        for doc in FAQ_CORPUS:
            res = self.preprocessor.process(doc["q"])
            tokens = res["tokens"]
            self.corpus_tokens.append(tokens)
            for t in set(tokens):
                self.df[t] = self.df.get(t, 0) + 1
        for tokens in self.corpus_tokens:
            tf = self._compute_tf(tokens)
            self.corpus_vectors.append({t: val * self._compute_idf(t) for t, val in tf.items()})

    def _compute_tf(self, tokens):
        tf = {}
        if not tokens: return tf
        for t in tokens: tf[t] = tf.get(t, 0) + 1
        for t in tf: tf[t] /= len(tokens)
        return tf

    def _compute_idf(self, token):
        return math.log(self.total_docs / (1 + self.df.get(token, 0)))

    def _cosine(self, a, b):
        dot = sum(a[k] * b[k] for k in a if k in b)
        na = math.sqrt(sum(v*v for v in a.values()))
        nb = math.sqrt(sum(v*v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def _match_topics(self, tokens):
        topics = set()
        for t in tokens:
            for topic, words in SYNONYM_GROUPS.items():
                if t in words: topics.add(topic)
        return list(topics)

    def retrieve(self, tokens):
        topics = self._match_topics(tokens)
        search = list(tokens)
        for t in topics: search.extend([t]*3)
        tf = self._compute_tf(search)
        qvec = {t: v * self._compute_idf(t) for t, v in tf.items()}
        scores = [{"doc": FAQ_CORPUS[i], "score": self._cosine(qvec, self.corpus_vectors[i])} for i in range(self.total_docs)]
        scores.sort(key=lambda x: x["score"], reverse=True)
        top = scores[0]
        conf = min(top["score"], 1.0)

        answer = ""
        if len(topics) > 1:
            parts = []
            for tp in topics:
                fid = TOPIC_TO_FAQ_MAP.get(tp)
                if fid:
                    f = next((d for d in FAQ_CORPUS if d["id"] == fid), None)
                    if f: parts.append(f["a"])
            if parts: answer = " | ".join(dict.fromkeys(parts)); conf = 1.0

        if not answer:
            if conf < 0.15 and not topics:
                answer = "I couldn't find a match. Please call +91-712-2345678."
                conf = 0.0
            elif conf < 0.15 and topics:
                fid = TOPIC_TO_FAQ_MAP.get(topics[0])
                f = next((d for d in FAQ_CORPUS if d["id"] == fid), None) if fid else None
                answer = f["a"] if f else top["doc"]["a"]
                conf = 0.9 if f else conf
            else:
                answer = top["doc"]["a"]

        related = [scores[i]["doc"]["q"] for i in range(1, min(4, len(scores))) if scores[i]["score"] > 0.05]
        return {"answer": answer, "confidence": conf, "matched_topics": topics, "related": related}


# ─────────────────────────────────────────────────────────────────────────────
# INTENT CLASSIFIER
# Define 6 intents with keyword lists; score each intent and pick the best
# ─────────────────────────────────────────────────────────────────────────────
INTENTS = {
    "ADMISSIONS": {
        "keywords": ["admission", "apply", "application", "enroll", "register",
                     "join", "form", "eligibility", "deadline", "last date",
                     "document", "process", "fees", "seat", "vacancy"],
        "prefix": "🎓 [Admissions Desk]",
        "className": "intent-admissions"
    },
    "EXAMS": {
        "keywords": ["exam", "examination", "test", "result", "marks", "grade",
                     "score", "paper", "syllabus", "pattern", "assessment",
                     "internal", "external", "practical", "theory"],
        "prefix": "📝 [Examination Cell]",
        "className": "intent-exams"
    },
    "TIMETABLE": {
        "keywords": ["timetable", "class", "lecture", "schedule", "period",
                     "routine", "timing", "when", "session", "calendar",
                     "semester", "weekly"],
        "prefix": "📅 [Academic Scheduler]",
        "className": "intent-timetable"
    },
    "HOSTEL": {
        "keywords": ["hostel", "accommodation", "stay", "room", "dorm",
                     "boarding", "lodge", "pg", "mess", "food", "warden",
                     "facility", "boys", "girls", "residence"],
        "prefix": "🏠 [Hostel Office]",
        "className": "intent-hostel"
    },
    "SCHOLARSHIPS": {
        "keywords": ["scholarship", "financial", "aid", "merit", "stipend",
                     "grant", "waiver", "concession", "discount", "free",
                     "fund", "needy", "income", "caste", "category"],
        "prefix": "💰 [Scholarship Cell]",
        "className": "intent-scholarships"
    },
    "PLACEMENTS": {
        "keywords": ["placement", "job", "career", "recruit", "company",
                     "hire", "salary", "package", "ctc", "lpa", "internship",
                     "campus", "drive", "offer", "letter"],
        "prefix": "💼 [Placement Cell]",
        "className": "intent-placements"
    }
}


class IntentClassifier:
    """
    Classifies user queries into one of 6 intents using keyword scoring.
    Supports multi-word phrase matching (+2 bonus) and tie-breaking.
    """

    def classify(self, tokens: list, raw_lowercased: str) -> dict:
        scores = {k: 0 for k in INTENTS}

        # Score single-word keyword matches
        for token in tokens:
            for intent, data in INTENTS.items():
                if token in data["keywords"]:
                    scores[intent] += 1

        # Bonus for multi-word phrase matches in raw text
        for intent, data in INTENTS.items():
            for kw in data["keywords"]:
                if " " in kw and kw in raw_lowercased:
                    scores[intent] += 2

        # Find best intent
        max_score = -1
        best_intent = None
        ties = 0

        for intent, score in scores.items():
            if score > max_score:
                max_score = score
                best_intent = intent
                ties = 1
            elif score == max_score and max_score > 0:
                ties += 1

        # No match → GENERAL
        if max_score == 0:
            return {
                "name": "GENERAL",
                "prefix": "🤖 [General Assistant]",
                "className": "intent-general",
                "score": 0
            }

        # Tie → MULTI_INTENT
        if ties > 1:
            return {
                "name": "MULTI_INTENT",
                "prefix": "🧩 [Multi-Department]",
                "className": "intent-general",
                "score": max_score
            }

        return {
            "name": best_intent,
            "prefix": INTENTS[best_intent]["prefix"],
            "className": INTENTS[best_intent]["className"],
            "score": max_score
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI Chat Loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    preprocessor = Preprocessor()
    classifier = IntentClassifier()
    tfidf = TFIDFEngine()

    print("=" * 60)
    print("  🧭 EduBot – Week 5: Intent Classification")
    print("  6 intents: Admissions | Exams | Timetable |")
    print("             Hostel | Scholarships | Placements")
    print("=" * 60)
    print("  Type a question or 'bye' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["bye", "exit", "quit"]:
            print("EduBot: Goodbye! 👋\n")
            break

        prep = preprocessor.process(user_input)
        tokens = prep["tokens"]

        # Classify intent
        intent = classifier.classify(tokens, prep["original_lowercased"])

        # Retrieve answer via TF-IDF
        tfidf_res = tfidf.retrieve(tokens)

        # Display
        print(f"\n  Tokens:     {tokens}")
        print(f"  Intent:     {intent['name']} (score: {intent['score']})")
        print(f"  Department: {intent['prefix']}")
        print(f"  Confidence: {tfidf_res['confidence']:.2%}")
        print(f"\n{intent['prefix']}: {tfidf_res['answer']}\n")


if __name__ == "__main__":
    main()
