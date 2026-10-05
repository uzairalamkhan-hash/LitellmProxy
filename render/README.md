# LiteLLM Proxy on Render

Render builds and runs your existing Dockerfile in the cloud — you never run
`docker` on your own machine. Free tier: 750 hours/month, sleeps after 15
minutes idle, auto-wakes on the next request (no button click needed, unlike
Streamlit Community Cloud).

## 1. Push this repo to GitHub (Render deploys from a repo, not a local file)

## 2. Create the service

Either click "New + → Blueprint" in the Render dashboard and point it at this
repo (it'll read `render.yaml` automatically), or "New + → Web Service →
Docker" and point the root/dockerfile path at `litellm-proxy/render/`.

## 3. Set environment variables in the Render dashboard

```
GEMINI_API_KEY=...
GROQ_API_KEY=...
ANTHROPIC_API_KEY=...        # optional for now
LITELLM_MASTER_KEY=...       # already generated in your .env
REDIS_HOST=...               # Upstash TCP host (needed for cost-based routing)
REDIS_PORT=...
REDIS_PASSWORD=...
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
