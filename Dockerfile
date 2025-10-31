# Multi-stage Dockerfile for GeneWeb
# Stage 1: Build OCaml binaries
FROM ocaml:latest AS builder

WORKDIR /build

# Copy OCaml source
COPY . /build

# Build OCaml binaries (adjust based on your build process)
RUN opam switch create 4.14.1 && \
    eval $(opam env) && \
    opam install -y dune && \
    dune build @install

# Stage 2: Runtime environment
FROM python:3.11-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy OCaml binaries from builder stage
COPY --from=builder /build/_build/default /usr/local/bin/

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /app/logs /app/bases

# Expose port
EXPOSE 2317

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:2317/health || exit 1

# Run the application
CMD ["./gwd"]
