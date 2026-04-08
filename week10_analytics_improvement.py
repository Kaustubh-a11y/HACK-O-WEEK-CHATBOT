"""
=============================================================================
  WEEK 10 – Analytics and Continuous Improvement
  -------------------------------------------------
  Log all interactions, label a small sample, and propose improvements
  (new intents, new FAQs, better patterns) based on observed queries.
=============================================================================
"""

import re, math, json, os
from datetime import datetime
from collections import Counter

# ── Preprocessing ──
STOPWORDS = {"a","an","the","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","could","should","may","might","shall","can","need","i","me","my","we","our","you","your","it","its","this","that","these","those","what","how","when","where","who","which","tell","please","want","know","about","of","in","on","at","to","for","with","by"}
SPELL = {"fess":"fees","fie":"fees","coarse":"course","corse":"course","timin":"timing","timming":"timing","addmission":"admission","admision":"admission","scolarship":"scholarship","hosstel":"hostel","hostl":"hostel","placment":"placement","affilated":"affiliated","contcat":"contact","princpal":"principal","documnt":"document","semster":"semester","examm":"exam","timetabel":"timetable"}

class Preprocessor:
    def process(self, text):
        low = text.lower()
        np = re.sub(r'[.,!?;:\'\"()\[\]{}/\\@#$%^&*~`]', '', low)
        toks = [SPELL.get(t,t) for t in np.split() if t not in STOPWORDS]
        return {"tokens": toks, "original_lowercased": low}

# ── FAQ + TF-IDF ──
FAQ = [
    {"id":1,"q":"What are the institute timings?","a":"We are open Monday to Saturday, 8:00 AM to 6:00 PM."},
    {"id":2,"q":"What courses does the institute offer?","a":"We offer BCA, BBA, B.Sc IT, MBA, and MCA programs."},
    {"id":3,"q":"What are the admission fees?","a":"UG courses: ₹45,000/year. PG courses: ₹60,000/year."},
    {"id":4,"q":"How do I apply for admission?","a":"Visit campus or apply online at www.institute.edu.in"},
    {"id":5,"q":"What is the last date for admission?","a":"The last date for admission is 30th June 2025."},
    {"id":6,"q":"Where is the institute located?","a":"123, College Road, Nagpur, Maharashtra - 440001."},
    {"id":7,"q":"What is the contact number?","a":"Call us at +91-712-2345678 (Mon-Sat, 9AM-5PM)."},
    {"id":8,"q":"What is the email address?","a":"Email us at admissions@institute.edu.in"},
    {"id":9,"q":"Is hostel facility available?","a":"Yes! Separate hostels for boys and girls with 24/7 security."},
    {"id":10,"q":"Do you offer scholarships?","a":"Yes, merit-based and need-based scholarships are available."},
    {"id":11,"q":"What is the student teacher ratio?","a":"Our student-teacher ratio is 20:1."},
    {"id":12,"q":"What is the placement record?","a":"85%+ placement record. Top recruiters include TCS, Infosys, Wipro."},
    {"id":13,"q":"Is the institute affiliated?","a":"Yes, affiliated to RTM Nagpur University. NAAC A+ accredited."},
    {"id":14,"q":"What documents are needed?","a":"10th & 12th marksheets, ID proof, passport-size photo, TC."},
    {"id":15,"q":"How do I contact the principal?","a":"Email: principal@institute.edu.in or visit during 10AM-12PM."}
]

SYN = {"fees":["fees","fee","cost","tuition","payment","charge"],"timing":["timing","timings","time","hours","schedule","open"],"courses":["course","courses","program","degree","branch","offer"],"admission":["admission","apply","enroll","join","register"],"contact":["contact","phone","number","call","email"],"location":["location","address","located","campus"],"hostel":["hostel","accommodation","stay","dorm","room"],"scholarship":["scholarship","financial","aid","merit","grant"],"placement":["placement","job","career","recruit","company","salary"],"exam":["exam","examination","test","marks","result","paper","syllabus"],"timetable":["timetable","class","lecture","period"],"principal":["principal","director","head"],"documents":["document","documents","certificate","marksheet","proof"],"affiliation":["affiliated","university","accredited","naac"]}
T2F = {"fees":3,"timing":1,"courses":2,"admission":4,"contact":7,"location":6,"hostel":9,"scholarship":10,"placement":12,"principal":15,"documents":14,"affiliation":13,"exam":11,"timetable":11}

