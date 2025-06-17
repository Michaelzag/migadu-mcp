#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh 1.2.3"
    exit 1
fi

echo "🔍 Pre-release checks for version $VERSION..."

# Update version in both files
echo "📝 Updating version to $VERSION..."
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" migadu_mcp/__init__.py

echo "🎨 Auto-fixing code style..."
uv run ruff format .
uv run ruff check --fix .

echo "📝 Type checking..."
uv run mypy migadu_mcp/

echo "🧪 Running tests..."
uv run pytest tests/ -v

echo "🔒 Security scan..."
uv run bandit -r migadu_mcp/

echo "🧹 Cleaning build artifacts..."
rm -rf dist/ build/ *.egg-info/

echo "🏗️ Building package..."
uv build

echo "✅ All checks passed! Creating release..."
git add migadu_mcp/__init__.py pyproject.toml migadu_mcp/ .github/ scripts/ uv.lock
# Add RELEASE_NOTES.md if it exists
if [ -f "RELEASE_NOTES.md" ]; then
    git add RELEASE_NOTES.md
fi
git commit -m "v$VERSION: Release with quality checks and fixes"
git tag "v$VERSION"
git push origin master
git push --tags

echo "🚀 Creating GitHub release..."

# Check if release notes file exists
if [ -f "RELEASE_NOTES.md" ]; then
    echo "📝 Using custom release notes from RELEASE_NOTES.md"
    gh release create "v$VERSION" \
      --title "v$VERSION" \
      --notes-file "RELEASE_NOTES.md"
    rm "RELEASE_NOTES.md"  # Clean up after use
else
    echo "📝 Auto-generating release notes from commits and PRs"
    gh release create "v$VERSION" \
      --title "v$VERSION" \
      --generate-notes
fi

echo "🎉 Release $VERSION completed successfully!"
echo "Monitor the build at: https://github.com/Michaelzag/migadu-mcp/actions"
echo ""
echo "💡 Tip: For custom release notes, create RELEASE_NOTES.md before running the script"