#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh X.Y.Z"
    echo "Example: ./scripts/release.sh 3.2.0"
    exit 1
fi

echo "🔍 Preparing release $VERSION..."

# Update version in both files
echo "📝 Updating version to $VERSION..."
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" migadu_mcp/__init__.py

# Commit version changes
echo "📋 Committing version update..."
git add pyproject.toml migadu_mcp/__init__.py
git commit -m "Bump version to $VERSION"

# Create and push tag
echo "🏷️ Creating tag v$VERSION..."
git tag "v$VERSION"
git push origin master
git push --tags

echo "✅ Release preparation complete!"
echo ""
echo "📋 Next steps - Create GitHub release:"
echo "Use the GitHub CLI to create and publish the release:"
echo ""
echo "gh release create v$VERSION \\"
echo "  --title \"v$VERSION - [Add descriptive title]\" \\"
echo "  --notes \"[Add release notes describing changes]\" \\"
echo "  --latest"
echo ""
echo "Or manually at: https://github.com/Michaelzag/migadu-mcp/releases/new"
echo ""
echo "The GitHub Actions workflow will then:"
echo "- Run all quality checks (tests, linting, security)"
echo "- Build and publish to PyPI automatically"
echo "- Only publish if ALL quality checks pass"