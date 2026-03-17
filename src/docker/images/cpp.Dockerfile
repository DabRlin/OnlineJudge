FROM gcc:13-bookworm

WORKDIR /workspace

RUN useradd -m -u 1000 runner && \
    chown -R runner:runner /workspace && \
    apt-get update && \
    apt-get install -y --no-install-recommends time && \
    rm -rf /var/lib/apt/lists/*

USER runner

ENV CXXFLAGS="-std=c++17 -O2 -Wall"

CMD ["g++"]
