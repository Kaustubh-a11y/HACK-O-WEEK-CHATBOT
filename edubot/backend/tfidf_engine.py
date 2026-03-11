import math
from faq_data import FAQ_CORPUS
from preprocessor import Preprocessor

# MODULE 2: Synonym-Aware Matcher embedded in TFIDF setup as domain boost
SYNONYM_GROUPS = {
    "fees": ["fees", "fee", "cost", "costs", "tuition", "payment", "charge", "charges", "price", "pricing", "amount", "pay", "expense", "expenses"],
    "timing": ["timing", "timings", "time", "times", "hours", "hour", "schedule", "open", "opening", "close", "closing", "working", "office"],
    "courses": ["course", "courses", "program", "programs", "degree", "degrees", "branch", "branches", "stream", "streams", "subject", "subjects", "offer", "offered", "available", "study", "studying"],
    "admission": ["admission", "admissions", "apply", "application", "enroll", "enrollment", "join", "joining", "register", "registration", "form", "forms", "process", "procedure", "eligibility"],
    "contact": ["contact", "contacts", "phone", "number", "call", "email", "mail", "address", "reach", "helpline", "support", "connect"],
    "location": ["location", "address", "located", "place", "where", "campus", "situated", "find", "directions", "map", "area", "city"],
    "hostel": ["hostel", "hostels", "accommodation", "stay", "dormitory", "dorm", "room", "rooms", "boarding", "lodge", "lodging", "pg", "housing", "residence"],
    "scholarship": ["scholarship", "scholarships", "financial", "aid", "stipend", "grant", "grants", "merit", "waiver", "concession", "discount", "free", "sponsored", "fund", "funding"],
    "placement": ["placement", "placements", "job", "jobs", "career", "careers", "recruit", "recruitment", "company", "companies", "hire", "hiring", "employ", "employment", "package", "salary", "lpa", "ctc", "campus"],
    "exam": ["exam", "exams", "examination", "test", "tests", "assessment", "marks", "grade", "grades", "result", "results", "score", "scores", "paper", "papers", "pattern", "syllabus"],
    "timetable": ["timetable", "timetables", "class", "classes", "lecture", "lectures", "period", "periods", "routine", "calendar", "schedule", "session", "sessions"],
    "library": ["library", "books", "book", "read", "reading", "study", "resources", "digital", "e-library", "elib", "journals", "reference"],
    "principal": ["principal", "director", "head", "hod", "faculty", "teacher", "professor", "staff", "administration", "admin"],
    "documents": ["document", "documents", "certificate", "certificates", "marksheet", "marksheets", "required", "need", "submit", "submission", "proof", "id", "photo", "passport"],
    "affiliation": ["affiliated", "affiliation", "university", "board", "recognized", "approved", "accredited", "naac", "ugc", "aicte"]
}

TOPIC_TO_FAQ_MAP = {
    "fees": 3, "timing": 1, "courses": 2, "admission": 4, "contact": 7,
    "location": 6, "hostel": 9, "scholarship": 10, "placement": 12,
    "principal": 15, "documents": 14, "affiliation": 13, "exam": 11, "timetable": 11 # Map conceptually closely if exact missing
}

# MODULE 3: TF-IDF Retrieval
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
            res = self.preprocessor.process(doc['q'])
            tokens = res['tokens']
            self.corpus_tokens.append(tokens)
            
            unique_tokens = set(tokens)
            for t in unique_tokens:
                self.df[t] = self.df.get(t, 0) + 1
        
        for tokens in self.corpus_tokens:
            tf = self.compute_tf(tokens)
            vec = {}
            for t, val in tf.items():
                vec[t] = val * self.compute_idf(t)
            self.corpus_vectors.append(vec)

    def compute_tf(self, tokens: list) -> dict:
        tf = {}
        if not tokens:
            return tf
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        for t in tf:
            tf[t] /= len(tokens)
        return tf

    def compute_idf(self, token: str) -> float:
        docs_with_token = self.df.get(token, 0)
        return math.log(self.total_docs / (1 + docs_with_token))

    def compute_vector_norm(self, vec: dict) -> float:
        return math.sqrt(sum(v * v for v in vec.values()))

    def cosine_similarity(self, vec_a: dict, vec_b: dict) -> float:
        dot_product = sum(vec_a[k] * vec_b[k] for k in vec_a if k in vec_b)
        norm_a = self.compute_vector_norm(vec_a)
        norm_b = self.compute_vector_norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def get_matched_topics(self, tokens: list) -> list:
        topics = set()
        for token in tokens:
            for topic, words in SYNONYM_GROUPS.items():
                if token in words:
                    topics.add(topic)
        return list(topics)

    def retrieve(self, query_tokens: list) -> dict:
        matched_topics = self.get_matched_topics(query_tokens)
        
        # Boost search using synonym topics
        search_tokens = list(query_tokens)
        for topic in matched_topics:
            search_tokens.extend([topic, topic, topic]) # add boost
            
        tf = self.compute_tf(search_tokens)
        query_tfidf = {t: val * self.compute_idf(t) for t, val in tf.items()}
        
        scores = []
        for idx, doc in enumerate(FAQ_CORPUS):
            score = self.cosine_similarity(query_tfidf, self.corpus_vectors[idx])
            scores.append({"doc": doc, "score": score})
            
        scores.sort(key=lambda x: x['score'], reverse=True)
        top_match = scores[0]
        
        top_conf = min(top_match['score'], 1.0)
        final_answer = ""
        
        if len(matched_topics) > 1:
            answers = []
            for topic in matched_topics:
                fid = TOPIC_TO_FAQ_MAP.get(topic)
                if fid:
                    f = next((doc for doc in FAQ_CORPUS if doc['id'] == fid), None)
                    if f:
                        answers.append(f['a'])
            if answers:
                final_answer = " ".join(answers)
                top_conf = 1.0
                
        if not final_answer:
            if top_conf < 0.15 and not matched_topics:
                final_answer = "I couldn't find a match. Please call +91-712-2345678 or email admissions@institute.edu.in."
                top_conf = 0.0
            else:
                if top_conf < 0.15 and matched_topics:
                    fid = TOPIC_TO_FAQ_MAP.get(matched_topics[0])
                    if fid:
                        f = next((doc for doc in FAQ_CORPUS if doc['id'] == fid), None)
                        if f:
                            final_answer = f['a']
                            top_conf = 0.9
                        else:
                            final_answer = top_match['doc']['a']
                    else:
                        final_answer = top_match['doc']['a']
                else:
                    final_answer = top_match['doc']['a']

        related = []
        if top_conf > 0:
            for i in range(1, min(4, len(scores))):
                if scores[i]['score'] > 0.05:
                    related.append(scores[i]['doc']['q'])
                    
        return {
            "top_match": {"faq_id": top_match['doc']['id'], "score": top_match['score']},
            "answer": final_answer,
            "confidence": top_conf,
            "matched_topics": matched_topics,
            "related": related
        }
