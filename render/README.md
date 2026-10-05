# LiteLLM Proxy on Render

Render builds and runs your existing Dockerfile in the cloud — you never run
`docker` on your own machine. Free tier: 750 hours/month, sleeps after 15
minutes idle, auto-wakes on the next request (no button click needed, unlike
Streamlit Community Cloud).

## 1. Already pushed — github.com/uzairalamkhan-hash/LitellmProxy

## 2. Create the service

Go to [dashboard.render.com](https://dashboard.render.com) → New → Web Service
→ connect the `LitellmProxy` repo. When asked for the **Root Directory**, enter
`render` (not the repo root — the Dockerfile and config.yaml this needs live in
that subfolder). Render will detect the Dockerfile automatically.

Alternatively: New → Blueprint, point it at the repo, and it'll pick up
`render/render.yaml` — but double check the Root Directory still resolves to
`render/` either way, since that's where `dockerfilePath: ./Dockerfile` in the
blueprint is relative to.

## 3. Set environment variables in the Render dashboard

From Upstash's "Connect" tab, TCP mode, you get one line like:
```
REDIS_URL="rediss://default:<password>@curious-colt-44838.upstash.io:6379"
```
Split that into all four of these (yes, both the combined URL and the pieces —
the routing config uses `REDIS_URL` directly since Upstash needs TLS, the
caching config uses the separate host/port/password + an explicit `ssl: true`):

```
GEMINI_API_KEY=...
GROQ_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...        # optional for now, leave blank
LITELLM_MASTER_KEY=...       # same value already in your .env
REDIS_URL=rediss://default:<password>@curious-colt-44838.upstash.io:6379
REDIS_HOST=curious-colt-44838.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=<password>    # just the password, no "default:" prefix
```

## 4. Deploy, then note the URL

Render gives you something like `https://liveramp-litellm-proxy-poc.onrender.com`.
That's what goes in the Streamlit app's sidebar as the "LiteLLM proxy URL".

## 5. Verify

```bash
curl https://liveramp-litellm-proxy-poc.onrender.com/health
```

## Note on the Dockerfile

This reuses the same `litellm`-image pattern as the Fly.io version, with the
`CMD` adjusted to read Render's dynamically assigned `$PORT` instead of a
fixed port. I haven't been able to build/test this image in this sandbox (no
general internet/Docker access here) — if the container fails to start on
first deploy, check Render's build logs for the exact `litellm` entrypoint
command the base image expects and adjust the `CMD` line accordingly.
