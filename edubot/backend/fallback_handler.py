import random
from dataclasses import dataclass

@dataclass
class FallbackDecision:
    trigger: bool
    reason: str
    fallback_type: str
    confidence_score: float
    query_tokens: list
    matched_intent: str

OUT_OF_SCOPE = ["refund", "transfer", "tc", "leaving", "rusticate",
                "fight", "complaint", "legal", "court", "police",
                "ragging", "harassment", "politics", "strike",
                "medical", "hospital", "accident", "death"]

HANDOVER_CONTACTS = {
  "ADMISSIONS": {
    "name":  "Admissions Office",
    "email": "admissions@institute.edu.in",
    "phone": "+91-712-2345678",
    "desk":  "Room 101, Admin Block",
    "hours": "Mon–Sat, 9AM–5PM"
  },
  "EXAMS": {
    "name":  "Examination Cell",
    "email": "exams@institute.edu.in",
    "phone": "+91-712-2345679",
    "desk":  "Room 205, Academic Block",
    "hours": "Mon–Fri, 10AM–4PM"
  },
  "HOSTEL": {
    "name":  "Hostel Warden Office",
    "email": "hostel@institute.edu.in",
    "phone": "+91-712-2345680",
    "desk":  "Hostel Admin Block",
    "hours": "All days, 8AM–8PM"
  },
  "SCHOLARSHIPS": {
    "name":  "Scholarship Cell",
    "email": "scholarship@institute.edu.in",
    "phone": "+91-712-2345681",
    "desk":  "Room 102, Admin Block",
    "hours": "Mon–Fri, 10AM–3PM"
  },
  "GENERAL": {
    "name":  "Student Help Desk",
    "email": "helpdesk@institute.edu.in",
    "phone": "+91-712-2345678",
    "desk":  "Main Reception, Ground Floor",
    "hours": "Mon–Sat, 8AM–6PM"
  }
}

class FallbackHandler:
    """Handles cases where the bot cannot confidently answer."""
    
    def evaluate_fallback(self, pipeline_result: dict, context: dict) -> FallbackDecision:
        conf = pipeline_result.get("confidence", 0.0)
        tokens = pipeline_result.get("tokens", [])
        intent = pipeline_result.get("intent", "GENERAL")
        
        # Condition 6 - Repeated fallback
        consecutive = context.get("consecutive_fallbacks", 0)
        if consecutive >= 2:
            return FallbackDecision(True, "repeated_confusion", "handover", conf, tokens, intent)
            
        # Condition 4 - Out of scope
        if any(t in OUT_OF_SCOPE for t in tokens):
            return FallbackDecision(True, "out_of_scope_topic", "handover", conf, tokens, intent)
            
        # Condition 5 - Gibberish
        if len(tokens) > 30 or (len(tokens) > 0 and sum(len(t) for t in tokens) / len(tokens) > 12):
            return FallbackDecision(True, "malformed_query", "clarification", conf, tokens, intent)
            
        # Condition 2 - Unknown intent
        if intent in ["GENERAL", "MULTI_INTENT"] and conf < 0.25:
            return FallbackDecision(True, "no_intent_matched", "clarification", conf, tokens, intent)
            
        # Condition 3 - Very short query
        if len(tokens) <= 1 and conf < 0.40:
            return FallbackDecision(True, "query_too_short", "clarification", conf, tokens, intent)
            
        # Condition 1 - Low confidence
        if conf < 0.15:
            return FallbackDecision(True, "low_tfidf_confidence", "suggestion", conf, tokens, intent)
            
        return FallbackDecision(False, "", "", conf, tokens, intent)

    def generate_clarification(self, raw_query: str, faq_corpus: list) -> dict:
        suggestions_pool = random.sample(faq_corpus, min(3, len(faq_corpus)))
        suggestions = [doc['q'] for doc in suggestions_pool]
        
        return {
            "type": "clarification",
            "message": f"I'm not sure what you mean by '{raw_query}'. Could you rephrase? For example, try asking: • 'What are the admission fees?' • 'When is the SEM 4 exam?' • 'Is hostel available?'",
            "suggestions": suggestions,
            "follow_up_prompt": "Or choose a topic below:"
        }

    def generate_suggestions(self, tfidf_res: dict) -> dict:
        related = tfidf_res.get("related", [])
        did_you_mean = []
        if related:
            for r in related[:3]:
                did_you_mean.append({"question": r, "score": 0.10}) # placeholder score visually
                
        return {
            "type": "suggestion",
            "message": "I'm not confident I understood your question. Did you mean one of these?",
            "did_you_mean": did_you_mean,
            "instruction": "Click a suggestion or rephrase your question."
        }
        
    def generate_handover(self, raw_query: str, reason: str, session_id: str, intent: str, timestamp: str) -> dict:
        contact_info = HANDOVER_CONTACTS.get(intent, HANDOVER_CONTACTS["GENERAL"])
        ticket_id = f"TKT-{session_id[:8]}-{timestamp.replace('-', '').replace(':', '').replace('.', '')[:14]}"
        
        return {
            "type": "handover",
            "message": f"This question needs a human advisor. I've noted your query: '{raw_query}'",
            "reason_human_readable": "This topic requires personal assistance.",
            "contact": contact_info,
            "mailto_link": f"mailto:{contact_info['email']}?subject=Student Query&body=My question: {raw_query}",
            "ticket_id": ticket_id,
            "escalation_note": f"Your query has been logged as ticket {ticket_id}. The office will respond within 24 hours."
        }

    def handle(self, pipeline_result: dict, context: dict, faq_corpus: list) -> dict:
        decision = self.evaluate_fallback(pipeline_result, context)
        raw_query = pipeline_result.get("raw_query", "")
        
        if not decision.trigger:
            context["consecutive_fallbacks"] = 0
            return {
                "triggered": False,
                "data": None
            }
            
        context["consecutive_fallbacks"] = context.get("consecutive_fallbacks", 0) + 1
        
        if decision.fallback_type == "handover":
            fb_data = self.generate_handover(raw_query, decision.reason, context.get("session_id", ""), decision.matched_intent, str(context.get("last_updated")))
        elif decision.fallback_type == "suggestion":
            fb_data = self.generate_suggestions(pipeline_result.get("tfidf_result", {}))
        else: # clarification
            fb_data = self.generate_clarification(raw_query, faq_corpus)
            
        return {
            "triggered": True,
            "data": fb_data,
            "reason": decision.reason
        }
