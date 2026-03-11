import argparse
import requests
import json
import time

API_URL = "http://localhost:5000"

def draw_header(channel, session_id, turn, intent):
    print(f"┌{'─'*49}┐")
    print(f"│  🤖 EduBot Pro  │  Channel: {channel:<20}│")
    print(f"├{'─'*49}┤")
    print(f"│  Session: {session_id[:8]:<8}│  Turn: {turn:<3}│  Intent: {intent:<7}│")
    print(f"└{'─'*49}┘\n")

def print_whatsapp(data):
    print("  [WhatsApp Format Simulation]")
    print("  ─────────────────────────────")
    for i, msg in enumerate(data.get("messages", [])):
        print(f"  Message {i+1} ({msg.get('type')}):")
        if msg["type"] == "text":
            print(f"  {msg['body']}\n")
        elif msg["type"] == "interactive":
            print(f"  {msg['interactive']['body']['text']}")
            btns = [b['reply']['title'] for b in msg['interactive']['action']['buttons']]
            print(f"    [{'] ['.join(btns)}]\n")
        print("  ─────────────────────────────")
        
def print_mobile(data):
    print("  [Mobile Format Simulation]")
    print(f"  Card Title: {data.get('card', {}).get('title')}")
    print(f"  Body: {data.get('card', {}).get('body')}")
    print(f"  Footer: {data.get('card', {}).get('footer')}")

def simulate(channel, compare=False):
    session_id = None
    print(f"Starting CLI Simulator for channel: {channel}. Type 'quit' to exit.")
    
    while True:
        query = input("\nYou: ")
        if query.lower() in ['quit', 'exit']:
            break
            
        payload = {"message": query, "session_id": session_id, "channel": channel}
        
        try:
            res = requests.post(f"{API_URL}/chat", json=payload)
            if res.status_code != 200:
                print(f"API Error: {res.status_code}")
                continue
                
            data = res.json()
            session_id = data.get("session_id")
            raw = data.get("bubble", {}).get("debug_panel", {}) if channel == "web" else data.get("raw", {}).get("debug", {})
            if "raw" in data: raw = data["raw"].get("debug", {})
            
            intent = payload.get("channel") # just visual
            turn = 1 # visual
            
            draw_header(channel.upper(), session_id, turn, "INTENT")
            print("  [Preprocessing]")
            if raw:
                print(f"    → Lowercased:    \"{raw.get('step1_lowercased', query)}\"")
                print(f"    → Tokens:        {raw.get('step3_tokens', [])}")
                print(f"    → Stopwords rm:  {raw.get('step4_no_stopwords', [])}")
                print(f"    → Entities:      {raw.get('entities_raw', {})}")
            print()
            
            if compare:
                # Send to all manually
                for c in ["whatsapp", "mobile", "web"]:
                    print(f"--- Channel: {c.upper()} ---")
                    r = requests.post(f"{API_URL}/chat", json={"message": query, "session_id": session_id, "channel": c}).json()
                    if c == "whatsapp": print_whatsapp(r)
                    elif c == "mobile": print_mobile(r)
                    else: print(f"  Web HTML: {r.get('bubble', {}).get('answer_html')}")
            else:
                if channel == "whatsapp":
                    print_whatsapp(data)
                elif channel == "mobile":
                    print_mobile(data)
                else:
                    print(f"  Response: {data.get('bubble', {}).get('answer_html', data.get('printable'))}")
            
        except requests.exceptions.ConnectionError:
            print("Failed to connect to Flask server. Is it running on port 5000?")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", default="cli", choices=["web", "mobile", "whatsapp", "cli"])
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    simulate(args.channel, args.compare)
