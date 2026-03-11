from datetime import datetime, timedelta

CLARIFICATION_PROMPTS = {
    "semester": "Which semester are you asking about? (e.g., Sem 3, Sem 5)",
    "course": "Which course/branch? (e.g., BCA, CS, IT, MBA)",
    "year": "Which year of study? (First/Second/Third/Final year)",
    "date": "Could you specify the date or time period?"
}

class ConversationContext:
    """Manages chat context and detects follow-ups."""
    def __init__(self):
        self.sessions = {}
        
    def _create_session(self, session_id):
        self.sessions[session_id] = {
            "session_id": session_id,
            "turns": [],
            "active_intent": None,
            "active_entities": {},
            "last_topic": None,
            "awaiting_clarification": False,
            "clarification_type": None,
            "last_updated": datetime.now()
        }
        
    def _clean_expired(self):
        now = datetime.now()
        expired = []
        for sid, state in self.sessions.items():
            if now - state["last_updated"] > timedelta(minutes=30):
                expired.append(sid)
        for sid in expired:
            del self.sessions[sid]

    def get_context(self, session_id):
        self._clean_expired()
        if session_id not in self.sessions:
            self._create_session(session_id)
        else:
            self.sessions[session_id]["last_updated"] = datetime.now()
        return self.sessions[session_id]

    def reset_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def is_followup(self, processed_tokens: list, raw_query: str, entities: dict) -> bool:
        low_q = raw_query.lower()
        if len(processed_tokens) < 6:
            pronouns = ["it", "that", "this", "they", "there"]
            if any(p in processed_tokens for p in pronouns):
                return True
                
            if entities and len(processed_tokens) <= 3:
                return True
                
            starts_with = ["what about", "and for", "how about", "same for", "also", "what if"]
            for prefix in starts_with:
                if low_q.startswith(prefix):
                    return True
        return False

    def resolve(self, query: str, context: dict, new_entities: dict) -> str:
        merged_entities = {**context.get("active_entities", {}), **new_entities}
        
        parts = []
        if context["last_topic"]:
            parts.append(context["last_topic"])
        if merged_entities.get("semester"):
            parts.append(f"semester {merged_entities['semester']}")
        if merged_entities.get("year"):
            parts.append(merged_entities['year'])
        if merged_entities.get("course"):
            parts.append(merged_entities['course'])
        if merged_entities.get("date"):
            parts.append(merged_entities['date'])
            
        enriched_query = " ".join(parts).strip()
        if not enriched_query: 
            return query
        return enriched_query

    def update(self, session_id: str, turn_data: dict, needs_clarification: list = None):
        if session_id not in self.sessions:
            self._create_session(session_id)
            
        ctx = self.sessions[session_id]
        
        ctx["turns"].append(turn_data)
        if len(ctx["turns"]) > 5:
            ctx["turns"].pop(0)
            
        if turn_data.get("intent") and turn_data["intent"] != "GENERAL":
            ctx["active_intent"] = turn_data["intent"]
            
        ctx["active_entities"].update(turn_data.get("entities", {}))
        
        if turn_data.get("topic"):
            ctx["last_topic"] = turn_data["topic"]
            
        if needs_clarification:
            ctx["awaiting_clarification"] = True
            ctx["clarification_type"] = needs_clarification
        else:
            ctx["awaiting_clarification"] = False
            ctx["clarification_type"] = None
            
        ctx["last_updated"] = datetime.now()

    def clarification_prompt(self, missing_entity: str) -> str:
        return CLARIFICATION_PROMPTS.get(missing_entity, "Can you provide more details?")
