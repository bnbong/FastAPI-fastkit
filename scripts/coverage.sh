#!/usr/bin/env bash

set -e
set -x

echo "Running tests with coverage..."

# Run tests with coverage
pytest --cov=src/fastapi_fastkit --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=70

coverage_exit_code=$?

echo "Coverage test completed!"
echo "Coverage report saved to:"
echo "  - Terminal: above output"
echo "  - HTML: htmlcov/index.html"
echo "  - XML: coverage.xml"

# Open HTML coverage report if running on macOS and not in CI
if [[ "$OSTYPE" == "darwin"* ]] && [[ -z "$CI" ]]; then
    echo "Opening HTML coverage report in browser..."
    if command -v open > /dev/null 2>&1; then
        open htmlcov/index.html
    else
        echo "Note: 'open' command not available"
    fi
fi

# Exit with the same code as pytest
exit $coverage_exit_code
