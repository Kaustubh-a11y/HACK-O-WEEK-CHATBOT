"""
=============================================================================
  WEEK 8 – Fallbacks and Handover
  ----------------------------------
  Design a strategy for unclear or out-of-scope questions:
    - Ask clarification
    - Offer suggestions
    - Route to a human advisor (email/help desk link)
=============================================================================
"""

import re, math, random
from dataclasses import dataclass

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
    {"id":7,"q":"What is the contact number?","a":"Call us at +91-712-2345678 (Mon–Sat, 9AM–5PM)."},
    {"id":8,"q":"What is the email address?","a":"Email us at admissions@institute.edu.in"},
    {"id":9,"q":"Is hostel facility available?","a":"Yes! Separate hostels for boys and girls with 24/7 security."},
    {"id":10,"q":"Do you offer scholarships?","a":"Yes, merit-based and need-based scholarships are available."},
    {"id":11,"q":"What is the student teacher ratio?","a":"Our student-teacher ratio is 20:1."},
    {"id":12,"q":"What is the placement record?","a":"85%+ placement record. Top recruiters include TCS, Infosys, Wipro."},
    {"id":13,"q":"Is the institute affiliated?","a":"Yes, affiliated to RTM Nagpur University. NAAC A+ accredited."},
    {"id":14,"q":"What documents are needed?","a":"10th & 12th marksheets, ID proof, passport-size photo, TC."},
    {"id":15,"q":"How do I contact the principal?","a":"Email: principal@institute.edu.in or visit during 10AM–12PM."}
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
        scores=sorted([{"d":FAQ[i],"s":self._cos(qv,self.cv[i])} for i in range(self.N)],key=lambda x:-x["s"])
        top=scores[0]; conf=min(top["s"],1.0); ans=""
        if conf<0.15 and topics:
            f=next((d for d in FAQ if d["id"]==T2F.get(topics[0])),None)
            ans=f["a"] if f else top["d"]["a"]; conf=0.9 if f else conf
        elif conf<0.15: ans="I couldn't find a match."; conf=0
        else: ans=top["d"]["a"]
        related=[scores[i]["d"]["q"] for i in range(1,min(4,len(scores))) if scores[i]["s"]>0.05]
        return {"answer":ans,"confidence":conf,"matched_topics":topics,"related":related}

# ── Intent Classifier ──
INTENTS = {
    "ADMISSIONS":{"keywords":["admission","apply","enroll","register","form","fees","document","eligibility"]},
    "EXAMS":{"keywords":["exam","test","result","marks","grade","syllabus","paper","assessment"]},
    "TIMETABLE":{"keywords":["timetable","class","lecture","schedule","period","timing","semester"]},
    "HOSTEL":{"keywords":["hostel","accommodation","stay","room","dorm","mess","warden"]},
    "SCHOLARSHIPS":{"keywords":["scholarship","financial","aid","merit","stipend","grant","waiver"]},
    "PLACEMENTS":{"keywords":["placement","job","career","recruit","company","salary","package","internship"]}
}

def classify_intent(tokens, raw):
    scores = {k:0 for k in INTENTS}
    for t in tokens:
        for intent, data in INTENTS.items():
            if t in data["keywords"]: scores[intent]+=1
    best = max(scores, key=scores.get)
    return best if scores[best]>0 else "GENERAL"


# ─────────────────────────────────────────────────────────────────
# FALLBACK HANDLER
# ─────────────────────────────────────────────────────────────────

OUT_OF_SCOPE = ["refund","transfer","tc","leaving","rusticate","fight","complaint",
                "legal","court","police","ragging","harassment","politics","strike",
                "medical","hospital","accident","death"]

HANDOVER_CONTACTS = {
    "ADMISSIONS": {"name":"Admissions Office","email":"admissions@institute.edu.in","phone":"+91-712-2345678","desk":"Room 101, Admin Block","hours":"Mon–Sat, 9AM–5PM"},
    "EXAMS":      {"name":"Examination Cell","email":"exams@institute.edu.in","phone":"+91-712-2345679","desk":"Room 205, Academic Block","hours":"Mon–Fri, 10AM–4PM"},
    "HOSTEL":     {"name":"Hostel Warden Office","email":"hostel@institute.edu.in","phone":"+91-712-2345680","desk":"Hostel Admin Block","hours":"All days, 8AM–8PM"},
    "SCHOLARSHIPS":{"name":"Scholarship Cell","email":"scholarship@institute.edu.in","phone":"+91-712-2345681","desk":"Room 102, Admin Block","hours":"Mon–Fri, 10AM–3PM"},
    "GENERAL":    {"name":"Student Help Desk","email":"helpdesk@institute.edu.in","phone":"+91-712-2345678","desk":"Main Reception, Ground Floor","hours":"Mon–Sat, 8AM–6PM"}
}

