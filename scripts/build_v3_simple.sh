#!/bin/bash
# Simplified V3 Build - Use projectserum/build image with Solana
# Alternative if Docker approach doesn't work

set -e

echo "🐳 Simplified Docker Build for V3"
echo "==================================="
echo ""

PROJECT_DIR="/Users/jaybrantley/myenv/Hackathon/Billions_Bounty"
V3_SOURCE="programs/billions-bounty-v3"
PROGRAM_ID="ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb"

# Create build directory
BUILD_DIR=$(mktemp -d)
cp -r "$PROJECT_DIR/$V3_SOURCE" "$BUILD_DIR/"
cp "$PROJECT_DIR/$V3_SOURCE/Cargo.toml" "$BUILD_DIR/"
sed -i '' '/rayon-core/d' "$BUILD_DIR/Cargo.toml"

# Create Dockerfile using Solana's official image
cat > "$BUILD_DIR/Dockerfile" << 'DOCKERFILE'
FROM ghcr.io/solana-labs/bpf:latest

WORKDIR /workspace
COPY . .

# Install dependencies and build
RUN cargo build-sbf --manifest-path Cargo.toml

DOCKERFILE

echo "Building with Solana BPF Docker image..."
docker build -t v3-build "$BUILD_DIR"

# Extract binary
CONTAINER_ID=$(docker create v3-build)
OUTPUT_DIR="$PROJECT_DIR/programs/billions-bounty-v3/target/deploy"
mkdir -p "$OUTPUT_DIR"
docker cp "$CONTAINER_ID:/workspace/target/deploy/billions_bounty_v3.so" "$OUTPUT_DIR/" || \
docker cp "$CONTAINER_ID:/workspace/target/sbf-solana-solana/release/billions_bounty_v3.so" "$OUTPUT_DIR/"
docker rm "$CONTAINER_ID"
rm -rf "$BUILD_DIR"

echo "✅ Build complete: $OUTPUT_DIR/billions_bounty_v3.so"

