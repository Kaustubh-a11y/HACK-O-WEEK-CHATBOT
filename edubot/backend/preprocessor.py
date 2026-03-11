import re

# MODULE 1: Text Preprocessing Pipeline

STOPWORDS = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
             "have", "has", "had", "do", "does", "did", "will", "would", "could",
             "should", "may", "might", "shall", "can", "need", "i", "me", "my",
             "we", "our", "you", "your", "it", "its", "this", "that", "these",
             "those", "what", "how", "when", "where", "who", "which", "tell",
             "please", "want", "know", "about", "of", "in", "on", "at",
             "to", "for", "with", "by"}

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
        """
        Runs the 5-step NLP preprocessing pipeline.
        Returns useful tokens and debug trace.
        """
        debug = {"original": text}

        # Step 1: Lowercasing
        lowercased = text.lower()
        debug['lowercased'] = lowercased

        # Step 2: Punctuation Removal
        no_punct = re.sub(r'[.,!?;:\'"()\[\]{}/\\@#$%^&*~`]', '', lowercased)
        debug['no_punct'] = no_punct

        # Step 3: Tokenization
        tokens = no_punct.split()
        debug['tokens'] = list(tokens)

        # Step 4: Stopword Removal
        no_stopwords = [t for t in tokens if t not in STOPWORDS]
        debug['no_stopwords'] = list(no_stopwords)

        # Step 5: Spelling Normalization
        normalized = [SPELLING_CORRECTIONS.get(t, t) for t in no_stopwords]
        debug['normalized'] = list(normalized)

        return {
            "tokens": normalized,
            "debug": debug,
            "original_lowercased": lowercased
        }