@dataclass
class FallbackDecision:
    trigger: bool
    reason: str
    fallback_type: str  # "clarification", "suggestion", or "handover"
    confidence: float


class FallbackHandler:
    """Handles unclear/out-of-scope questions with 3 strategies."""

    def evaluate(self, tokens, confidence, intent, consecutive_fallbacks=0):
        # 1. Repeated confusion → handover
        if consecutive_fallbacks >= 2:
            return FallbackDecision(True, "repeated_confusion", "handover", confidence)
        # 2. Out of scope topic → handover
        if any(t in OUT_OF_SCOPE for t in tokens):
            return FallbackDecision(True, "out_of_scope_topic", "handover", confidence)
        # 3. Gibberish detection
        if len(tokens)>30 or (len(tokens)>0 and sum(len(t) for t in tokens)/len(tokens)>12):
            return FallbackDecision(True, "malformed_query", "clarification", confidence)
        # 4. Unknown intent + low confidence
        if intent in ["GENERAL","MULTI_INTENT"] and confidence < 0.25:
            return FallbackDecision(True, "no_intent_matched", "clarification", confidence)
        # 5. Very short query
        if len(tokens) <= 1 and confidence < 0.40:
            return FallbackDecision(True, "query_too_short", "clarification", confidence)
        # 6. Low TF-IDF confidence
        if confidence < 0.15:
            return FallbackDecision(True, "low_confidence", "suggestion", confidence)
        return FallbackDecision(False, "", "", confidence)

    def clarification_response(self, raw_query):
        return (f"🤔 I'm not sure what you mean by '{raw_query}'.\n"
                f"   Could you rephrase? For example, try:\n"
                f"     • 'What are the admission fees?'\n"
                f"     • 'When is the SEM 4 exam?'\n"
                f"     • 'Is hostel available?'")

    def suggestion_response(self, related):
        if related:
            lines = "   Did you mean one of these?\n"
            for i, q in enumerate(related[:3], 1):
                lines += f"     {i}. {q}\n"
            return "💡 " + lines
        return "💡 I'm not confident I understood. Please rephrase."

    def handover_response(self, raw_query, intent):
        contact = HANDOVER_CONTACTS.get(intent, HANDOVER_CONTACTS["GENERAL"])
        return (f"👤 This question needs a human advisor.\n"
                f"   📧 Email: {contact['email']}\n"
                f"   📞 Phone: {contact['phone']}\n"
                f"   🏢 Desk:  {contact['desk']} ({contact['hours']})\n"
                f"   Your query: '{raw_query}' has been noted.")

    def handle(self, raw_query, tokens, confidence, intent, related, consecutive=0):
        decision = self.evaluate(tokens, confidence, intent, consecutive)
        if not decision.trigger:
            return None, 0
        if decision.fallback_type == "handover":
            return self.handover_response(raw_query, intent), consecutive+1
        elif decision.fallback_type == "suggestion":
            return self.suggestion_response(related), consecutive+1
        else:
            return self.clarification_response(raw_query), consecutive+1


# ── CLI Loop ──
def main():
    pp=Preprocessor(); tfidf=TFIDFEngine(); fb=FallbackHandler()
    consecutive = 0
    print("="*60)
    print("  🛡️ EduBot – Week 8: Fallbacks and Handover")
    print("  Try out-of-scope queries like 'refund', gibberish,")
    print("  or very vague questions to see fallback strategies.")
    print("="*60)
    print("  Type a question or 'bye' to exit.\n")
    while True:
        ui=input("You: ").strip()
        if not ui: continue
        if ui.lower() in ["bye","exit","quit"]: print("EduBot: Goodbye! 👋\n"); break
        p=pp.process(ui); tok=p["tokens"]
        intent=classify_intent(tok, p["original_lowercased"])
        r=tfidf.retrieve(tok)
        fb_msg, consecutive = fb.handle(ui, tok, r["confidence"], intent, r["related"], consecutive)
        if fb_msg:
            print(f"\n  ⚠️  FALLBACK TRIGGERED")
            print(f"  Intent: {intent} | Confidence: {r['confidence']:.2%}")
            print(f"\n{fb_msg}\n")
        else:
            consecutive = 0
            print(f"\n  Intent: {intent} | Confidence: {r['confidence']:.2%}")
            print(f"\nEduBot: {r['answer']}\n")

if __name__ == "__main__":
    main()
