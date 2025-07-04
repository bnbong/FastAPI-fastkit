#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script options
OPEN_HTML=false
SHOW_MISSING=true
MIN_COVERAGE=70
OUTPUT_FORMAT="term"

# Help function
show_help() {
    echo "FastAPI-fastkit Coverage Report Generator"
    echo "========================================"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -o, --open          Open HTML report in browser (macOS only)"
    echo "  -f, --format FORMAT Output format: term, html, xml, json, all (default: term)"
    echo "  -m, --min NUM       Minimum coverage percentage (default: 70)"
    echo "  --no-missing        Don't show missing lines in terminal output"
    echo ""
    echo "Examples:"
    echo "  $0                  # Generate terminal report"
    echo "  $0 -f html -o       # Generate HTML report and open in browser"
    echo "  $0 -f all           # Generate all report formats"
    echo "  $0 -m 80            # Set minimum coverage to 80%"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -o|--open)
            OPEN_HTML=true
            shift
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -m|--min)
            MIN_COVERAGE="$2"
            shift 2
            ;;
        --no-missing)
            SHOW_MISSING=false
            shift
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_ARGS="--cov=src/fastapi_fastkit --cov-fail-under=${MIN_COVERAGE}"

# Add output formats based on selection
case $OUTPUT_FORMAT in
    "term")
        if [[ "$SHOW_MISSING" == "true" ]]; then
            PYTEST_ARGS="$PYTEST_ARGS --cov-report=term-missing"
        else
            PYTEST_ARGS="$PYTEST_ARGS --cov-report=term"
        fi
        ;;
    "html")
        PYTEST_ARGS="$PYTEST_ARGS --cov-report=html"
        OPEN_HTML=true
        ;;
    "xml")
        PYTEST_ARGS="$PYTEST_ARGS --cov-report=xml"
        ;;
    "json")
        PYTEST_ARGS="$PYTEST_ARGS --cov-report=json"
        ;;
    "all")
        if [[ "$SHOW_MISSING" == "true" ]]; then
            PYTEST_ARGS="$PYTEST_ARGS --cov-report=term-missing"
        else
            PYTEST_ARGS="$PYTEST_ARGS --cov-report=term"
        fi
        PYTEST_ARGS="$PYTEST_ARGS --cov-report=html --cov-report=xml --cov-report=json"
        ;;
    *)
        echo -e "${RED}Error: Invalid format '$OUTPUT_FORMAT'${NC}"
        echo "Valid formats: term, html, xml, json, all"
        exit 1
        ;;
esac

echo -e "${BLUE}🧪 Running coverage tests...${NC}"
echo -e "${YELLOW}Minimum coverage threshold: ${MIN_COVERAGE}%${NC}"

# Check if fastapi_project_template has changes
TEMPLATE_CHANGED=false

# Check for changes in fastapi_project_template directory
# First try to get staged files (for pre-commit), then fall back to working directory changes
if command -v git >/dev/null 2>&1; then
    # Check if we're in a git repository
    if git rev-parse --git-dir >/dev/null 2>&1; then
        # Try to get staged files first (for pre-commit hooks)
        CHANGED_FILES=$(git diff --cached --name-only 2>/dev/null || git diff --name-only HEAD~1 2>/dev/null || git diff --name-only 2>/dev/null || echo "")

        if [[ -n "$CHANGED_FILES" ]]; then
            if echo "$CHANGED_FILES" | grep -q "src/fastapi_fastkit/fastapi_project_template"; then
                TEMPLATE_CHANGED=true
            fi
        fi
    fi
fi

# Add template test exclusion if no template changes detected
if [[ "$TEMPLATE_CHANGED" == "false" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS --ignore=tests/test_templates"
    echo -e "${YELLOW}ℹ️  No changes detected in fastapi_project_template - skipping template tests${NC}"
else
    echo -e "${GREEN}ℹ️  Changes detected in fastapi_project_template - running all tests${NC}"
fi

echo ""

# Run tests with coverage
if pytest $PYTEST_ARGS; then
    echo ""
    echo -e "${GREEN}✅ Coverage test completed successfully!${NC}"

    # Show generated reports
    echo ""
    echo -e "${BLUE}📊 Generated reports:${NC}"

    if [[ "$OUTPUT_FORMAT" == "term" ]]; then
        echo "  - Terminal output above"
    elif [[ "$OUTPUT_FORMAT" == "html" ]] || [[ "$OUTPUT_FORMAT" == "all" ]]; then
        echo "  - HTML: htmlcov/index.html"
    fi

    if [[ "$OUTPUT_FORMAT" == "xml" ]] || [[ "$OUTPUT_FORMAT" == "all" ]]; then
        echo "  - XML: coverage.xml"
    fi

    if [[ "$OUTPUT_FORMAT" == "json" ]] || [[ "$OUTPUT_FORMAT" == "all" ]]; then
        echo "  - JSON: coverage.json"
    fi

    if [[ "$OUTPUT_FORMAT" == "all" ]]; then
        echo "  - Terminal output above"
        echo "  - HTML: htmlcov/index.html"
    fi

    # Open HTML report if requested
    if [[ "$OPEN_HTML" == "true" ]] && [[ "$OSTYPE" == "darwin"* ]] && [[ -z "$CI" ]]; then
        if [[ -f "htmlcov/index.html" ]]; then
            echo ""
            echo -e "${BLUE}🌐 Opening HTML coverage report in browser...${NC}"
            open htmlcov/index.html
        fi
    fi

else
    echo ""
    echo -e "${RED}❌ Coverage test failed!${NC}"
    echo -e "${YELLOW}Coverage is below the minimum threshold of ${MIN_COVERAGE}%${NC}"
    exit 1
fi
