# MODULE 4: Intent Classification

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
    """Classifies user query into one of the known intents based on keywords and scores."""
    def classify(self, tokens: list, raw_lowercased: str) -> dict:
        scores = {k: 0 for k in INTENTS}

        # Value words: partial/synonym matches
        for token in tokens:
            for intent, data in INTENTS.items():
                if token in data['keywords']:
                    scores[intent] += 1

        # Exact phrase checks gives +2 score
        for intent, data in INTENTS.items():
            for kw in data['keywords']:
                if " " in kw and kw in raw_lowercased:
                    scores[intent] += 2

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

        if max_score == 0:
            return {
                "name": "GENERAL",
                "prefix": "🤖 [General Assistant]",
                "className": "intent-general",
                "score": 0
            }

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
