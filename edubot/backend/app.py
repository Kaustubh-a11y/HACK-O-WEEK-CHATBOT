from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
import time
from datetime import datetime

from preprocessor import Preprocessor
from tfidf_engine import TFIDFEngine
from intent_classifier import IntentClassifier
from entity_extractor import EntityExtractor
from context_manager import ConversationContext
from fallback_handler import FallbackHandler
from multichannel_adapter import ChannelAdapter, Channel
from analytics_logger import InteractionLogger
from analytics_reporter import AnalyticsReporter 
from faq_data import FAQ_CORPUS

app = Flask(__name__)
CORS(app)

preprocessor = Preprocessor()
tfidf_engine = TFIDFEngine()
intent_classifier = IntentClassifier()
entity_extractor = EntityExtractor()
context_manager = ConversationContext()
fallback_handler = FallbackHandler()
channel_adapter = ChannelAdapter()
analytics_logger = InteractionLogger()
analytics_reporter = AnalyticsReporter()

def process_pipeline(message, session_id, channel):
    start_time = time.time()
    context = context_manager.get_context(session_id)
    
    # Preprocess
    prep = preprocessor.process(message)
    tokens = prep['tokens']
    
    # Entity Extraction
    entities = entity_extractor.extract(message)
    
    # Context resolution
    is_followup = context_manager.is_followup(tokens, message, entities)
    enriched_query = message
    if is_followup and context.get("last_topic"):
        enriched_query = context_manager.resolve(message, context, entities)
        prep = preprocessor.process(enriched_query)
        tokens = prep['tokens']
        entities = entity_extractor.extract(enriched_query)
        
    # Classify & Retrieve
    intent_res = intent_classifier.classify(tokens, prep['original_lowercased'])
    tfidf_res = tfidf_engine.retrieve(tokens)
    
    # Fallback Handling
    pipeline_res = {
        "raw_query": message,
        "tokens": tokens,
        "intent": intent_res['name'],
        "confidence": tfidf_res['confidence'],
        "tfidf_result": tfidf_res
    }
    fb_result = fallback_handler.handle(pipeline_res, context, FAQ_CORPUS)
    
    # Answer Formulation
    base_answer = tfidf_res['answer']
    merged_entities = {**context.get("active_entities", {}), **entities}
    enhanced_answer = entity_extractor.answer_enhancer(base_answer, merged_entities)
    
    needs_clarification = []
    if intent_res['name'] in ["EXAMS", "TIMETABLE"]:
        if "semester" not in merged_entities:
            needs_clarification.append("semester")
        elif "course" not in merged_entities:
            needs_clarification.append("course")
            
    internal_resp = {
        "session_id": session_id,
        "answer": enhanced_answer,
        "intent": intent_res['name'],
        "intent_prefix": intent_res['prefix'],
        "confidence": tfidf_res['confidence'],
        "entities": entities,
        "fallback": fb_result.get("data") if fb_result.get("triggered") else None,
        "related_questions": tfidf_res['related'],
        "clarification_prompt": context_manager.clarification_prompt(needs_clarification[0]) if needs_clarification else None,
        "debug": {
            "step1_lowercased": prep['debug']['lowercased'],
            "step2_no_punct": prep['debug']['no_punct'],
            "step3_tokens": prep['debug']['tokens'],
            "step4_no_stopwords": prep['debug']['no_stopwords'],
            "step5_normalized": prep['debug']['normalized'],
            "entities_raw": entities,
            "context_active_intent": context.get("active_intent"),
            "context_active_entities": context.get("active_entities")
        }
    }
    
    # Format according to channel
    formatted = channel_adapter.format(internal_resp, channel)
    
    # Analytics logging
    elapsed = int((time.time() - start_time) * 1000)
    log_data = {
        "session_id": session_id,
        "turn_number": len(context.get('turns', [])) + 1,
        "channel": channel,
        "raw_query": message,
        "preprocessed_tokens": tokens,
        "is_followup": is_followup,
        "enriched_query": enriched_query,
        "intent": intent_res['name'],
        "confidence": tfidf_res['confidence'],
        "tfidf_match": tfidf_res['top_match'],
        "entities": entities,
        "fallback_triggered": fb_result.get("triggered"),
        "fallback_type": fb_result.get("data", {}).get("type") if fb_result.get("triggered") else None,
        "consecutive_fallbacks": context.get("consecutive_fallbacks", 0),
        "faq_id": tfidf_res['top_match']['faq_id'],
        "answer": enhanced_answer,
        "response_time_ms": elapsed
    }
    
    if fb_result.get("triggered") and fb_result.get("data", {}).get("type") == "handover":
        log_data["handover_contact"] = fb_result["data"]["contact"]
        log_data["ticket_id"] = fb_result["data"]["ticket_id"]
        
    log_id = analytics_logger.log(log_data)
    
    # Update Context
    turn_data = {
        "raw_query": message, "intent": intent_res['name'],
        "entities": entities, "topic": tfidf_res['matched_topics'][0] if tfidf_res['matched_topics'] else None
    }
    context_manager.update(session_id, turn_data, needs_clarification)
    
    formatted['log_id'] = log_id
    formatted['is_followup'] = is_followup
    formatted['enriched_query'] = enriched_query
    formatted['turns_count'] = len(context.get('turns', [])) + 1
    
    return formatted

@app.route('/chat', methods=['POST'])
@app.route('/chat/web', methods=['POST'])
def chat_web():
    data = request.get_json()
    return jsonify(process_pipeline(data.get('message', ''), data.get('session_id') or str(uuid.uuid4()), Channel.WEB.value))

@app.route('/chat/mobile', methods=['POST'])
def chat_mobile():
    data = request.get_json()
    return jsonify(process_pipeline(data.get('message', ''), data.get('session_id') or str(uuid.uuid4()), Channel.MOBILE.value))

@app.route('/chat/whatsapp', methods=['POST'])
def chat_whatsapp():
    data = request.get_json()
    return jsonify(process_pipeline(data.get('message', ''), data.get('session_id') or str(uuid.uuid4()), Channel.WHATSAPP.value))

@app.route('/reset', methods=['POST'])
def reset_session():
    data = request.get_json()
    if data.get('session_id'): context_manager.reset_session(data['session_id'])
    return jsonify({"status": "Session reset"})

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    success = analytics_logger.update_feedback(data.get('log_id'), data.get('thumbs_up'), data.get('comment'))
    return jsonify({"success": success})

@app.route('/label', methods=['POST'])
def label():
    data = request.get_json()
    success = analytics_logger.update_label(data.get('log_id'), data.get('label'))
    return jsonify({"success": success})

@app.route('/analytics/report', methods=['GET'])
def get_analytics_report():
    return jsonify(analytics_reporter.generate_report())

@app.route('/analytics/proposals', methods=['GET'])
def get_analytics_proposals():
    return jsonify(analytics_reporter.generate_improvement_proposals())

@app.route('/analytics/logs', methods=['GET'])
def get_analytics_logs():
    return jsonify(analytics_logger.get_recent(int(request.args.get('limit', 50))))

@app.route('/analytics/export', methods=['GET'])
def export_logs():
    return send_file('logs/interactions.jsonl', as_attachment=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "version": "3.0"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
