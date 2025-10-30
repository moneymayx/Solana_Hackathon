#!/bin/bash
# Clean Android Studio caches and build artifacts
# Run this if Android Studio shows build errors but command line builds work

cd "$(dirname "$0")"

echo "🧹 Cleaning Android Studio caches and build artifacts..."

# Remove Android Studio caches
echo "Removing .idea/caches..."
rm -rf .idea/caches
rm -rf .idea/gradle

# Remove build directories
echo "Removing build directories..."
rm -rf app/build
rm -rf build
rm -rf .gradle

# Clean Gradle cache (optional - uncomment if needed)
# echo "Cleaning Gradle cache..."
# rm -rf ~/.gradle/caches

echo "✅ Clean complete!"
echo ""
echo "Next steps:"
echo "1. Close Android Studio completely"
echo "2. Reopen Android Studio"
echo "3. File → Sync Project with Gradle Files"
echo "4. Build → Rebuild Project"


