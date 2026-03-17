FROM eclipse-temurin:17-jdk-jammy

WORKDIR /workspace

RUN useradd -m -u 1000 runner && \
    chown -R runner:runner /workspace && \
    apt-get update && \
    apt-get install -y --no-install-recommends time && \
    rm -rf /var/lib/apt/lists/*

USER runner

ENV JAVA_OPTS="-Xmx256m -Xms128m"

CMD ["java"]
