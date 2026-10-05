# LiteLLM Proxy on Fly.io — always-reachable, near-zero cost

For asynchronous testing (people trying it on their own schedule, not all at
once, possibly while your machine is off). Fly.io scales the container to zero
when idle and wakes it automatically on the next request, so you're not paying
for — or depending on — an always-on machine.

## 1. Install flyctl and log in

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

## 2. Get a free Redis endpoint (needed for cost-based routing)

Use [Upstash](https://upstash.com) (free tier, pay-per-request beyond that) —
create a Redis database, and copy the **TCP** connection details (host, port,
password) from its dashboard, not the REST URL/token pair.

## 3. Launch the app

```bash
cd litellm-proxy/fly
fly launch --no-deploy   # detects the Dockerfile, creates the app, keep the generated fly.toml close to this one
```

## 4. Set secrets (never commit these)

```bash
fly secrets set \
  ANTHROPIC_API_KEY=sk-ant-... \
  GEMINI_API_KEY=AIza... \
  LITELLM_MASTER_KEY=sk-litellm-pick-any-secret-string \
  REDIS_HOST=your-upstash-host \
  REDIS_PORT=your-upstash-port \
  REDIS_PASSWORD=your-upstash-password
```

## 5. Deploy

```bash
fly deploy
```

Fly prints a URL like `https://liveramp-litellm-proxy-poc.fly.dev`. Put that
in the webapp's "LiteLLM proxy URL" config field, mint a low-privilege virtual
key off the master key for anyone testing (don't hand out the master key
itself), and put that in the "LiteLLM virtual key" field.

## Cost expectation

With `auto_stop_machines`/`auto_start_machines` on and `min_machines_running = 0`,
you pay only for the seconds the machine is actually awake handling a request —
for intermittent PoC testing by a handful of people, this is very likely to
stay within Fly's free monthly allowance. The only recurring cost is Upstash
Redis if your request volume pushes past its free tier (unlikely for this use
case) and whatever Gemini/Claude token usage the test calls themselves incur.

## Minting a scoped virtual key (don't hand out the master key)

Once deployed, create a budget-capped key for testers instead of sharing
`LITELLM_MASTER_KEY`:

```bash
curl -X POST https://liveramp-litellm-proxy-poc.fly.dev/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"max_budget": 5, "duration": "30d"}'
```

This returns a `key` — that's what goes in the webapp, not the master key.
