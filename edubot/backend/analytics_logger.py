import json
import os
from datetime import datetime

class InteractionLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "interactions.jsonl")

    def log(self, data: dict) -> str:
        timestamp = datetime.utcnow().isoformat() + "Z"
        log_id = f"LOG-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{data.get('session_id', 'unknown')[:6]}"
        
        log_entry = {
            "log_id": log_id,
            "timestamp": timestamp,
            "session_id": data.get("session_id"),
            "turn_number": data.get("turn_number", 1),
            "channel": data.get("channel", "web"),
            "query": {
                "raw": data.get("raw_query", ""),
                "preprocessed": data.get("preprocessed_tokens", []),
                "char_length": len(data.get("raw_query", "")),
                "token_count": len(data.get("preprocessed_tokens", [])),
                "is_followup": data.get("is_followup", False),
                "enriched": data.get("enriched_query", "")
            },
            "pipeline": {
                "intent": data.get("intent", "UNKNOWN"),
                "confidence": data.get("confidence", 0.0),
                "tfidf_rank1": data.get("tfidf_match", {}),
                "entities": data.get("entities", {}),
                "fallback_triggered": data.get("fallback_triggered", False),
                "fallback_type": data.get("fallback_type", None),
                "consecutive_fallbacks": data.get("consecutive_fallbacks", 0)
            },
            "response": {
                "answer_faq_id": data.get("faq_id", None),
                "answer_length": len(data.get("answer", "")),
                "had_clarification": data.get("had_clarification", False),
                "had_handover": data.get("fallback_type") == "handover",
                "handover_contact": data.get("handover_contact", None),
                "ticket_id": data.get("ticket_id", None)
            },
            "feedback": {
                "thumbs_up": None,
                "thumbs_down": None,
                "user_comment": None,
                "label": None
            },
            "performance": {
                "response_time_ms": data.get("response_time_ms", 0),
                "pipeline_stages": data.get("pipeline_stages", {})
            }
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return log_id

    def update_feedback(self, log_id: str, thumbs_up: bool, comment: str = None) -> bool:
        return self._update_entry(log_id, {"thumbs_up": thumbs_up, "thumbs_down": not thumbs_up, "user_comment": comment})

    def update_label(self, log_id: str, label: str) -> bool:
        return self._update_entry(log_id, {"label": label})

    def _update_entry(self, log_id: str, updates: dict) -> bool:
        if not os.path.exists(self.log_file): return False
        
        lines = []
        updated = False
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        with open(self.log_file, "w", encoding="utf-8") as f:
            for line in lines:
                entry = json.loads(line)
                if entry["log_id"] == log_id:
                    entry["feedback"].update(updates)
                    updated = True
                f.write(json.dumps(entry) + "\n")
        return updated

    def get_recent(self, n=50) -> list:
        if not os.path.exists(self.log_file): return []
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(line) for line in reversed(lines[-n:])]
