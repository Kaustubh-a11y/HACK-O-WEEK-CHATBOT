"""
=============================================================================
  WEEK 6 – Entity Extraction for Dates & Courses
  -------------------------------------------------
  Implement basic entity recognition to extract dates, course codes, and
  semester numbers from questions (e.g., "When is SEM 5 CS exam?") and
  use them in responses.
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


# ─────────────────────  FAQ + TF-IDF (from Week 4, compact)  ─────────────

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

SYNONYM_GROUPS = {
    "fees": ["fees", "fee", "cost", "tuition", "payment", "charge", "price"],
    "timing": ["timing", "timings", "time", "hours", "schedule", "open"],
    "courses": ["course", "courses", "program", "degree", "branch", "offer"],
    "admission": ["admission", "apply", "application", "enroll", "join", "register"],
    "contact": ["contact", "phone", "number", "call", "email", "mail"],
    "location": ["location", "address", "located", "campus", "situated"],
    "hostel": ["hostel", "accommodation", "stay", "dorm", "room", "boarding"],
    "scholarship": ["scholarship", "financial", "aid", "stipend", "grant", "merit"],
    "placement": ["placement", "job", "career", "recruit", "company", "salary"],
    "exam": ["exam", "examination", "test", "marks", "result", "paper", "syllabus"],
    "timetable": ["timetable", "class", "lecture", "period", "routine", "calendar"],
    "principal": ["principal", "director", "head", "hod"],
    "documents": ["document", "documents", "certificate", "marksheet", "proof"],
    "affiliation": ["affiliated", "university", "accredited", "naac"]
}
TOPIC_TO_FAQ = {"fees":3,"timing":1,"courses":2,"admission":4,"contact":7,"location":6,"hostel":9,"scholarship":10,"placement":12,"principal":15,"documents":14,"affiliation":13,"exam":11,"timetable":11}

class TFIDFEngine:
    def __init__(self):
        self.pp = Preprocessor()
        self.N = len(FAQ_CORPUS)
        self.ct = []
        self.df = {}
        self.cv = []
        self._build()
    def _build(self):
        for d in FAQ_CORPUS:
            t = self.pp.process(d["q"])["tokens"]; self.ct.append(t)
            for u in set(t): self.df[u] = self.df.get(u,0)+1
        for t in self.ct:
            tf = {}
            for w in t: tf[w] = tf.get(w,0)+1
            for w in tf: tf[w] /= len(t) if t else 1
            self.cv.append({w: tf[w]*math.log(self.N/(1+self.df.get(w,0))) for w in tf})
    def _cos(self, a, b):
        d = sum(a[k]*b[k] for k in a if k in b)
        na = math.sqrt(sum(v*v for v in a.values())); nb = math.sqrt(sum(v*v for v in b.values()))
        return d/(na*nb) if na and nb else 0
    def _topics(self, tokens):
        t = set()
        for w in tokens:
            for tp,ws in SYNONYM_GROUPS.items():
                if w in ws: t.add(tp)
        return list(t)
    def retrieve(self, tokens):
        topics = self._topics(tokens)
        s = list(tokens)
        for t in topics: s.extend([t]*3)
        tf = {}
        for w in s: tf[w] = tf.get(w,0)+1
        for w in tf: tf[w]/=len(s)
        qv = {w:tf[w]*math.log(self.N/(1+self.df.get(w,0))) for w in tf}
        scores = sorted([{"d":FAQ_CORPUS[i],"s":self._cos(qv,self.cv[i])} for i in range(self.N)], key=lambda x:-x["s"])
        top = scores[0]; conf = min(top["s"],1.0)
        ans = ""
        if len(topics)>1:
            ps = [next((d for d in FAQ_CORPUS if d["id"]==TOPIC_TO_FAQ.get(t)),None) for t in topics]
            ps = [p["a"] for p in ps if p]
            if ps: ans = " | ".join(dict.fromkeys(ps)); conf = 1.0
        if not ans:
            if conf < 0.15 and topics:
                f = next((d for d in FAQ_CORPUS if d["id"]==TOPIC_TO_FAQ.get(topics[0])),None)
                ans = f["a"] if f else top["d"]["a"]; conf = 0.9 if f else conf
            elif conf < 0.15: ans = "I couldn't find a match."; conf = 0
            else: ans = top["d"]["a"]
        return {"answer":ans,"confidence":conf,"matched_topics":topics}


# ─────────────────────────────────────────────────────────────────────────────
# ENTITY EXTRACTOR – extracts semester, course, date, year, roll number
# ─────────────────────────────────────────────────────────────────────────────

COURSE_ALIASES = {
    "cs": "Computer Science", "it": "Information Technology",
    "bca": "BCA", "bba": "BBA", "mba": "MBA", "mca": "MCA",
    "bsc": "B.Sc IT", "civil": "Civil Engineering",
    "mech": "Mechanical Engineering",
    "computer science": "Computer Science",
    "information technology": "Information Technology",
    "commerce": "Commerce"
}

WORD_TO_NUM = {
    "first": 1, "second": 2, "third": 3, "fourth": 4,
    "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8
}

RESPONSE_TEMPLATES = {
    "semester+course": "For Semester {semester} {course}, {base}",
    "semester_only":   "Regarding Semester {semester}: {base}",
    "course_only":     "For {course} students: {base}",
    "date_only":       "On {date}: {base}",
    "year_only":       "For {year} students: {base}",
    "semester+year":   "Semester {semester} ({year}): {base}",
    "none":            "{base}"
}


class EntityExtractor:
    """
    Extracts structured entities from free-form student questions:
      - Semester number  (e.g., SEM 5, 3rd semester, fifth sem)
      - Course/branch    (e.g., CS, BCA, MBA)
      - Date/month       (e.g., 15/06, March 20, tomorrow)
      - Year             (e.g., 2025, third year)
      - Roll number      (e.g., BCA2023001)
    """

    def extract(self, query: str) -> dict:
        entities = {}
        low = query.lower()

        # 1. SEMESTER NUMBER
        m = re.search(r'\bsem(?:ester)?\s*[-]?\s*(\d+)\b', low)
        if not m:
            m = re.search(r'\b(\d+)(?:st|nd|rd|th)\s+sem(?:ester)?\b', low)
        if not m:
            m2 = re.search(r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth)\s+sem\b', low)
            if m2:
                entities["semester"] = WORD_TO_NUM[m2.group(1)]
        if m:
            entities["semester"] = int(m.group(1))

        # 2. COURSE / BRANCH
        for alias, full_name in COURSE_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', low):
                entities["course"] = full_name
                break

        # 3. DATE / MONTH
        d = re.search(r'\b(\d{1,2})[/\-.](\d{1,2})(?:[/\-.](\d{2,4}))?\b', low)
        months = r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
        if not d:
            d = re.search(r'\b(\d{1,2})\s+' + months + r'\b', low)
        if not d:
            d = re.search(r'\b' + months + r'\s+(\d{1,2})\b', low)
        if not d:
            d = re.search(r'\b(tomorrow|today|next\s+\w+|this\s+week|this\s+month)\b', low)
        if d:
            entities["date"] = d.group(0)

        # 4. YEAR
        y = re.search(r'\b(20\d{2})\b', low)
        if not y:
            y = re.search(r'\b(first|second|third|final)\s+year\b', low)
        if y:
            entities["year"] = y.group(0) if not y.group(0).isdigit() else y.group(1)

        # 5. ROLL NUMBER
        r = re.search(r'\b([a-z]{1,4}\d{4,8})\b', low)
        if not r:
            r = re.search(r'\b(\d{4}[a-z]{2,5}\d{3})\b', low)
        if r:
            entities["roll_no"] = r.group(1).upper()

        return entities

    def enhance_answer(self, base_answer: str, entities: dict) -> str:
        """Injects extracted entities into a response template."""
        sem = entities.get("semester")
        crs = entities.get("course")
        dt  = entities.get("date")
        yr  = entities.get("year")

        if sem and crs:
            tpl = RESPONSE_TEMPLATES["semester+course"]
        elif sem and yr:
            tpl = RESPONSE_TEMPLATES["semester+year"]
        elif sem:
            tpl = RESPONSE_TEMPLATES["semester_only"]
        elif crs:
            tpl = RESPONSE_TEMPLATES["course_only"]
        elif yr:
            tpl = RESPONSE_TEMPLATES["year_only"]
        elif dt:
            tpl = RESPONSE_TEMPLATES["date_only"]
        else:
            tpl = RESPONSE_TEMPLATES["none"]

        return tpl.format(
            semester=sem or "", course=crs or "",
            date=dt or "", year=yr or "", base=base_answer
        ).replace("  ", " ").strip()


# ─────────────────────────────────────────────────────────────────────────────
# CLI Chat Loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    preprocessor = Preprocessor()
    tfidf = TFIDFEngine()
    extractor = EntityExtractor()

    print("=" * 60)
    print("  🔍 EduBot – Week 6: Entity Extraction")
    print("  Try: 'When is SEM 5 CS exam?'")
    print("       'Fees for BCA 2025?'")
    print("       'Result for third year on 15 March?'")
    print("=" * 60)
    print("  Type a question or 'bye' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["bye", "exit", "quit"]:
            print("EduBot: Goodbye! 👋\n")
            break

        # Extract entities
        entities = extractor.extract(user_input)

        # Preprocess + retrieve
        prep = preprocessor.process(user_input)
        tfidf_res = tfidf.retrieve(prep["tokens"])

        # Enhance answer with entities
        enhanced = extractor.enhance_answer(tfidf_res["answer"], entities)

        # Display
        print(f"\n  Tokens:      {prep['tokens']}")
        print(f"  Entities:    {entities}")
        print(f"  Confidence:  {tfidf_res['confidence']:.2%}")
        print(f"\nEduBot: {enhanced}\n")


if __name__ == "__main__":
    main()
