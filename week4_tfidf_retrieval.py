"""
=============================================================================
  WEEK 4 – FAQ Retrieval with TF-IDF
  -------------------------------------
  Build a retrieval-based chatbot that stores FAQs and uses TF-IDF
  similarity to select the most relevant answer for a student's query.
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


# ─────────────────────  Synonym Boost (from Week 3)  ─────────────────────

SYNONYM_GROUPS = {
    "fees":        ["fees", "fee", "cost", "costs", "tuition", "payment", "charge", "charges", "price", "pricing", "amount", "pay", "expense", "expenses"],
    "timing":      ["timing", "timings", "time", "times", "hours", "hour", "schedule", "open", "opening", "close", "closing", "working", "office"],
    "courses":     ["course", "courses", "program", "programs", "degree", "degrees", "branch", "branches", "stream", "streams", "subject", "subjects", "offer", "offered", "available", "study", "studying"],
    "admission":   ["admission", "admissions", "apply", "application", "enroll", "enrollment", "join", "joining", "register", "registration", "form", "forms", "process", "procedure", "eligibility"],
    "contact":     ["contact", "contacts", "phone", "number", "call", "email", "mail", "address", "reach", "helpline", "support", "connect"],
    "location":    ["location", "address", "located", "place", "where", "campus", "situated", "find", "directions", "map", "area", "city"],
    "hostel":      ["hostel", "hostels", "accommodation", "stay", "dormitory", "dorm", "room", "rooms", "boarding", "lodge", "lodging", "pg", "housing", "residence"],
    "scholarship": ["scholarship", "scholarships", "financial", "aid", "stipend", "grant", "grants", "merit", "waiver", "concession", "discount", "free", "sponsored", "fund", "funding"],
    "placement":   ["placement", "placements", "job", "jobs", "career", "careers", "recruit", "recruitment", "company", "companies", "hire", "hiring", "employ", "employment", "package", "salary", "lpa", "ctc"],
    "exam":        ["exam", "exams", "examination", "test", "tests", "assessment", "marks", "grade", "grades", "result", "results", "score", "scores", "paper", "papers", "pattern", "syllabus"],
    "timetable":   ["timetable", "timetables", "class", "classes", "lecture", "lectures", "period", "periods", "routine", "calendar", "session", "sessions"],
    "principal":   ["principal", "director", "head", "hod", "faculty", "teacher", "professor", "staff", "administration", "admin"],
    "documents":   ["document", "documents", "certificate", "certificates", "marksheet", "marksheets", "required", "submit", "submission", "proof", "id", "photo", "passport"],
    "affiliation": ["affiliated", "affiliation", "university", "board", "recognized", "approved", "accredited", "naac", "ugc", "aicte"]
}

TOPIC_TO_FAQ_MAP = {
    "fees": 3, "timing": 1, "courses": 2, "admission": 4, "contact": 7,
    "location": 6, "hostel": 9, "scholarship": 10, "placement": 12,
    "principal": 15, "documents": 14, "affiliation": 13, "exam": 11, "timetable": 11
}


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
# TF-IDF Engine
# ─────────────────────────────────────────────────────────────────────────────
class TFIDFEngine:
    """
    Builds a TF-IDF index over the FAQ corpus questions.
    Retrieves the best matching FAQ using cosine similarity.
    """

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.total_docs = len(FAQ_CORPUS)
        self.corpus_tokens = []
        self.df = {}                   # document frequency per token
        self.corpus_vectors = []       # TF-IDF vector for each FAQ question

        self._build_index()

    def _build_index(self):
        """Pre-compute TF-IDF vectors for all FAQ questions."""
        # Step 1: Tokenize each document and compute document frequency
        for doc in FAQ_CORPUS:
            res = self.preprocessor.process(doc["q"])
            tokens = res["tokens"]
            self.corpus_tokens.append(tokens)

            unique_tokens = set(tokens)
            for t in unique_tokens:
                self.df[t] = self.df.get(t, 0) + 1

        # Step 2: Compute TF-IDF vector for each document
        for tokens in self.corpus_tokens:
            tf = self._compute_tf(tokens)
            vec = {}
            for t, val in tf.items():
                vec[t] = val * self._compute_idf(t)
            self.corpus_vectors.append(vec)

    def _compute_tf(self, tokens: list) -> dict:
        """Term Frequency: count / total tokens in document."""
        tf = {}
        if not tokens:
            return tf
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        for t in tf:
            tf[t] /= len(tokens)
        return tf

    def _compute_idf(self, token: str) -> float:
        """Inverse Document Frequency: log(N / (1 + df))."""
        docs_with_token = self.df.get(token, 0)
        return math.log(self.total_docs / (1 + docs_with_token))

    def _vector_norm(self, vec: dict) -> float:
        return math.sqrt(sum(v * v for v in vec.values()))

    def _cosine_similarity(self, vec_a: dict, vec_b: dict) -> float:
        """Cosine similarity between two sparse TF-IDF vectors."""
        dot = sum(vec_a[k] * vec_b[k] for k in vec_a if k in vec_b)
        norm_a = self._vector_norm(vec_a)
        norm_b = self._vector_norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _get_matched_topics(self, tokens: list) -> list:
        """Returns synonym-group topics that match query tokens."""
        topics = set()
        for token in tokens:
            for topic, words in SYNONYM_GROUPS.items():
                if token in words:
                    topics.add(topic)
        return list(topics)

    def retrieve(self, query_tokens: list) -> dict:
        """
        Main retrieval method.
        1. Boost query with synonym topics
        2. Compute TF-IDF for the query
        3. Rank all FAQs by cosine similarity
        4. Return best answer + related questions
        """
        matched_topics = self._get_matched_topics(query_tokens)

        # Boost search with synonym topics
        search_tokens = list(query_tokens)
        for topic in matched_topics:
            search_tokens.extend([topic] * 3)

        # Compute query TF-IDF vector
        tf = self._compute_tf(search_tokens)
        query_vec = {t: val * self._compute_idf(t) for t, val in tf.items()}

        # Score all documents
        scores = []
        for idx, doc in enumerate(FAQ_CORPUS):
            score = self._cosine_similarity(query_vec, self.corpus_vectors[idx])
            scores.append({"doc": doc, "score": score})

        scores.sort(key=lambda x: x["score"], reverse=True)
        top = scores[0]
        confidence = min(top["score"], 1.0)

        # Determine answer
        answer = ""
        if len(matched_topics) > 1:
            parts = []
            for topic in matched_topics:
                fid = TOPIC_TO_FAQ_MAP.get(topic)
                if fid:
                    f = next((d for d in FAQ_CORPUS if d["id"] == fid), None)
                    if f:
                        parts.append(f["a"])
            if parts:
                answer = " | ".join(dict.fromkeys(parts))
                confidence = 1.0

        if not answer:
            if confidence < 0.15 and not matched_topics:
                answer = "I couldn't find a match. Please call +91-712-2345678."
                confidence = 0.0
            elif confidence < 0.15 and matched_topics:
                fid = TOPIC_TO_FAQ_MAP.get(matched_topics[0])
                f = next((d for d in FAQ_CORPUS if d["id"] == fid), None) if fid else None
                answer = f["a"] if f else top["doc"]["a"]
                confidence = 0.9 if f else confidence
            else:
                answer = top["doc"]["a"]

        # Related questions
        related = []
        if confidence > 0:
            for i in range(1, min(4, len(scores))):
                if scores[i]["score"] > 0.05:
                    related.append(scores[i]["doc"]["q"])

        return {
            "answer": answer,
            "confidence": confidence,
            "top_match": {"faq_id": top["doc"]["id"], "score": top["score"]},
            "matched_topics": matched_topics,
            "related": related,
            "all_scores": [(s["doc"]["id"], round(s["score"], 4)) for s in scores[:5]]
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI Chat Loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    preprocessor = Preprocessor()
    engine = TFIDFEngine()

    print("=" * 60)
    print("  📊 EduBot – Week 4: FAQ Retrieval with TF-IDF")
    print("  Cosine-similarity ranking over 15 FAQ documents")
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
        result = engine.retrieve(prep["tokens"])

        print(f"\n  Tokens:      {prep['tokens']}")
        print(f"  Topics:      {result['matched_topics']}")
        print(f"  Confidence:  {result['confidence']:.2%}")
        print(f"  Top Scores:  {result['all_scores']}")
        if result["related"]:
            print(f"  Related:     {result['related']}")
        print(f"\nEduBot: {result['answer']}\n")


if __name__ == "__main__":
    main()
