FROM ghcr.io/berriai/litellm:main-latest

COPY config.yaml /app/config.yaml
COPY guardrails/ /app/guardrails/
COPY callbacks/ /app/callbacks/
ENV PYTHONPATH=/app

EXPOSE 4000

# Render injects $PORT at runtime (not always 4000) — expand it via shell form.
ENTRYPOINT []
CMD ["sh", "-c", "litellm --config /app/config.yaml --port ${PORT:-4000}"]
