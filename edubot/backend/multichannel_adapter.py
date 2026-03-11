from enum import Enum
import json

class Channel(Enum):
    WEB = "web"
    MOBILE = "mobile"
    WHATSAPP = "whatsapp"
    CLI = "cli"

class ChannelAdapter:
    """Adapts internal agnostic response to specific channel formats."""
    
    def format(self, internal_resp: dict, channel: str) -> dict:
        ch = channel.lower()
        if ch == Channel.WEB.value:
            return self.format_web(internal_resp)
        elif ch == Channel.MOBILE.value:
            return self.format_mobile(internal_resp)
        elif ch == Channel.WHATSAPP.value:
            return self.format_whatsapp(internal_resp)
        elif ch == Channel.CLI.value:
            return self.format_cli(internal_resp)
        return self.format_web(internal_resp)

    def format_web(self, resp: dict) -> dict:
        entity_tags = []
        for k, v in resp.get("entities", {}).items():
            color = "#3b82f6"
            if k == "course": color = "#10b981"
            elif k == "date": color = "#f97316"
            elif k == "year": color = "#8b5cf6"
            entity_tags.append({"type": k, "value": str(v), "color": color})
            
        return {
            "channel": "web",
            "session_id": resp.get("session_id"),
            "log_id": resp.get("log_id"),
            "bubble": {
                "intent_badge": {"label": resp.get("intent"), "color": "#f97316", "icon": "📝"},
                "confidence_bar": {"percent": int(resp.get("confidence", 0) * 100), "label": f"{int(resp.get('confidence', 0) * 100)}% match"},
                "answer_html": f"<p>{resp.get('answer', '')}</p>",
                "entity_tags": entity_tags,
                "related_chips": resp.get("related_questions", []),
                "fallback_card": resp.get("fallback"),
                "clarification_prompt": resp.get("clarification_prompt"),
                "debug_panel": resp.get("debug", {})
            },
            "quick_replies": ["Fees", "Timings", "Hostel", "Admissions", "Contact"]
        }

    def format_mobile(self, resp: dict) -> dict:
        fb = resp.get("fallback")
        msg_type = "text"
        if fb:
            msg_type = fb.get("type", "text")
            
        list_items = [{"title": f"Related: {r}", "action": "send_message"} for r in resp.get("related_questions", [])]
        
        return {
            "channel": "mobile",
            "session_id": resp.get("session_id"),
            "message_type": msg_type,
            "text": resp.get("answer", ""),
            "card": {
                "title": f"📝 {resp.get('intent', 'INFO')}",
                "subtitle": f"{int(resp.get('confidence', 0) * 100)}% match",
                "body": resp.get("answer", ""),
                "footer": "Tap for more options"
            },
            "list_items": list_items,
            "action_buttons": [
                {"label": "📞 Call Office", "type": "phone", "value": "+91-712-2345678"},
                {"label": "📧 Email Us", "type": "email", "value": "exams@institute.edu.in"},
                {"label": "🔄 Ask Another", "type": "reset", "value": None}
            ],
            "push_notification": {
                "title": "EduBot Reply",
                "body": resp.get("answer", "")[:50] + "...",
                "badge": 1
            }
        }

    def format_whatsapp(self, resp: dict) -> dict:
        import re
        ans = resp.get("answer", "")
        # Basic terminal to whatsapp markdown
        ans = re.sub(r'<[^>]+>', '', ans)
        ans = ans.replace("•", "-")
        
        prefix = resp.get("intent_prefix", "EduBot")
        body = f"*{prefix}*\n\n{ans}"
        
        fallback = resp.get("fallback")
        msgs = [{"type": "text", "body": body}]
        
        if fallback:
            if fallback["type"] == "handover":
                c = fallback["contact"]
                msgs.append({"type": "text", "body": f"Human Handover: {c['name']} - {c['phone']} / {c['email']}"})
            elif fallback["type"] == "clarification":
                btns = [{"type": "reply", "reply": {"id": f"s_{i}", "title": s[:20]}} for i, s in enumerate(fallback.get("suggestions", [])[:3])]
                msgs.append({
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": "Or choose from these:"},
                        "action": {"buttons": btns}
                    }
                })
        else:
            msgs.append({
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": "Was this helpful?"},
                    "action": {
                        "buttons": [
                            {"type":"reply","reply":{"id":"yes","title":"✅ Yes"}},
                            {"type":"reply","reply":{"id":"no", "title":"❌ No"}},
                            {"type":"reply","reply":{"id":"human","title":"👤 Talk to human"}}
                        ]
                    }
                }
            })
            
        return {
            "channel": "whatsapp",
            "session_id": resp.get("session_id"),
            "messages": msgs,
            "whatsapp_number": "whatsapp:+91-712-2345678",
            "template_name": None
        }

    def format_cli(self, resp: dict) -> dict:
        # CLI plain output formatting logic embedded
        return {
            "channel": "cli",
            "session_id": resp.get("session_id"),
            "printable": resp.get("answer", ""),
            "raw": resp
        }
