"""
EduBot Pro – Flask Backend
Serves the chatbot API for the web frontend.
Integrates all 10 weeks of functionality.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re, math, json, os, uuid, time
from datetime import datetime, timedelta
from collections import Counter
from dataclasses import dataclass

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ═══════════════════════════════════════════════════════════════
# WEEK 1 & 2: FAQ Data + Preprocessing
# ═══════════════════════════════════════════════════════════════

FAQ_CORPUS = [
    {"id":1, "q":"What are the institute timings?","a":"We are open Monday to Saturday, 8:00 AM to 6:00 PM."},
    {"id":2, "q":"What courses does the institute offer?","a":"We offer BCA, BBA, B.Sc IT, MBA, and MCA programs."},
    {"id":3, "q":"What are the admission fees?","a":"UG courses: Rs.45,000/year. PG courses: Rs.60,000/year."},
    {"id":4, "q":"How do I apply for admission?","a":"Visit campus or apply online at www.institute.edu.in"},
    {"id":5, "q":"What is the last date for admission?","a":"The last date for admission is 30th June 2025."},
    {"id":6, "q":"Where is the institute located?","a":"123, College Road, Nagpur, Maharashtra - 440001."},
    {"id":7, "q":"What is the contact number?","a":"Call us at +91-712-2345678 (Mon-Sat, 9AM-5PM)."},
    {"id":8, "q":"What is the email address?","a":"Email us at admissions@institute.edu.in"},
    {"id":9, "q":"Is hostel facility available?","a":"Yes! Separate hostels for boys and girls with 24/7 security."},
    {"id":10,"q":"Do you offer scholarships?","a":"Yes, merit-based and need-based scholarships are available."},
    {"id":11,"q":"What is the student teacher ratio?","a":"Our student-teacher ratio is 20:1."},
    {"id":12,"q":"What is the placement record?","a":"85%+ placement record. Top recruiters include TCS, Infosys, Wipro."},
    {"id":13,"q":"Is the institute affiliated to any university?","a":"Yes, affiliated to RTM Nagpur University. NAAC A+ accredited."},
    {"id":14,"q":"What documents are needed for admission?","a":"10th & 12th marksheets, ID proof, passport-size photo, TC."},
    {"id":15,"q":"How do I contact the principal?","a":"Email: principal@institute.edu.in or visit during 10AM-12PM."}
]

STOPWORDS = {"a","an","the","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","could","should","may","might","shall","can","need","i","me","my","we","our","you","your","it","its","this","that","these","those","what","how","when","where","who","which","tell","please","want","know","about","of","in","on","at","to","for","with","by"}

SPELLING_CORRECTIONS = {
    "fess":"fees","fie":"fees","coarse":"course","corse":"course",
    "timin":"timing","timming":"timing","addmission":"admission",
    "admision":"admission","scolarship":"scholarship","scholaship":"scholarship",
    "hosstel":"hostel","hostl":"hostel","placment":"placement","plcement":"placement",
    "affilated":"affiliated","contcat":"contact","princpal":"principal",
    "documnt":"document","semster":"semester","semestre":"semester",
    "examm":"exam","timetabel":"timetable","libary":"library","libraray":"library"
}

class Preprocessor:
    def process(self, text):
        lowercased = text.lower()
        no_punct = re.sub(r'[.,!?;:\'\"()\[\]{}/\\@#$%^&*~`]', '', lowercased)
        tokens = no_punct.split()
        no_stopwords = [t for t in tokens if t not in STOPWORDS]
        normalized = [SPELLING_CORRECTIONS.get(t, t) for t in no_stopwords]
        return {
            "tokens": normalized,
            "original_lowercased": lowercased,
            "debug": {
                "lowercased": lowercased,
                "no_punct": no_punct,
                "tokens": no_punct.split(),
                "no_stopwords": list(no_stopwords),
                "normalized": list(normalized)
            }
        }

# ═══════════════════════════════════════════════════════════════
# WEEK 3 & 4: Synonym Groups + TF-IDF Engine
# ═══════════════════════════════════════════════════════════════

SYNONYM_GROUPS = {
    "fees":["fees","fee","cost","costs","tuition","payment","charge","charges","price","pay","expense"],
    "timing":["timing","timings","time","times","hours","hour","schedule","open","opening","close","closing","working"],
    "courses":["course","courses","program","programs","degree","degrees","branch","stream","offer","offered","available","study"],
    "admission":["admission","admissions","apply","application","enroll","enrollment","join","register","registration","form","eligibility"],
    "contact":["contact","contacts","phone","number","call","email","mail","reach","helpline","support"],
    "location":["location","address","located","place","campus","situated","directions","map"],
    "hostel":["hostel","hostels","accommodation","stay","dormitory","dorm","room","rooms","boarding","lodge","residence"],
    "scholarship":["scholarship","scholarships","financial","aid","stipend","grant","merit","waiver","concession","fund"],
    "placement":["placement","placements","job","jobs","career","recruit","recruitment","company","hire","salary","package","lpa","ctc"],
    "exam":["exam","exams","examination","test","tests","assessment","marks","grade","result","score","paper","syllabus"],
    "timetable":["timetable","class","classes","lecture","lectures","period","routine","calendar","session"],
    "principal":["principal","director","head","hod","faculty","teacher","professor","staff"],
    "documents":["document","documents","certificate","marksheet","required","submit","proof","photo","passport"],
    "affiliation":["affiliated","affiliation","university","board","recognized","accredited","naac","ugc","aicte"]
}
TOPIC_TO_FAQ = {"fees":3,"timing":1,"courses":2,"admission":4,"contact":7,"location":6,"hostel":9,"scholarship":10,"placement":12,"principal":15,"documents":14,"affiliation":13,"exam":11,"timetable":11}

class TFIDFEngine:
    def __init__(self):
        self.pp = Preprocessor()
        self.N = len(FAQ_CORPUS)
        self.ct, self.df, self.cv = [], {}, []
        for d in FAQ_CORPUS:
            t = self.pp.process(d["q"])["tokens"]; self.ct.append(t)
            for u in set(t): self.df[u] = self.df.get(u,0)+1
        for t in self.ct:
            tf = {}
            for w in t: tf[w] = tf.get(w,0)+1
            for w in tf: tf[w] /= len(t) if t else 1
            self.cv.append({w: tf[w]*math.log(self.N/(1+self.df.get(w,0))) for w in tf})

    def _cos(self, a, b):
        d = sum(a[k]*b[k] for k in a if k in b)
        na = math.sqrt(sum(v*v for v in a.values()))
        nb = math.sqrt(sum(v*v for v in b.values()))
        return d/(na*nb) if na and nb else 0

    def _topics(self, tokens):
        t = set()
        for w in tokens:
            for tp, ws in SYNONYM_GROUPS.items():
                if w in ws: t.add(tp)
        return list(t)

    def retrieve(self, tokens):
        topics = self._topics(tokens)
        s = list(tokens)
        for t in topics: s.extend([t]*3)
        tf = {}
        for w in s: tf[w] = tf.get(w,0)+1
        for w in tf: tf[w] /= len(s)
        qv = {w: tf[w]*math.log(self.N/(1+self.df.get(w,0))) for w in tf}
        scores = sorted([{"d":FAQ_CORPUS[i],"s":self._cos(qv,self.cv[i])} for i in range(self.N)], key=lambda x:-x["s"])
        top = scores[0]; conf = min(top["s"],1.0); ans = ""
        if len(topics) > 1:
            ps = [next((d for d in FAQ_CORPUS if d["id"]==TOPIC_TO_FAQ.get(t)),None) for t in topics]
            ps = [p["a"] for p in ps if p]
            if ps: ans = " ".join(dict.fromkeys(ps)); conf = 1.0
        if not ans:
            if conf < 0.15 and topics:
                f = next((d for d in FAQ_CORPUS if d["id"]==TOPIC_TO_FAQ.get(topics[0])),None)
                ans = f["a"] if f else top["d"]["a"]; conf = 0.9 if f else conf
            elif conf < 0.15: ans = "I couldn't find a match. Please call +91-712-2345678."; conf = 0
            else: ans = top["d"]["a"]
        related = [scores[i]["d"]["q"] for i in range(1, min(4, len(scores))) if scores[i]["s"] > 0.05]
        return {"answer":ans,"confidence":conf,"matched_topics":topics,"related":related,"top_faq_id":top["d"]["id"]}

# ═══════════════════════════════════════════════════════════════
# WEEK 5: Intent Classification
# ═══════════════════════════════════════════════════════════════

INTENTS = {
    "ADMISSIONS":{"keywords":["admission","apply","application","enroll","register","join","form","eligibility","deadline","document","process","fees","seat"],"prefix":"Admissions Desk","icon":"🎓"},
    "EXAMS":{"keywords":["exam","examination","test","result","marks","grade","score","paper","syllabus","pattern","assessment"],"prefix":"Examination Cell","icon":"📝"},
    "TIMETABLE":{"keywords":["timetable","class","lecture","schedule","period","routine","timing","session","calendar","semester"],"prefix":"Academic Scheduler","icon":"📅"},
    "HOSTEL":{"keywords":["hostel","accommodation","stay","room","dorm","boarding","lodge","mess","food","warden","residence"],"prefix":"Hostel Office","icon":"🏠"},
    "SCHOLARSHIPS":{"keywords":["scholarship","financial","aid","merit","stipend","grant","waiver","concession","fund"],"prefix":"Scholarship Cell","icon":"💰"},
    "PLACEMENTS":{"keywords":["placement","job","career","recruit","company","hire","salary","package","ctc","lpa","internship"],"prefix":"Placement Cell","icon":"💼"}
}

class IntentClassifier:
    def classify(self, tokens, raw):
        scores = {k:0 for k in INTENTS}
        for t in tokens:
            for intent, data in INTENTS.items():
                if t in data["keywords"]: scores[intent] += 1
        for intent, data in INTENTS.items():
            for kw in data["keywords"]:
                if " " in kw and kw in raw: scores[intent] += 2
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return {"name":"GENERAL","prefix":"General Assistant","icon":"🤖","score":0}
        ties = sum(1 for v in scores.values() if v == scores[best])
        if ties > 1:
            return {"name":"MULTI_INTENT","prefix":"Multi-Department","icon":"🧩","score":scores[best]}
        return {"name":best,"prefix":INTENTS[best]["prefix"],"icon":INTENTS[best]["icon"],"score":scores[best]}

# ═══════════════════════════════════════════════════════════════
# WEEK 6: Entity Extraction
# ═══════════════════════════════════════════════════════════════

COURSE_ALIASES = {"cs":"Computer Science","it":"Information Technology","bca":"BCA","bba":"BBA","mba":"MBA","mca":"MCA","bsc":"B.Sc IT","commerce":"Commerce"}
WORD_TO_NUM = {"first":1,"second":2,"third":3,"fourth":4,"fifth":5,"sixth":6,"seventh":7,"eighth":8}

class EntityExtractor:
    def extract(self, query):
        e = {}; low = query.lower()
        m = re.search(r'\bsem(?:ester)?\s*[-]?\s*(\d+)\b', low)
        if not m: m = re.search(r'\b(\d+)(?:st|nd|rd|th)\s+sem(?:ester)?\b', low)
        if not m:
            m2 = re.search(r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth)\s+sem\b', low)
            if m2: e["semester"] = WORD_TO_NUM[m2.group(1)]
        if m: e["semester"] = int(m.group(1))
        for a, f in COURSE_ALIASES.items():
            if re.search(r'\b'+re.escape(a)+r'\b', low): e["course"] = f; break
        y = re.search(r'\b(first|second|third|final)\s+year\b', low)
        if y: e["year"] = y.group(0)
        elif re.search(r'\b(20\d{2})\b', low): e["year"] = re.search(r'\b(20\d{2})\b', low).group(1)
        d = re.search(r'\b(\d{1,2})[/\-.](\d{1,2})(?:[/\-.](\d{2,4}))?\b', low)
        if not d: d = re.search(r'\b(tomorrow|today|next\s+\w+|this\s+week)\b', low)
        if d: e["date"] = d.group(0)
        return e

    def enhance(self, base, ent):
        s = ent.get("semester"); c = ent.get("course"); y = ent.get("year")
        if s and c: return f"For Semester {s} {c}, {base}"
        if s: return f"Regarding Semester {s}: {base}"
        if c: return f"For {c} students: {base}"
        if y: return f"For {y} students: {base}"
        return base

# ═══════════════════════════════════════════════════════════════
# WEEK 7: Context Manager
# ═══════════════════════════════════════════════════════════════

class ConversationContext:
    def __init__(self):
        self.sessions = {}

    def _create(self, sid):
        self.sessions[sid] = {"turns":[],"active_intent":None,"active_entities":{},"last_topic":None,"last_updated":datetime.now(),"consecutive_fallbacks":0}

    def get(self, sid):
        now = datetime.now()
        expired = [k for k,v in self.sessions.items() if now-v["last_updated"]>timedelta(minutes=30)]
        for k in expired: del self.sessions[k]
        if sid not in self.sessions: self._create(sid)
        else: self.sessions[sid]["last_updated"] = now
        return self.sessions[sid]

    def is_followup(self, tokens, raw, entities):
        if len(tokens) < 6:
            if any(p in tokens for p in ["it","that","this","they","there"]): return True
            if entities and len(tokens) <= 3: return True
            for pfx in ["what about","and for","how about","same for","also","what if"]:
                if raw.lower().startswith(pfx): return True
        return False

    def resolve(self, query, ctx, new_ent):
        merged = {**ctx.get("active_entities",{}), **new_ent}
        parts = []
        if ctx["last_topic"]: parts.append(ctx["last_topic"])
        if merged.get("semester"): parts.append(f"semester {merged['semester']}")
        if merged.get("year"): parts.append(merged["year"])
        if merged.get("course"): parts.append(merged["course"])
        return " ".join(parts).strip() or query

    def update(self, sid, data):
        if sid not in self.sessions: self._create(sid)
        c = self.sessions[sid]
        c["turns"].append(data)
        if len(c["turns"]) > 5: c["turns"].pop(0)
        if data.get("intent") and data["intent"] != "GENERAL": c["active_intent"] = data["intent"]
        c["active_entities"].update(data.get("entities",{}))
        if data.get("topic"): c["last_topic"] = data["topic"]
        c["last_updated"] = datetime.now()

# ═══════════════════════════════════════════════════════════════
# WEEK 8: Fallback Handler
# ═══════════════════════════════════════════════════════════════

OUT_OF_SCOPE = ["refund","transfer","tc","leaving","rusticate","fight","complaint","legal","court","police","ragging","harassment","medical","hospital"]
HANDOVER_CONTACTS = {
    "ADMISSIONS":{"name":"Admissions Office","email":"admissions@institute.edu.in","phone":"+91-712-2345678"},
    "EXAMS":{"name":"Examination Cell","email":"exams@institute.edu.in","phone":"+91-712-2345679"},
    "HOSTEL":{"name":"Hostel Warden Office","email":"hostel@institute.edu.in","phone":"+91-712-2345680"},
    "GENERAL":{"name":"Student Help Desk","email":"helpdesk@institute.edu.in","phone":"+91-712-2345678"}
}

class FallbackHandler:
    def evaluate(self, tokens, conf, intent, consecutive=0):
        if consecutive >= 2: return ("handover","repeated_confusion")
        if any(t in OUT_OF_SCOPE for t in tokens): return ("handover","out_of_scope")
        if len(tokens)>30 or (len(tokens)>0 and sum(len(t) for t in tokens)/len(tokens)>12): return ("clarification","malformed")
        if intent in ["GENERAL","MULTI_INTENT"] and conf < 0.25: return ("clarification","no_intent")
        if len(tokens) <= 1 and conf < 0.40: return ("clarification","too_short")
        if conf < 0.15: return ("suggestion","low_confidence")
        return (None, None)

    def handle(self, raw, tokens, conf, intent, related, consecutive=0):
        fb_type, reason = self.evaluate(tokens, conf, intent, consecutive)
        if not fb_type: return None
        contact = HANDOVER_CONTACTS.get(intent, HANDOVER_CONTACTS["GENERAL"])
        if fb_type == "handover":
            return {"type":"handover","message":f"This question needs a human advisor.","contact":contact,"reason":reason}
        elif fb_type == "suggestion":
            return {"type":"suggestion","message":"I'm not confident I understood. Did you mean one of these?","suggestions":related[:3]}
        else:
            return {"type":"clarification","message":f"I'm not sure what you mean. Could you rephrase? Try: 'What are the admission fees?' or 'Is hostel available?'","suggestions":[f["q"] for f in FAQ_CORPUS[:3]]}

# ═══════════════════════════════════════════════════════════════
# WEEK 10: Analytics Logger
# ═══════════════════════════════════════════════════════════════

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "interactions.jsonl")

class InteractionLogger:
    def log(self, data):
        ts = datetime.utcnow().isoformat()+"Z"
        log_id = f"LOG-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{data.get('session_id','?')[:6]}"
        entry = {"log_id":log_id,"timestamp":ts,"session_id":data.get("session_id"),"raw_query":data.get("raw_query",""),"intent":data.get("intent","UNKNOWN"),"confidence":data.get("confidence",0),"answer":data.get("answer",""),"fallback":data.get("fallback_triggered",False),"feedback":{"thumbs_up":None}}
        with open(LOG_FILE,"a",encoding="utf-8") as f: f.write(json.dumps(entry)+"\n")
        return log_id
    def update_feedback(self, log_id, thumbs_up):
        if not os.path.exists(LOG_FILE): return False
        lines = open(LOG_FILE,"r",encoding="utf-8").readlines()
        ok = False
        with open(LOG_FILE,"w",encoding="utf-8") as f:
            for line in lines:
                e = json.loads(line)
                if e["log_id"]==log_id: e["feedback"]["thumbs_up"]=thumbs_up; ok=True
                f.write(json.dumps(e)+"\n")
        return ok
    def get_recent(self, n=50):
        if not os.path.exists(LOG_FILE): return []
        with open(LOG_FILE,"r",encoding="utf-8") as f: lines=f.readlines()
        return [json.loads(l) for l in reversed(lines[-n:])]

class AnalyticsReporter:
    def report(self):
        if not os.path.exists(LOG_FILE): return {"total":0}
        with open(LOG_FILE,"r",encoding="utf-8") as f: logs=[json.loads(l) for l in f]
        if not logs: return {"total":0}
        total=len(logs); avg_conf=sum(l["confidence"] for l in logs)/total
        intents=Counter(l["intent"] for l in logs)
        fb=sum(1 for l in logs if l["fallback"])
        return {"total":total,"avg_confidence":round(avg_conf,3),"fallback_rate":round(fb/total,3),"intents":dict(intents)}

# ═══════════════════════════════════════════════════════════════
# Initialize all modules
# ═══════════════════════════════════════════════════════════════

preprocessor = Preprocessor()
tfidf_engine = TFIDFEngine()
intent_classifier = IntentClassifier()
entity_extractor = EntityExtractor()
context_manager = ConversationContext()
fallback_handler = FallbackHandler()
logger = InteractionLogger()
reporter = AnalyticsReporter()

# ═══════════════════════════════════════════════════════════════
# Full Pipeline
# ═══════════════════════════════════════════════════════════════

def process_pipeline(message, session_id):
    start = time.time()
    ctx = context_manager.get(session_id)

    prep = preprocessor.process(message)
    tokens = prep["tokens"]
    entities = entity_extractor.extract(message)

    is_followup = context_manager.is_followup(tokens, message, entities)
    enriched = message
    if is_followup and ctx.get("last_topic"):
        enriched = context_manager.resolve(message, ctx, entities)
        prep = preprocessor.process(enriched)
        tokens = prep["tokens"]
        entities = entity_extractor.extract(enriched)

    intent = intent_classifier.classify(tokens, prep["original_lowercased"])
    tfidf = tfidf_engine.retrieve(tokens)

    fb = fallback_handler.handle(message, tokens, tfidf["confidence"], intent["name"], tfidf["related"], ctx.get("consecutive_fallbacks",0))
    if fb: ctx["consecutive_fallbacks"] = ctx.get("consecutive_fallbacks",0)+1
    else: ctx["consecutive_fallbacks"] = 0

    merged_ent = {**ctx.get("active_entities",{}), **entities}
    answer = entity_extractor.enhance(tfidf["answer"], merged_ent)

    context_manager.update(session_id, {
        "raw_query":message,"intent":intent["name"],"entities":entities,
        "topic":tfidf["matched_topics"][0] if tfidf["matched_topics"] else None
    })

    log_id = logger.log({"session_id":session_id,"raw_query":message,"intent":intent["name"],"confidence":tfidf["confidence"],"answer":answer,"fallback_triggered":fb is not None})

    elapsed = int((time.time()-start)*1000)

    return {
        "answer": answer,
        "intent": {"name":intent["name"],"prefix":intent["prefix"],"icon":intent["icon"]},
        "confidence": tfidf["confidence"],
        "entities": entities,
        "matched_topics": tfidf["matched_topics"],
        "related": tfidf["related"],
        "fallback": fb,
        "is_followup": is_followup,
        "enriched_query": enriched if is_followup else None,
        "debug": prep["debug"],
        "log_id": log_id,
        "response_time_ms": elapsed,
        "session_id": session_id
    }

# ═══════════════════════════════════════════════════════════════
# Flask Routes
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "").strip()
    sid = data.get("session_id") or str(uuid.uuid4())
    if not msg: return jsonify({"error":"Empty message"}), 400
    return jsonify(process_pipeline(msg, sid))

@app.route("/reset", methods=["POST"])
def reset():
    data = request.get_json()
    sid = data.get("session_id")
    if sid and sid in context_manager.sessions:
        del context_manager.sessions[sid]
    return jsonify({"status":"reset"})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    ok = logger.update_feedback(data.get("log_id"), data.get("thumbs_up"))
    return jsonify({"success":ok})

@app.route("/analytics", methods=["GET"])
def analytics():
    return jsonify(reporter.report())

@app.route("/analytics/logs", methods=["GET"])
def analytics_logs():
    return jsonify(logger.get_recent(int(request.args.get("limit",50))))

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","version":"4.0"})

if __name__ == "__main__":
    print("\n  EduBot Pro Server starting on http://localhost:5000")
    print("  Open index.html in your browser!\n")
    app.run(debug=True, port=5000)
