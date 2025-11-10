#!/bin/bash
# Build V3 Contract in Docker Container
# Avoids workspace dependency conflicts

set -e

echo "🐳 Building V3 Contract in Docker"
echo "=================================="
echo ""

PROJECT_DIR="/Users/jaybrantley/myenv/Hackathon/Billions_Bounty"
V3_SOURCE="programs/billions-bounty-v3"
PROGRAM_ID="ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb"
DEPLOYED_SIZE=313216

echo "📋 Configuration:"
echo "   Program ID: $PROGRAM_ID"
echo "   Source: $V3_SOURCE"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Create temporary build context
BUILD_DIR=$(mktemp -d)
echo "📦 Creating build context in: $BUILD_DIR"

# Copy V3 source files
cp -r "$PROJECT_DIR/$V3_SOURCE" "$BUILD_DIR/"
cp "$PROJECT_DIR/Cargo.toml" "$BUILD_DIR/" 2>/dev/null || true

# Remove rayon-core from dependencies
sed -i '' '/rayon-core/d' "$BUILD_DIR/$V3_SOURCE/Cargo.toml"

# Create Dockerfile
cat > "$BUILD_DIR/Dockerfile" << 'DOCKERFILE'
FROM projectserum/build:v0.28.0

# Install Solana toolchain
RUN sh -c "$(curl -sSfL https://release.solana.com/v1.18.26/install)"
ENV PATH="/root/.local/share/solana/install/active_release/bin:$PATH"

WORKDIR /workspace

# Copy source
COPY programs/billions-bounty-v3 /workspace/programs/billions-bounty-v3

# Create minimal workspace
RUN mkdir -p /workspace && \
    cat > /workspace/Cargo.toml << 'EOF'
[workspace]
members = ["programs/billions-bounty-v3"]
resolver = "2"
EOF

# Build
WORKDIR /workspace/programs/billions-bounty-v3
RUN cargo-build-sbf

# Output will be in target/deploy/
DOCKERFILE

echo "✅ Dockerfile created"

# Build Docker image
echo ""
echo "🔨 Building Docker image..."
docker build -t billions-bounty-v3-build "$BUILD_DIR" 2>&1 | tail -30

# Check if build succeeded
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    rm -rf "$BUILD_DIR"
    exit 1
fi

# Extract binary from container
echo ""
echo "📤 Extracting binary..."
CONTAINER_ID=$(docker create billions-bounty-v3-build)
OUTPUT_DIR="$PROJECT_DIR/programs/billions-bounty-v3/target/deploy"
mkdir -p "$OUTPUT_DIR"
docker cp "$CONTAINER_ID:/workspace/programs/billions-bounty-v3/target/deploy/billions_bounty_v3.so" "$OUTPUT_DIR/"
docker rm "$CONTAINER_ID"

echo "✅ Binary extracted to: $OUTPUT_DIR/billions_bounty_v3.so"

# Verification
BINARY_PATH="$OUTPUT_DIR/billions_bounty_v3.so"
if [ ! -f "$BINARY_PATH" ]; then
    echo "❌ Binary not found"
    rm -rf "$BUILD_DIR"
    exit 1
fi

echo ""
echo "🔍 CHECKPOINT 2: Verifying embedded program ID..."
if strings "$BINARY_PATH" | grep -q "$PROGRAM_ID"; then
    echo "   ✅ Correct program ID found: $PROGRAM_ID"
else
    echo "   ❌ Correct program ID NOT found"
    rm -rf "$BUILD_DIR"
    exit 1
fi

echo ""
echo "🔍 CHECKPOINT 3: Verifying binary size..."
BINARY_SIZE=$(stat -f%z "$BINARY_PATH")
SIZE_DIFF=$(( ($BINARY_SIZE - $DEPLOYED_SIZE) * 100 / $DEPLOYED_SIZE ))
echo "   Binary size: $BINARY_SIZE bytes"
echo "   Deployed size: $DEPLOYED_SIZE bytes"
echo "   Difference: ${SIZE_DIFF}%"

if [ ${SIZE_DIFF#-} -gt 10 ]; then
    echo "   ⚠️  WARNING: Size difference > 10%"
else
    echo "   ✅ Size within acceptable range"
fi

# Cleanup
rm -rf "$BUILD_DIR"

echo ""
echo "✅ Build complete! Binary ready at:"
echo "   $BINARY_PATH"
echo ""
echo "Next: Run local validator test or proceed to deployment"

