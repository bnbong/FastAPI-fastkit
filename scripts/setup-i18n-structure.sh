#!/bin/bash

# Setup i18n directory structure for FastAPI-fastkit documentation (created for legacy development environment users)
# This script moves existing English documentation to the en/ directory
# and sets up the structure for multi-language support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$PROJECT_ROOT/docs"

echo -e "${GREEN}FastAPI-fastkit i18n Structure Setup${NC}"
echo "================================================"
echo ""

# Check if docs directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo -e "${RED}Error: docs directory not found at $DOCS_DIR${NC}"
    exit 1
fi

# Create en directory if it doesn't exist
echo -e "${YELLOW}Creating en/ directory...${NC}"
mkdir -p "$DOCS_DIR/en"

# Function to move files/directories
move_to_en() {
    local item="$1"
    local item_name=$(basename "$item")

    # Skip if already in en/ or if it's a special directory
    if [[ "$item" == *"/en/"* ]] || [[ "$item_name" == "en" ]] || \
       [[ "$item_name" == "ko" ]] || [[ "$item_name" == "ja" ]] || \
       [[ "$item_name" == "zh" ]] || [[ "$item_name" == "es" ]] || \
       [[ "$item_name" == "fr" ]] || [[ "$item_name" == "de" ]] || \
       [[ "$item_name" == "css" ]] || [[ "$item_name" == "js" ]] || \
       [[ "$item_name" == "img" ]]; then
        return
    fi

    # Move markdown files and directories
    if [[ -f "$item" && "$item" == *.md ]] || [[ -d "$item" ]]; then
        local target="$DOCS_DIR/en/$item_name"

        if [ ! -e "$target" ]; then
            echo "  Moving: $item_name"
            mv "$item" "$target"
        else
            echo "  Skipping (already exists): $item_name"
        fi
    fi
}

# Move markdown files from docs root
echo ""
echo -e "${YELLOW}Moving English documentation to en/...${NC}"

for item in "$DOCS_DIR"/*; do
    move_to_en "$item"
done

# Create symbolic links for shared assets in en/ directory
echo ""
echo -e "${YELLOW}Creating symbolic links for shared assets...${NC}"

if [ -d "$DOCS_DIR/css" ]; then
    ln -sf ../css "$DOCS_DIR/en/css"
    echo "  Created: en/css -> ../css"
fi

if [ -d "$DOCS_DIR/js" ]; then
    ln -sf ../js "$DOCS_DIR/en/js"
    echo "  Created: en/js -> ../js"
fi

if [ -d "$DOCS_DIR/img" ]; then
    ln -sf ../img "$DOCS_DIR/en/img"
    echo "  Created: en/img -> ../img"
fi

# Create placeholder directories for other languages
echo ""
echo -e "${YELLOW}Creating placeholder directories for other languages...${NC}"

languages=("ko" "ja" "zh" "es" "fr" "de")

for lang in "${languages[@]}"; do
    mkdir -p "$DOCS_DIR/$lang"
    echo "  Created: $lang/"

    # Create symbolic links for assets
    if [ -d "$DOCS_DIR/css" ]; then
        ln -sf ../css "$DOCS_DIR/$lang/css"
    fi
    if [ -d "$DOCS_DIR/js" ]; then
        ln -sf ../js "$DOCS_DIR/$lang/js"
    fi
    if [ -d "$DOCS_DIR/img" ]; then
        ln -sf ../img "$DOCS_DIR/$lang/img"
    fi
done

# Create a .gitkeep file in each language directory
echo ""
echo -e "${YELLOW}Creating .gitkeep files...${NC}"

for lang in en "${languages[@]}"; do
    touch "$DOCS_DIR/$lang/.gitkeep"
    echo "  Created: $lang/.gitkeep"
done

# Print final structure
echo ""
echo -e "${GREEN}Setup Complete!${NC}"
echo ""
echo "Current documentation structure:"
tree -L 2 -d "$DOCS_DIR" 2>/dev/null || ls -la "$DOCS_DIR"

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Review the new structure in docs/"
echo "2. Update any internal links if necessary"
echo "3. Run 'mkdocs build' to test the site"
echo "4. Run 'python scripts/translate.py --target-lang ko' to create translations"
echo ""
echo -e "${YELLOW}Note: The English documentation is now in docs/en/${NC}"
echo -e "${YELLOW}      All language directories share the same css/, js/, and img/ directories${NC}"
