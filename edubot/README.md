# EduBot Pro Backend & Frontend
Fully AI-driven FAQ response system utilizing pure Python NLP pipelines (TF-IDF, Tokenization, Classifier, Entity Extraction, Session Management, Channel Formats, and Analytics).

## Features
**Module 1:** Custom Lowercase + Stopword + Stemming preprocessor.
**Module 2:** Synonym mapping via groups.
**Module 3:** Pure TF-IDF retrieval system.
**Module 4:** Naïve Bayes keyword count intent classification.
**Module 6:** Regular expression entity extraction (`Semester`, `Course`, `Year`, `Date`).
**Module 7:** Contextual memory / conversational follow-up merging.
**Module 8:** Intelligent fallback (Clarification, Suggestion, Human Handover).
**Module 9:** Multichannel JSON response adapter (`web`, `mobile`, `whatsapp`, `cli`).
**Module 10:** Persistent JSONL logging & analytics reporting endpoint.

## Requirements
```bash
pip install -r backend/requirements.txt
```
*(Only `flask` and `flask-cors`)*

## Running the Web System
1. `cd backend`
2. `python app.py`
3. Open `frontend/index.html` in Chrome/Firefox.

## Simulating Channels via CLI
We built a rich terminal CLI simulator to test formatting output across various devices without needing actual React Native or WhatsApp Business API setups.

Ensure the Flask server is running in another tab:
```bash
python app.py
```

Then run the CLI Simulator:
```bash
cd backend
python channel_cli.py
```

**Options:**
- `--channel whatsapp`: See strict Markdown and interactive buttons.
- `--channel mobile`: See JSON objects optimized for cards and lists.
- `--channel web`: See HTML representations.
- `--compare`: Send a single message to all 3 simulated endpoints at once and see side-by-side terminal output.

## Analytics Dashboard
While on the Web Frontend (`index.html`), click the `📊 Analytics` tab in the top right to view live charts and metrics computed by Module 10 over the `logs/interactions.jsonl` data. 
You can upvote/downvote answers in the chat, which instantly saves via HTTP REST point to the logs.
