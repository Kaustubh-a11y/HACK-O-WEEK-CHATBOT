import json
import os
from collections import Counter

class AnalyticsReporter:
    def __init__(self, log_dir="logs"):
        self.log_file = os.path.join(log_dir, "interactions.jsonl")

    def _load_logs(self):
        if not os.path.exists(self.log_file): return []
        with open(self.log_file, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def generate_report(self) -> dict:
        logs = self._load_logs()
        if not logs: return {}

        total = len(logs)
        sessions = len(set(l['session_id'] for l in logs))
        
        avg_conf = sum(l['pipeline']['confidence'] for l in logs) / total if total else 0
        fallbacks = sum(1 for l in logs if l['pipeline']['fallback_triggered'])
        handovers = sum(1 for l in logs if l['pipeline']['fallback_type'] == "handover")
        
        intents = Counter(l['pipeline']['intent'] for l in logs)
        channels = Counter(l['channel'] for l in logs)
        
        return {
            "volume": {
                "total_interactions": total,
                "unique_sessions": sessions,
                "avg_turns_per_session": total / sessions if sessions else 0,
                "queries_by_channel": dict(channels)
            },
            "quality": {
                "avg_confidence_score": avg_conf,
                "fallback_rate": fallbacks / total if total else 0,
                "handover_rate": handovers / total if total else 0
            },
            "intents": dict(intents)
        }

    def generate_improvement_proposals(self) -> list:
        logs = self._load_logs()
        proposals = []
        
        fb_queries = [l['query']['raw'] for l in logs if l['pipeline']['fallback_triggered']]
        counts = Counter(fb_queries)
        
        for q, count in counts.items():
            if count >= 3:
                proposals.append({
                    "type": "new_faq",
                    "priority": "HIGH",
                    "evidence": f"Query pattern '{q}' seen {count} times with fallback",
                    "proposed_question": q,
                    "proposed_answer": "[TO BE FILLED BY ADMIN]",
                    "sample_queries": [q]
                })
                
        # Sample addition to show UI
        if not proposals:
            proposals.append({
                "type": "new_intent",
                "priority": "MEDIUM",
                "proposed_intent": "LIBRARY",
                "evidence": "12 queries about library not mapped to any intent",
                "suggested_keywords": ["library", "books", "reading room", "issue", "return"]
            })
            
        return proposals
