FROM node:20-slim

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends time && \
    rm -rf /var/lib/apt/lists/* && \
    chown -R node:node /workspace

USER node

ENV NODE_OPTIONS="--max-old-space-size=256"

CMD ["node"]
