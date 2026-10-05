FROM ghcr.io/berriai/litellm:main-latest

COPY config.yaml /app/config.yaml
COPY guardrails/ /app/guardrails/
COPY callbacks/ /app/callbacks/
ENV PYTHONPATH=/app

EXPOSE 4000

CMD ["--config", "/app/config.yaml", "--port", "4000"]
