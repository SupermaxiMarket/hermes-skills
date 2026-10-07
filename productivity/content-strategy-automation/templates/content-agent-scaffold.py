"""
Template pour construire un agent de stratégie de contenu 24/7.
À copier et modifier selon les besoins.
Structure:
  - analyzer.py   → analyse + scoring
  - ideas.py      → génération d'idées avec fallback
  - server.py     → dashboard FastAPI
  - cron_run.py   → script cron 3 phases
"""

ANALYZER_TEMPLATE = '''#!/usr/bin/env python3
"""
Content Analyzer — analyse les performances et calcule le heat score
"""
import json, os, time
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@dataclass
class ContentItem:
    id: str
    title: str
    platform: str = "youtube"
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    published_at: str = ""
    collected_at: str = ""
    url: str = ""
    velocity: float = 0.0
    heat_score: float = 0.0
    engagement_rate: float = 0.0

def calculate_heat_score(item: ContentItem) -> ContentItem:
    """Heat score = (views_norm × 0.4 + engagement_norm × 0.6) × velocity_bonus"""
    now = datetime.now(timezone.utc)
    days_since = 1
    if item.published_at:
        try:
            pub = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
            days_since = max(1, (now - pub).days)
        except:
            pass
    
    item.velocity = item.views / days_since
    views_norm = min((min(item.views, 1_000_000) / 10000) ** 0.5 / 10 * 100, 100)
    engagement_total = item.likes + item.comments * 2 + item.shares * 3
    item.engagement_rate = (engagement_total / max(item.views, 1)) * 100
    engagement_norm = min(item.engagement_rate * 10, 100)
    velocity_factor = min(item.velocity / 100, 5)
    item.heat_score = round(min((views_norm * 0.4 + engagement_norm * 0.6) * (1 + velocity_factor * 0.1), 100), 1)
    return item

def generate_sample_data() -> list:
    """Replace with real data source"""
    from datetime import timedelta
    samples = [
        {"title": "Sample 1", "views": 15000, "likes": 800, "comments": 100, "shares": 200, "days_ago": 3},
        {"title": "Sample 2", "views": 40000, "likes": 2400, "comments": 350, "shares": 500, "days_ago": 7},
    ]
    items = []
    now = datetime.now(timezone.utc)
    for i, s in enumerate(samples):
        pub = now - timedelta(days=s["days_ago"])
        item = ContentItem(id=f"s_{i}", title=s["title"], platform="youtube",
            views=s["views"], likes=s["likes"], comments=s["comments"], shares=s["shares"],
            published_at=pub.isoformat(), collected_at=now.isoformat())
        items.append(calculate_heat_score(item))
    return items

def save_analysis(items):
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {"analyzed_at": datetime.now(timezone.utc).isoformat(), "total_items": len(items),
            "items": [asdict(i) for i in items]}
    with open(os.path.join(DATA_DIR, "latest_analysis.json"), "w") as f:
        json.dump(data, f, indent=2)
    winners = sorted(items, key=lambda x: x.heat_score, reverse=True)
    with open(os.path.join(DATA_DIR, "winners.json"), "w") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                    "winners": [asdict(w) for w in winners]}, f, indent=2)

if __name__ == "__main__":
    items = generate_sample_data()
    save_analysis(items)
    winners = sorted(items, key=lambda x: x.heat_score, reverse=True)
    for w in winners[:3]:
        print(f"  🔥 {w.heat_score} — {w.title} ({w.views:,} vues, {w.velocity:.0f}/jour)")
'''

IDEAS_TEMPLATE = '''#!/usr/bin/env python3
"""
Idea Generator — génère des idées à partir des winners
Toujours avec fallback template si LLM indisponible
"""
import json, os, re, time
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_winners():
    path = os.path.join(DATA_DIR, "winners.json")
    if not os.path.exists(path): return []
    with open(path) as f: return json.load(f).get("winners", [])

def save_ideas(ideas):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "ideas.json"), "w") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                    "total_ideas": len(ideas), "ideas": ideas}, f, indent=2)

def generate_ideas(winners, count=5):
    # Always build fallback first
    fallback = _fallback_ideas(winners, count)
    
    # Try LLM if configured (short timeout)
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if api_key and len(api_key) > 10:
        try:
            import requests
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user",
                    "content": f"Generate {count} content ideas based on: {[w['title'] for w in winners[:3]]}. Return JSON array."}],
                    "temperature": 0.8, "max_tokens": 2000}, timeout=8)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                import re
                jm = re.search(r'\\[.*?\\]', content, re.DOTALL)
                if jm:
                    llm = json.loads(jm.group(0))
                    for i, idea in enumerate(llm[:count]):
                        fb = fallback[i] if i < len(fallback) else {}
                        for k in ["format", "reasoning", "predictions"]:
                            if k not in idea or not idea.get(k): idea[k] = fb.get(k, "")
                    return llm[:count]
        except: pass
    
    return fallback

def _fallback_ideas(winners, count=5):
    formats = ["tutoriel", "comparaison", "liste", "storytelling"]
    hooks = [
        "Tu fais encore X manuellement ? Voici comment l'automatiser",
        "X vs Y : lequel choisir en 2026 ?",
        "TOP 10 des outils X qui vont changer votre workflow",
        "J'ai perdu 3 mois à cause de X — voici ce que j'ai appris",
    ]
    topics = ["les agents IA", "l'automatisation", "les LLMs locaux", "le déploiement d'apps IA"]
    if winners:
        wt = []
        for w in winners[:3]:
            words = w.get("title", "").lower().split()
            wt.append(" ".join(words[1:4]) if len(words) > 3 else w.get("title", ""))
        topics = wt + topics
    
    ideas = []
    for i in range(min(count, 8)):
        f = formats[i % len(formats)]
        topic = topics[i % len(topics)]
        ideas.append({
            "id": f"idea_{int(time.time())}_{i}",
            "title": f"Comment {topic} va changer votre façon de travailler",
            "hook": hooks[i % len(hooks)].replace("X", topic),
            "format": f,
            "reasoning": f"Format '{f}' performe bien avec votre audience.",
            "based_on": winners[i % len(winners)]["title"] if winners and i < len(winners) else "Tendances",
            "score": round(90 - i * 5, 1),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "predictions": {"expected_views": "haute" if i < 2 else "moyenne",
                "engagement_potential": "viral" if i < 2 else "high" if i < 4 else "medium"},
        })
    return ideas

if __name__ == "__main__":
    winners = load_winners()
    ideas = generate_ideas(winners)
    save_ideas(ideas)
    for idea in ideas:
        print(f"  {idea['title']} (⭐ {idea['score']})")
'''

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if action == "scaffold":
        import os
        base = sys.argv[2] if len(sys.argv) > 2 else "./content-agent"
        os.makedirs(f"{base}/data", exist_ok=True)
        os.makedirs(f"{base}/templates", exist_ok=True)
        
        with open(f"{base}/analyzer.py", "w") as f:
            f.write(ANALYZER_TEMPLATE)
        with open(f"{base}/ideas.py", "w") as f:
            f.write(IDEAS_TEMPLATE)
        
        print(f"✅ Scaffolded content agent at {base}/")
        print(f"   Edit analyzer.py with your data source, then:")
        print(f"   python3 {base}/analyzer.py && python3 {base}/ideas.py")
    else:
        print("Usage: python3 scaffold.py scaffold ./my-content-agent")