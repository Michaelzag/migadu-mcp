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

echo "✅ All checks passed! Creating release..."
git add migadu_mcp/__init__.py pyproject.toml migadu_mcp/ .github/ scripts/ uv.lock README.md
git commit -m "v$VERSION: Release with quality checks and fixes"
git tag "v$VERSION"
git push origin master
git push --tags

echo "🎉 Build and tag $VERSION completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Create GitHub release manually at: https://github.com/Michaelzag/migadu-mcp/releases/new"
echo "2. Select tag: v$VERSION"
echo "3. Add release notes describing the changes"
echo "4. Publish the release"
echo ""
echo "Monitor the build at: https://github.com/Michaelzag/migadu-mcp/actions"