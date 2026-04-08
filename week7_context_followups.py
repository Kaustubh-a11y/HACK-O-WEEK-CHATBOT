"""
=============================================================================
  WEEK 7 – Context Handling for Follow-ups
  -------------------------------------------
  Enhance the chatbot to support short multi-turn conversations
  (e.g., "When is the exam?" followed by "For third year?") by
  maintaining minimal conversation state.
=============================================================================
"""

import re, math
from datetime import datetime, timedelta

# ── Preprocessing ──
STOPWORDS = {"a","an","the","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","could","should","may","might","shall","can","need","i","me","my","we","our","you","your","it","its","this","that","these","those","what","how","when","where","who","which","tell","please","want","know","about","of","in","on","at","to","for","with","by"}
SPELL = {"fess":"fees","fie":"fees","coarse":"course","corse":"course","timin":"timing","timming":"timing","addmission":"admission","admision":"admission","scolarship":"scholarship","scholaship":"scholarship","hosstel":"hostel","hostl":"hostel","placment":"placement","plcement":"placement","affilated":"affiliated","contcat":"contact","princpal":"principal","documnt":"document","semster":"semester","semestre":"semester","examm":"exam","timetabel":"timetable"}

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
        if not ans:
            if conf<0.15 and topics:
                f=next((d for d in FAQ if d["id"]==T2F.get(topics[0])),None)
                ans=f["a"] if f else top["d"]["a"]; conf=0.9 if f else conf
            elif conf<0.15: ans="I couldn't find a match."; conf=0
            else: ans=top["d"]["a"]
        return {"answer":ans,"confidence":conf,"matched_topics":topics}

# ── Entity Extractor ──
CA = {"cs":"Computer Science","it":"Information Technology","bca":"BCA","bba":"BBA","mba":"MBA","mca":"MCA","bsc":"B.Sc IT"}
W2N = {"first":1,"second":2,"third":3,"fourth":4,"fifth":5,"sixth":6,"seventh":7,"eighth":8}

class EntityExtractor:
    def extract(self, q):
        e={}; low=q.lower()
        m=re.search(r'\bsem(?:ester)?\s*[-]?\s*(\d+)\b',low)
        if not m: m=re.search(r'\b(\d+)(?:st|nd|rd|th)\s+sem(?:ester)?\b',low)
        if not m:
            m2=re.search(r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth)\s+sem\b',low)
            if m2: e["semester"]=W2N[m2.group(1)]
        if m: e["semester"]=int(m.group(1))
        for a,f in CA.items():
            if re.search(r'\b'+re.escape(a)+r'\b',low): e["course"]=f; break
        y=re.search(r'\b(first|second|third|final)\s+year\b',low)
        if y: e["year"]=y.group(0)
        elif re.search(r'\b(20\d{2})\b',low): e["year"]=re.search(r'\b(20\d{2})\b',low).group(1)
        return e
    def enhance(self, base, ent):
        s=ent.get("semester"); c=ent.get("course"); y=ent.get("year")
        if s and c: return f"For Semester {s} {c}, {base}"
        if s: return f"Regarding Semester {s}: {base}"
        if c: return f"For {c} students: {base}"
        if y: return f"For {y} students: {base}"
        return base

# ─────────────────────────────────────────────────────────────────
# CONTEXT MANAGER – multi-turn follow-up handling
# ─────────────────────────────────────────────────────────────────
class ConversationContext:
    def __init__(self):
        self.sessions = {}

    def _create(self, sid):
        self.sessions[sid] = {"turns":[],"active_intent":None,"active_entities":{},"last_topic":None,"last_updated":datetime.now()}

    def get(self, sid):
        now=datetime.now()
        for s in [k for k,v in self.sessions.items() if now-v["last_updated"]>timedelta(minutes=30)]: del self.sessions[s]
        if sid not in self.sessions: self._create(sid)
        else: self.sessions[sid]["last_updated"]=now
        return self.sessions[sid]

    def is_followup(self, tokens, raw, entities):
        if len(tokens)<6:
            if any(p in tokens for p in ["it","that","this","they","there"]): return True
            if entities and len(tokens)<=3: return True
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
        c=self.sessions[sid]; c["turns"].append(data)
        if len(c["turns"])>5: c["turns"].pop(0)
        if data.get("intent") and data["intent"]!="GENERAL": c["active_intent"]=data["intent"]
        c["active_entities"].update(data.get("entities",{}))
        if data.get("topic"): c["last_topic"]=data["topic"]
        c["last_updated"]=datetime.now()

# ── CLI Loop ──
def main():
    pp=Preprocessor(); tfidf=TFIDFEngine(); ext=EntityExtractor(); ctx=ConversationContext()
    SID="demo"
    print("="*60)
    print("  💬 EduBot – Week 7: Context Handling for Follow-ups")
    print('  Try: "When is the exam?" then "For third year?"')
    print("="*60)
    print("  Type a question or 'bye' to exit.\n")
    while True:
        ui=input("You: ").strip()
        if not ui: continue
        if ui.lower() in ["bye","exit","quit"]: print("EduBot: Goodbye! 👋\n"); break
        c=ctx.get(SID); ent=ext.extract(ui); p=pp.process(ui); tok=p["tokens"]
        fu=ctx.is_followup(tok,ui,ent); eq=ui
        if fu and c.get("last_topic"):
            eq=ctx.resolve(ui,c,ent); p=pp.process(eq); tok=p["tokens"]; ent=ext.extract(eq)
            print(f"  🔄 Follow-up detected! Enriched → \"{eq}\"")
        r=tfidf.retrieve(tok); me={**c.get("active_entities",{}),**ent}
        ans=ext.enhance(r["answer"],me)
        ctx.update(SID,{"raw_query":ui,"intent":"GENERAL","entities":ent,"topic":r["matched_topics"][0] if r["matched_topics"] else None})
        print(f"\n  Tokens: {tok}\n  Entities: {me}\n  Context: topic={c.get('last_topic')}, stored={c.get('active_entities')}\n  Follow-up: {fu}\n  Confidence: {r['confidence']:.2%}")
        print(f"\nEduBot: {ans}\n")

if __name__ == "__main__":
    main()
