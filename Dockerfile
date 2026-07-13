# TythanAI Community Edition — container image
# Build:  docker build -t tythanai/community .
# Scan:   docker run --rm -v "$PWD:/src" tythanai/community scan /src
FROM python:3.12-slim

LABEL org.opencontainers.image.title="TythanAI Community Edition" \
      org.opencontainers.image.description="Offline Web3-native security scanner (SAST/SCA/Secrets/IaC/Web3)" \
      org.opencontainers.image.source="https://github.com/TythanAI/TythanAIOpen" \
      org.opencontainers.image.licenses="BUSL-1.1"

WORKDIR /app
COPY . /app

# Install the package (pulls Semgrep for extra SAST breadth; the built-in
# engine works with no network regardless).
RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 scanner

USER scanner
WORKDIR /src

ENTRYPOINT ["tythanai"]
CMD ["--help"]