class TFIDFEngine:
    def __init__(self):
        self.pp=Preprocessor(); self.N=len(FAQ); self.ct=[]; self.df={}; self.cv=[]
        for d in FAQ:
            t=self.pp.process(d["q"])["tokens"]; self.ct.append(t)
            for u in set(t): self.df[u]=self.df.get(u,0)+1
        for t in self.ct:
            tf={}
            for w in t: tf[w]=tf.get(w,0)+1
            for w in tf: tf[w]/=len(t) if t else 1
            self.cv.append({w:tf[w]*math.log(self.N/(1+self.df.get(w,0))) for w in tf})
    def _cos(self,a,b):
        d=sum(a[k]*b[k] for k in a if k in b)
        na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values()))
        return d/(na*nb) if na and nb else 0
    def _topics(self,tokens):
        t=set()
        for w in tokens:
            for tp,ws in SYN.items():
                if w in ws: t.add(tp)
        return list(t)
    def retrieve(self,tokens):
        topics=self._topics(tokens); s=list(tokens)
        for t in topics: s.extend([t]*3)
        tf={}
        for w in s: tf[w]=tf.get(w,0)+1
        for w in tf: tf[w]/=len(s)
        qv={w:tf[w]*math.log(self.N/(1+self.df.get(w,0))) for w in tf}
        sc=sorted([{"d":FAQ[i],"s":self._cos(qv,self.cv[i])} for i in range(self.N)],key=lambda x:-x["s"])
        top=sc[0]; conf=min(top["s"],1.0); ans=""
        if conf<0.15 and topics:
            f=next((d for d in FAQ if d["id"]==T2F.get(topics[0])),None)
            ans=f["a"] if f else top["d"]["a"]; conf=0.9 if f else conf
        elif conf<0.15: ans="I couldn't find a match."; conf=0
        else: ans=top["d"]["a"]
        return {"answer":ans,"confidence":conf,"topics":topics,"faq_id":top["d"]["id"]}

# ── Intent ──
INTENTS = {
    "ADMISSIONS":["admission","apply","enroll","register","form","fees","document"],
    "EXAMS":["exam","test","result","marks","grade","syllabus","paper"],
    "TIMETABLE":["timetable","class","lecture","schedule","period","timing"],
    "HOSTEL":["hostel","accommodation","stay","room","dorm","mess"],
    "SCHOLARSHIPS":["scholarship","financial","aid","merit","stipend","grant"],
    "PLACEMENTS":["placement","job","career","recruit","company","salary","package"]
}

def classify(tokens):
    scores = {k:sum(1 for t in tokens if t in ws) for k,ws in INTENTS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best]>0 else "GENERAL"


# ─────────────────────────────────────────────────────────────────
# INTERACTION LOGGER – logs every chat turn to a JSONL file
# ─────────────────────────────────────────────────────────────────

LOG_DIR = "week10_logs"
LOG_FILE = os.path.join(LOG_DIR, "interactions.jsonl")


class InteractionLogger:
    """Appends each interaction as a JSON line to a log file."""

    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)

    def log(self, data: dict) -> str:
        ts = datetime.utcnow().isoformat() + "Z"
        log_id = f"LOG-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        entry = {
            "log_id": log_id,
            "timestamp": ts,
            "raw_query": data.get("raw_query", ""),
            "tokens": data.get("tokens", []),
            "intent": data.get("intent", "UNKNOWN"),
            "confidence": data.get("confidence", 0.0),
            "faq_id": data.get("faq_id"),
            "answer": data.get("answer", ""),
            "is_fallback": data.get("confidence", 1.0) < 0.15,
            "feedback": {"thumbs_up": None, "label": None}
        }

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return log_id

    def update_feedback(self, log_id: str, thumbs_up: bool, label: str = None):
        if not os.path.exists(LOG_FILE):
            return False
        lines = open(LOG_FILE, "r", encoding="utf-8").readlines()
        updated = False
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            for line in lines:
                entry = json.loads(line)
                if entry["log_id"] == log_id:
                    entry["feedback"]["thumbs_up"] = thumbs_up
                    if label:
                        entry["feedback"]["label"] = label
                    updated = True
                f.write(json.dumps(entry) + "\n")
        return updated

    def get_all(self):
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]


# ─────────────────────────────────────────────────────────────────
# ANALYTICS REPORTER – generates reports and improvement proposals
# ─────────────────────────────────────────────────────────────────

