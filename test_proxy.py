"""
Test script for the LiteLLM proxy PoC.

Run the proxy first (either):
  A) Docker:  cd litellm-proxy && docker compose up -d
  B) Local:   pip install 'litellm[proxy]' && litellm --config litellm-proxy/config.yaml --port 4000

Then, from the project root (with the same .env loaded):
  python litellm-proxy/test_proxy.py
"""
import os
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")

client = OpenAI(base_url=PROXY_URL, api_key=MASTER_KEY)

prompt = "Say 'OK' and nothing else."

print(f"Sending 10 requests to '{PROXY_URL}' model='auto' (cost-based routing)...\n")

hits = Counter()
for i in range(10):
    r = client.chat.completions.create(
        model="auto",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5,
    )
    routed_id = r._hidden_params.get("model_id", r.model) if hasattr(r, "_hidden_params") else r.model
    hits[routed_id] += 1
    print(f"Request {i+1:>2}: routed to {r.model}")

print("\nRouting distribution (should favor the cheaper model over time):")
for model_id, count in hits.most_common():
    print(f"  {model_id}: {count}/10")

# Direct-alias sanity checks (bypass routing, hit a specific model)
# claude-direct will 401 until ANTHROPIC_API_KEY is added to .env — expected for now.
for alias in ("gemini-direct", "groq-direct", "claude-direct"):
    try:
        r = client.chat.completions.create(
            model=alias,
            messages=[{"role": "user", "content": "Reply with your model family in one word."}],
            max_tokens=5,
        )
        print(f"\n[{alias}] -> {r.choices[0].message.content} (model={r.model})")
    except Exception as e:
        print(f"\n[{alias}] -> ❌ {type(e).__name__}: {e}")
