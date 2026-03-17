FROM python:3.11-slim

WORKDIR /workspace

RUN useradd -m -u 1000 runner && \
    chown -R runner:runner /workspace && \
    apt-get update && \
    apt-get install -y --no-install-recommends time && \
    rm -rf /var/lib/apt/lists/*

USER runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python3"]
