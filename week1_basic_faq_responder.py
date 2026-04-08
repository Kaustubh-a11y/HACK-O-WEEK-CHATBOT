"""
=============================================================================
  WEEK 1 – Basic FAQ Responder
  -----------------------------
  Design a rule-based chatbot that answers 10–15 fixed institute FAQs
  (e.g., timings, fees, contacts) using simple if–else / pattern matching.
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# FAQ Database – 15 fixed institute frequently asked questions
# ─────────────────────────────────────────────────────────────────────────────
FAQ_LIST = [
    {
        "id": 1,
        "keywords": ["timing", "timings", "time", "hours", "open", "close"],
        "question": "What are the institute timings?",
        "answer": "We are open Monday to Saturday, 8:00 AM to 6:00 PM."
    },
    {
        "id": 2,
        "keywords": ["course", "courses", "program", "programs", "degree", "offer", "branch"],
        "question": "What courses does the institute offer?",
        "answer": "We offer BCA, BBA, B.Sc IT, MBA, and MCA programs."
    },
    {
        "id": 3,
        "keywords": ["fee", "fees", "cost", "tuition", "payment", "charge", "price"],
        "question": "What are the admission fees?",
        "answer": "UG courses: ₹45,000/year. PG courses: ₹60,000/year."
    },
    {
        "id": 4,
        "keywords": ["apply", "admission", "enroll", "join", "register", "application"],
        "question": "How do I apply for admission?",
        "answer": "Visit campus or apply online at www.institute.edu.in"
    },
    {
        "id": 5,
        "keywords": ["last date", "deadline", "last day"],
        "question": "What is the last date for admission?",
        "answer": "The last date for admission is 30th June 2025."
    },
    {
        "id": 6,
        "keywords": ["location", "address", "where", "located", "campus", "place"],
        "question": "Where is the institute located?",
        "answer": "123, College Road, Nagpur, Maharashtra - 440001."
    },
    {
        "id": 7,
        "keywords": ["contact", "phone", "number", "call", "helpline"],
        "question": "What is the contact number?",
        "answer": "Call us at +91-712-2345678 (Mon–Sat, 9AM–5PM)."
    },
    {
        "id": 8,
        "keywords": ["email", "mail", "email address"],
        "question": "What is the email address?",
        "answer": "Email us at admissions@institute.edu.in"
    },
    {
        "id": 9,
        "keywords": ["hostel", "accommodation", "stay", "dormitory", "dorm", "room"],
        "question": "Is hostel facility available?",
        "answer": "Yes! Separate hostels for boys and girls with 24/7 security."
    },
    {
        "id": 10,
        "keywords": ["scholarship", "financial", "aid", "merit", "concession"],
        "question": "Do you offer scholarships?",
        "answer": "Yes, merit-based and need-based scholarships are available."
    },
    {
        "id": 11,
        "keywords": ["ratio", "student teacher", "faculty ratio"],
        "question": "What is the student teacher ratio?",
        "answer": "Our student-teacher ratio is 20:1."
    },
    {
        "id": 12,
        "keywords": ["placement", "placements", "job", "recruit", "career", "company"],
        "question": "What is the placement record?",
        "answer": "85%+ placement record. Top recruiters include TCS, Infosys, Wipro."
    },
    {
        "id": 13,
        "keywords": ["affiliated", "affiliation", "university", "naac", "accredited"],
        "question": "Is the institute affiliated to any university?",
        "answer": "Yes, affiliated to RTM Nagpur University. NAAC A+ accredited."
    },
    {
        "id": 14,
        "keywords": ["document", "documents", "marksheet", "certificate", "proof", "required"],
        "question": "What documents are needed for admission?",
        "answer": "10th & 12th marksheets, ID proof, passport-size photo, TC."
    },
    {
        "id": 15,
        "keywords": ["principal", "head", "director"],
        "question": "How do I contact the principal?",
        "answer": "Email: principal@institute.edu.in or visit during 10AM–12PM."
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# Rule-Based Pattern Matcher
# ─────────────────────────────────────────────────────────────────────────────
def find_answer(user_input: str) -> str:
    """
    Matches user input against FAQ keywords using simple if-else / pattern
    matching logic. Returns the best matching answer or a default message.
    """
    query = user_input.lower().strip()

    # Check each FAQ entry for keyword matches
    best_match = None
    best_score = 0

    for faq in FAQ_LIST:
        score = 0
        for keyword in faq["keywords"]:
            if keyword in query:
                score += 1
        if score > best_score:
            best_score = score
            best_match = faq

    # If-else threshold: at least 1 keyword must match
    if best_match and best_score >= 1:
        return f"[FAQ #{best_match['id']}] {best_match['answer']}"
    else:
        return ("I'm sorry, I couldn't understand your question. "
                "Please try asking about timings, fees, courses, "
                "admission, hostel, placements, or contact info.")


# ─────────────────────────────────────────────────────────────────────────────
# Greeting / Exit Pattern Matching
# ─────────────────────────────────────────────────────────────────────────────
GREETINGS    = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
EXIT_WORDS   = ["bye", "exit", "quit", "goodbye", "thanks", "thank you"]


def check_greeting(user_input: str) -> str | None:
    """Returns a greeting response if the input matches a greeting pattern."""
    query = user_input.lower().strip()
    for greet in GREETINGS:
        if greet in query:
            return "Hello! 👋 I'm EduBot. Ask me anything about our institute!"
    return None


def check_exit(user_input: str) -> bool:
    """Returns True if the user wants to exit."""
    query = user_input.lower().strip()
    for word in EXIT_WORDS:
        if word in query:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# CLI Chat Loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  🤖 EduBot – Week 1: Basic FAQ Responder")
    print("  Rule-based chatbot with if-else pattern matching")
    print("=" * 55)
    print("  Type your question or 'bye' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        # Check exit
        if check_exit(user_input):
            print("EduBot: Goodbye! Have a great day! 👋\n")
            break

        # Check greeting
        greeting = check_greeting(user_input)
        if greeting:
            print(f"EduBot: {greeting}\n")
            continue

        # Pattern-match FAQs
        answer = find_answer(user_input)
        print(f"EduBot: {answer}\n")


if __name__ == "__main__":
    main()
