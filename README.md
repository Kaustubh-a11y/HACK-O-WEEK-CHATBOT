# EduBot Pro: Intelligent Institute Chatbot

EduBot Pro is a comprehensive, progressive chatbot system designed for educational institutes. It demonstrates a complete NLP pipeline from basic rule-based responses to advanced TF-IDF retrieval, intent classification, entity extraction, and context-aware multi-turn conversations.

Originally developed as a "Hack-O-Week" project, the repository is organized into 10 independent weekly modules to facilitate easy evaluation of specific chatbot components.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Browser (Chrome/Edge/Firefox)

### Installation
1. Clone this repository to your local machine.
2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📅 Weekly Progression (Modules)

Each script below is **self-contained** and can be run independently using `python filename.py`. They demonstrate the progressive complexity of the chatbot logic.

| Week | Module | Description |
| :--- | :--- | :--- |
| **Week 1** | `week1_basic_faq_responder.py` | Simple rule-based logic for 15 fixed FAQs. |
| **Week 2** | `week2_preprocessing_queries.py` | 5-step NLP pipeline: Lowercasing, Punctuation removal, Tokenization, Stopwords, and Spelling correction. |
| **Week 3** | `week3_synonym_aware_bot.py` | Implementation of synonym groups for semantic matching (e.g., "fees" ↔ "tuition"). |
| **Week 4** | `week4_tfidf_retrieval.py` | Advanced retrieval using TF-IDF vectorization and Cosine Similarity ranking. |
| **Week 5** | `week5_intent_classification.py` | 6-intent classifier for routing queries to departments (Admissions, Exams, etc.). |
| **Week 6** | `week6_entity_extraction.py` | Regex-based extraction of specific entities like Semester, Course, and Dates. |
| **Week 7** | `week7_context_followups.py` | Session-based state management for handling follow-up questions (e.g., "For SEM 3?"). |
| **Week 8** | `week8_fallbacks_handover.py` | Intelligent fallback strategies: Clarification, Suggestions, and Human Handover. |
| **Week 9** | `week9_multichannel_mockup.py` | Simulation of response formatting for Web, Mobile, and WhatsApp. |
| **Week 10**| `week10_analytics_improvement.py`| Performance logging to JSONL, feedback tracking, and automated improvement proposals. |

---

## 🌐 Full Web Application

The repository includes a premium integrated web interface.

### Running the Full App
1. Start the Flask backend:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to:
   `http://localhost:5000`

### Key Web Features
- **Modern UI/UX**: Dark-mode glassmorphism interface with smooth animations.
- **Pipeline Debug Panel**: Real-time view of what the NLP pipeline is doing (tokens, intensities, etc.).
- **Intent & Confidence**: Visual feedback on how the bot interpreted your query.
- **Analytics Dashboard**: View session statistics, intent distribution, and recent logs directly in the UI.
- **Feedback Loop**: Rate answers with 👍/👎 to generate data for continuous improvement.

---

## 📂 Project Structure

- `app.py`: Main Flask backend integrating all 10 modules.
- `index.html`: Premium frontend interface.
- `requirements.txt`: Project dependencies (Flask, Flask-CORS).
- `week*.py`: Individual weekly learning modules.
- `logs/`: Directory  for interaction logs and analytics data.

---

## 🛠️ Built With

- **Backend**: Python, Flask, Flask-CORS
- **NLP**: Custom regex-based and math-based (TF-IDF) implementations
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+)


