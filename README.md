# LiteLLM Proxy PoC

A minimal, containerized LiteLLM proxy routing between **Gemini** and **Claude** under one alias (`auto`), using cost-based routing — this is the piece `llm_gateway_tutorial.ipynb` doesn't cover (it only uses the LiteLLM SDK/Router in-process, not the standalone proxy server).

## 1. Fill in `.env` (project root, one level up)

```
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
LITELLM_MASTER_KEY=sk-litellm-pick-any-secret-string
```

`LITELLM_PROXY_URL` is already defaulted to `http://localhost:4000`.

## 2. Run the proxy

**Option A — Docker (recommended, matches the ticket's "containerized instance" ask):**
```bash
cd litellm-proxy
docker compose up -d
```

**Option B — Local process:**
```bash
pip install 'litellm[proxy]'
litellm --config litellm-proxy/config.yaml --port 4000
```
(Local mode skips Redis, so cost-based routing falls back to LiteLLM's default; use Docker for the full routing-strategy demo.)

## 3. Test it

```bash
pip install openai python-dotenv
python litellm-proxy/test_proxy.py
```

This sends 10 requests to the `auto` alias and prints which underlying model (Gemini or Claude) answered each time — demonstrating cost-based routing — plus two direct-alias sanity checks.

## Notes
- `master_key` in `config.yaml` gates the proxy itself; mint per-team **virtual keys** off of it later for budgets/access control (see the ticket's Operations/Enterprise comparison rows).
- Swap `routing_strategy` in `config.yaml` to `latency-based-routing`, `least-busy`, or `usage-based-routing` to test the other strategies called out in the ticket.
