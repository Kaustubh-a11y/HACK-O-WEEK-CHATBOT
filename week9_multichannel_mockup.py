"""
=============================================================================
  WEEK 9 – Multichannel Deployment Mockup
  ------------------------------------------
  Plan and prototype how the chatbot would behave on web, mobile app,
  and WhatsApp. Logic simulated via console/CLI with channel-specific
  formatting.
=============================================================================
"""

import re, math
from enum import Enum

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
        related=[sc[i]["d"]["q"] for i in range(1,min(4,len(sc))) if sc[i]["s"]>0.05]
        return {"answer":ans,"confidence":conf,"topics":topics,"related":related}


# ─────────────────────────────────────────────────────────────────
# CHANNEL ADAPTER – formats responses for different platforms
# ─────────────────────────────────────────────────────────────────

class Channel(Enum):
    WEB = "web"
    MOBILE = "mobile"
    WHATSAPP = "whatsapp"
    CLI = "cli"


class ChannelAdapter:
    """Adapts internal response to platform-specific output format."""

    def format(self, answer, confidence, topics, related, channel):
        ch = channel.lower()
        if ch == "web":
            return self._web(answer, confidence, topics, related)
        elif ch == "mobile":
            return self._mobile(answer, confidence, topics, related)
        elif ch == "whatsapp":
            return self._whatsapp(answer, confidence, topics, related)
        else:
            return self._cli(answer, confidence, topics, related)

    def _web(self, answer, conf, topics, related):
        """HTML-like rich response for web browser."""
        lines = []
        lines.append("  ┌─── 🌐 WEB CHANNEL ────────────────────────────┐")
        lines.append(f"  │ Intent Badge: [{', '.join(topics) or 'GENERAL'}]")
        lines.append(f"  │ Confidence:   {'█'*int(conf*20)}{'░'*(20-int(conf*20))} {conf:.0%}")
        lines.append(f"  │")
        lines.append(f"  │ <p>{answer}</p>")
        if related:
            lines.append(f"  │")
            lines.append(f"  │ Related chips:")
            for r in related[:3]:
                lines.append(f"  │   [🔗 {r}]")
        lines.append(f"  │")
        lines.append(f"  │ Quick replies: [Fees] [Timings] [Hostel] [Contact]")
        lines.append("  └──────────────────────────────────────────────────┘")
        return "\n".join(lines)

    def _mobile(self, answer, conf, topics, related):
        """Card-based response for mobile app."""
        lines = []
        lines.append("  ┌─── 📱 MOBILE CHANNEL ─────────────────────────┐")
        lines.append(f"  │ Card Title: 📝 {', '.join(topics) or 'INFO'}")
        lines.append(f"  │ Subtitle:   {conf:.0%} match")
        lines.append(f"  │ Body:       {answer}")
        lines.append(f"  │ Footer:     Tap for more options")
        lines.append(f"  │")
        lines.append(f"  │ Action buttons:")
        lines.append(f"  │   [📞 Call Office] [📧 Email Us] [🔄 Ask Another]")
        if related:
            lines.append(f"  │ List items:")
            for r in related[:2]:
                lines.append(f"  │   → {r}")
        lines.append("  └──────────────────────────────────────────────────┘")
        return "\n".join(lines)

    def _whatsapp(self, answer, conf, topics, related):
        """WhatsApp Business API message format."""
        lines = []
        lines.append("  ┌─── 💬 WHATSAPP CHANNEL ───────────────────────┐")
        lines.append(f"  │ *EduBot* 🤖")
        lines.append(f"  │")
        lines.append(f"  │ {answer}")
        lines.append(f"  │")
        lines.append(f"  │ Was this helpful?")
        lines.append(f"  │   [✅ Yes]  [❌ No]  [👤 Talk to human]")
        if related:
            lines.append(f"  │")
            lines.append(f"  │ Or choose from these:")
            for i, r in enumerate(related[:3]):
                lines.append(f"  │   [{i+1}] {r[:30]}...")
        lines.append("  └──────────────────────────────────────────────────┘")
        return "\n".join(lines)

    def _cli(self, answer, conf, topics, related):
        """Plain text for terminal/CLI."""
        lines = []
        lines.append("  ┌─── 🖥️ CLI CHANNEL ─────────────────────────────┐")
        lines.append(f"  │ Topics: {topics}")
        lines.append(f"  │ Confidence: {conf:.2%}")
        lines.append(f"  │ Answer: {answer}")
        if related:
            for r in related[:2]:
                lines.append(f"  │ Related: {r}")
        lines.append("  └──────────────────────────────────────────────────┘")
        return "\n".join(lines)


# ── CLI Loop ──
def main():
    pp = Preprocessor()
    tfidf = TFIDFEngine()
    adapter = ChannelAdapter()

    print("=" * 60)
    print("  📡 EduBot – Week 9: Multichannel Deployment Mockup")
    print("  Simulates: Web | Mobile | WhatsApp | CLI")
    print("=" * 60)
    print()

    # Channel selection
    print("  Select channel to simulate:")
    print("    1. web")
    print("    2. mobile")
    print("    3. whatsapp")
    print("    4. cli")
    print("    5. compare (show all at once)")
    ch_input = input("  Choice [1-5]: ").strip()

    channel_map = {"1":"web","2":"mobile","3":"whatsapp","4":"cli","5":"compare"}
    channel = channel_map.get(ch_input, "cli")

    print(f"\n  ✅ Simulating channel: {channel.upper()}\n")
    print("  Type a question or 'bye' to exit.\n")

    while True:
        ui = input("You: ").strip()
        if not ui:
            continue
        if ui.lower() in ["bye","exit","quit"]:
            print("EduBot: Goodbye! 👋\n")
            break

        p = pp.process(ui)
        r = tfidf.retrieve(p["tokens"])

        if channel == "compare":
            for ch in ["web","mobile","whatsapp","cli"]:
                print(adapter.format(r["answer"],r["confidence"],r["topics"],r["related"],ch))
                print()
        else:
            print(adapter.format(r["answer"],r["confidence"],r["topics"],r["related"],channel))
            print()


if __name__ == "__main__":
    main()
