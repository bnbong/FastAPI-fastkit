#!/usr/bin/env bash

set -e
set -x

echo "🧪 Running tests with coverage..."

# Run tests with coverage
pytest --cov=src/fastapi_fastkit --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=70

echo "✅ Coverage test completed!"
echo "📊 Coverage report saved to:"
echo "  - Terminal: above output"
echo "  - HTML: htmlcov/index.html"
echo "  - XML: coverage.xml"

# Open HTML coverage report if running on macOS and not in CI
if [[ "$OSTYPE" == "darwin"* ]] && [[ -z "$CI" ]]; then
    echo "🌐 Opening HTML coverage report in browser..."
    open htmlcov/index.html
fi