class AnalyticsReporter:
    """Analyzes logged interactions and proposes improvements."""

    def __init__(self, logger: InteractionLogger):
        self.logger = logger

    def generate_report(self) -> dict:
        logs = self.logger.get_all()
        if not logs:
            return {"message": "No interactions logged yet."}

        total = len(logs)
        avg_conf = sum(l["confidence"] for l in logs) / total
        fallbacks = sum(1 for l in logs if l["is_fallback"])
        intents = Counter(l["intent"] for l in logs)
        thumbs_up = sum(1 for l in logs if l["feedback"]["thumbs_up"] is True)
        thumbs_down = sum(1 for l in logs if l["feedback"]["thumbs_up"] is False)

        return {
            "total_interactions": total,
            "avg_confidence": round(avg_conf, 3),
            "fallback_rate": f"{fallbacks/total:.1%}",
            "intent_distribution": dict(intents),
            "feedback": {"thumbs_up": thumbs_up, "thumbs_down": thumbs_down,
                         "no_feedback": total - thumbs_up - thumbs_down}
        }

    def propose_improvements(self) -> list:
        logs = self.logger.get_all()
        proposals = []

        # Find repeated fallback queries
        fb_queries = [l["raw_query"] for l in logs if l["is_fallback"]]
        counts = Counter(fb_queries)
        for q, count in counts.items():
            if count >= 2:
                proposals.append({
                    "type": "NEW_FAQ",
                    "priority": "HIGH",
                    "evidence": f"Query '{q}' triggered fallback {count} times",
                    "proposed_question": q,
                    "proposed_answer": "[TO BE FILLED BY ADMIN]"
                })

        # Find intents with low avg confidence
        intent_conf = {}
        for l in logs:
            intent_conf.setdefault(l["intent"], []).append(l["confidence"])
        for intent, confs in intent_conf.items():
            avg = sum(confs) / len(confs)
            if avg < 0.5 and len(confs) >= 3:
                proposals.append({
                    "type": "IMPROVE_INTENT",
                    "priority": "MEDIUM",
                    "evidence": f"Intent '{intent}' has avg confidence {avg:.2%} across {len(confs)} queries",
                    "suggestion": "Add more keywords or training data"
                })

        # Suggest new intents for unmatched patterns
        general = [l["raw_query"] for l in logs if l["intent"]=="GENERAL"]
        if len(general) >= 5:
            proposals.append({
                "type": "NEW_INTENT",
                "priority": "MEDIUM",
                "evidence": f"{len(general)} queries classified as GENERAL",
                "sample_queries": general[:5],
                "suggestion": "Analyze patterns and create new intent category"
            })

        if not proposals:
            proposals.append({
                "type": "INFO",
                "priority": "LOW",
                "evidence": "System performing well, no urgent improvements needed"
            })

        return proposals


# ── CLI Loop with Analytics ──
def main():
    pp = Preprocessor()
    tfidf = TFIDFEngine()
    logger = InteractionLogger()
    reporter = AnalyticsReporter(logger)

    print("=" * 60)
    print("  📊 EduBot – Week 10: Analytics & Continuous Improvement")
    print("  Commands:")
    print("    /report     – View analytics report")
    print("    /proposals  – View improvement proposals")
    print("    /logs       – View recent interaction logs")
    print("    /feedback   – Rate the last answer (👍/👎)")
    print("    bye         – Exit")
    print("=" * 60)
    print(f"  Logs saved to: {os.path.abspath(LOG_FILE)}\n")

    last_log_id = None

    while True:
        ui = input("You: ").strip()
        if not ui:
            continue
        if ui.lower() in ["bye", "exit", "quit"]:
            print("EduBot: Goodbye! 👋\n")
            break

        # ── Special commands ──
        if ui == "/report":
            report = reporter.generate_report()
            print("\n  ╔═══ ANALYTICS REPORT ═══════════════════════════╗")
            for k, v in report.items():
                print(f"  ║  {k}: {v}")
            print("  ╚══════════════════════════════════════════════════╝\n")
            continue

        if ui == "/proposals":
            props = reporter.propose_improvements()
            print("\n  ╔═══ IMPROVEMENT PROPOSALS ══════════════════════╗")
            for i, p in enumerate(props, 1):
                print(f"  ║  {i}. [{p['priority']}] {p['type']}")
                print(f"  ║     {p['evidence']}")
            print("  ╚══════════════════════════════════════════════════╝\n")
            continue

        if ui == "/logs":
            logs = logger.get_all()[-10:]
            print(f"\n  Last {len(logs)} interactions:")
            for l in logs:
                fb = "👍" if l["feedback"]["thumbs_up"] else ("👎" if l["feedback"]["thumbs_up"] is False else "–")
                print(f"    {l['log_id']} | {l['intent']:12} | {l['confidence']:.0%} | {fb} | {l['raw_query'][:40]}")
            print()
            continue

        if ui == "/feedback":
            if not last_log_id:
                print("  No recent interaction to rate.\n")
                continue
            rating = input("  Rate last answer (y=👍 / n=👎): ").strip().lower()
            ok = logger.update_feedback(last_log_id, rating == "y")
            print(f"  {'✅ Feedback saved!' if ok else '❌ Failed to save.'}\n")
            continue

        # ── Normal query ──
        p = pp.process(ui)
        intent = classify(p["tokens"])
        r = tfidf.retrieve(p["tokens"])

        # Log interaction
        last_log_id = logger.log({
            "raw_query": ui,
            "tokens": p["tokens"],
            "intent": intent,
            "confidence": r["confidence"],
            "faq_id": r["faq_id"],
            "answer": r["answer"]
        })

        print(f"\n  Intent: {intent} | Confidence: {r['confidence']:.2%} | Log: {last_log_id}")
        print(f"\nEduBot: {r['answer']}")
        print(f"  (Type /feedback to rate this answer)\n")


if __name__ == "__main__":
    main()
