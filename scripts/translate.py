#!/usr/bin/env python3
# --------------------------------------------------------------------------
# Translation automation script for FastAPI-fastkit documentation.
#
# This script handles:
# - Reading source documentation files
# - Sending translation requests to external AI APIs
# - Saving translated files to language-specific directories
# - Creating GitHub Pull Requests for review
#
# This script translate en/ directory materials to other languages.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TranslationConfig:
    """Configuration for translation process."""

    source_lang: str = "en"
    target_langs: List[str] = field(
        default_factory=lambda: ["ko", "ja", "zh", "es", "fr", "de"]
    )
    docs_dir: Path = Path(__file__).parent.parent / "docs" / source_lang
    api_provider: str = "openai"  # openai, anthropic, etc.
    api_key: Optional[str] = None
    create_pr: bool = True
    branch_prefix: str = "translation"


class TranslationAPI:
    """Base class for translation API providers."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def translate(self, text: str, target_lang: str, source_lang: str = "en") -> str:
        """Translate text to target language."""
        raise NotImplementedError("Subclass must implement translate method")

    def get_translation_prompt(
        self, text: str, target_lang: str, source_lang: str
    ) -> str:
        """Generate translation prompt for AI."""
        lang_names = {
            "en": "English",
            "ko": "Korean",
            "ja": "Japanese",
            "zh": "Chinese",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
        }

        return f"""You are a professional technical documentation translator.

Translate the following {lang_names.get(source_lang, source_lang)} documentation to {lang_names.get(target_lang, target_lang)}.

IMPORTANT RULES:
1. Preserve all markdown formatting exactly (headers, code blocks, links, etc.)
2. DO NOT translate:
   - Code snippets and command examples
   - File paths and URLs
   - Technical terms that are commonly used in English (API, CLI, FastAPI, etc.)
   - Product names and proper nouns
3. Maintain the same document structure
4. Keep the same level of technical detail
5. Use appropriate technical terminology for the target language
6. Preserve all code block language identifiers (```python, ```bash, etc.)
7. Keep all special formatting like admonitions, tables, etc.

Source text:

{text}

Provide only the translated text without any additional commentary or explanation."""


class OpenAITranslator(TranslationAPI):
    """OpenAI API translator."""

    def translate(self, text: str, target_lang: str, source_lang: str = "en") -> str:
        """Translate using OpenAI API."""
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            prompt = self.get_translation_prompt(text, target_lang, source_lang)

            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional technical documentation translator.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4096,
            )

            response_content = response.choices[0].message.content
            if response_content is None:
                return text
            return response_content.strip()
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise


class DocumentTranslator:
    """Main document translation handler."""

    def __init__(self, config: TranslationConfig):
        self.config = config
        self.translator = self._initialize_translator()

    def _initialize_translator(self) -> TranslationAPI:
        """Initialize the appropriate translation API."""
        if not self.config.api_key:
            raise ValueError(
                "API key is required. Set via --api-key or environment variable."
            )

        if self.config.api_provider == "openai":
            return OpenAITranslator(self.config.api_key)
        else:
            raise ValueError(f"Unsupported API provider: {self.config.api_provider}")

    def get_markdown_files(self, directory: Path) -> List[Path]:
        """Get all markdown files from source language directory recursively."""
        markdown_files = []
        for file_path in directory.rglob("*.md"):
            markdown_files.append(file_path)
        return markdown_files

    def translate_file(self, file_path: Path, target_lang: str) -> Tuple[str, Path]:
        """Translate a single file."""
        logger.info(f"Translating {file_path.name} to {target_lang}")

        # Read source file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Translate content
        translated_content = self.translator.translate(
            content, target_lang=target_lang, source_lang=self.config.source_lang
        )

        # Determine target path
        relative_path = file_path.relative_to(str(self.config.docs_dir))
        target_path = self.config.docs_dir.parent / target_lang / relative_path

        return translated_content, target_path

    def save_translation(self, content: str, target_path: Path) -> None:
        """Save translated content to file."""
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Saved translation to {target_path}")

    def translate_all(
        self, target_lang: str, file_paths: Optional[List[Path]] = None
    ) -> List[Path]:
        """Translate all documentation files to target language."""
        if file_paths is None:
            file_paths = self.get_markdown_files(self.config.docs_dir)

        translated_files = []

        for file_path in file_paths:
            try:
                translated_content, target_path = self.translate_file(
                    file_path, target_lang
                )
                self.save_translation(translated_content, target_path)
                translated_files.append(target_path)
            except Exception as e:
                logger.error(f"Failed to translate {file_path}: {e}")
                continue

        return translated_files

    def create_pull_request(
        self, target_lang: str, translated_files: List[Path]
    ) -> Optional[str]:
        """Create a GitHub Pull Request for translated files."""
        if not self.config.create_pr:
            return None

        branch_name = f"{self.config.branch_prefix}/{target_lang}"

        try:
            # Create new branch
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)

            # Add translated files
            for file_path in translated_files:
                subprocess.run(["git", "add", str(file_path)], check=True)

            # Commit changes
            commit_message = f"Add {target_lang} translation for documentation"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Push to remote
            subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

            # Create PR using GitHub CLI
            pr_title = f"[Translation] Add {target_lang} documentation"
            docs_root = self.config.docs_dir.parent
            pr_body = f"""## Translation Update

This PR adds {target_lang} translations for the documentation.

### Files Translated
{chr(10).join(f"- {f.relative_to(docs_root)}" for f in translated_files)}

### Translation Details
- Source Language: {self.config.source_lang}
- Target Language: {target_lang}
- API Provider: {self.config.api_provider}
- Files Count: {len(translated_files)}

Please review the translations for accuracy and consistency."""

            result = subprocess.run(
                ["gh", "pr", "create", "--title", pr_title, "--body", pr_body],
                capture_output=True,
                text=True,
                check=True,
            )

            pr_url = result.stdout.strip()
            logger.info(f"Created PR: {pr_url}")

            # Return to main branch
            subprocess.run(["git", "checkout", "main"], check=True)

            return pr_url

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create PR: {e}")
            # Try to return to main branch
            subprocess.run(["git", "checkout", "main"], check=False)
            return None


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Translate FastAPI-fastkit documentation to multiple languages"
    )
    parser.add_argument(
        "--target-lang",
        type=str,
        help="Target language code (e.g., ko, ja, zh). If not specified, translates to all configured languages.",
    )
    parser.add_argument(
        "--api-provider",
        type=str,
        choices=["openai"],
        default="openai",
        help="AI API provider for translation",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for translation service. Can also be set via TRANSLATION_API_KEY environment variable.",
    )
    parser.add_argument(
        "--no-pr", action="store_true", help="Skip creating GitHub Pull Request"
    )
    parser.add_argument(
        "--files",
        type=str,
        nargs="+",
        help="Specific files to translate (relative to docs directory)",
    )
    parser.add_argument("--docs-dir", type=str, help="Path to documentation directory")

    args = parser.parse_args()

    # Get API key from args or environment
    api_key = args.api_key or os.getenv("TRANSLATION_API_KEY")
    if not api_key:
        logger.error(
            "API key is required. Provide via --api-key or TRANSLATION_API_KEY environment variable."
        )
        sys.exit(1)

    # Setup configuration
    config = TranslationConfig(
        api_provider=args.api_provider, api_key=api_key, create_pr=not args.no_pr
    )

    if args.docs_dir:
        config.docs_dir = Path(args.docs_dir)

    # Ensure docs_dir points to source language directory
    if config.docs_dir and not str(config.docs_dir).endswith(config.source_lang):
        config.docs_dir = config.docs_dir / config.source_lang

    # Initialize translator
    translator = DocumentTranslator(config)

    # Get file paths if specified
    file_paths = None
    if args.files:
        file_paths = [config.docs_dir / f for f in args.files]
        # Verify files exist
        for fp in file_paths:
            if not fp.exists():
                logger.warning(f"File not found: {fp}")
        file_paths = [fp for fp in file_paths if fp.exists()]

    # Determine target languages
    target_langs = [args.target_lang] if args.target_lang else config.target_langs

    # Translate for each target language
    for lang in target_langs:
        logger.info(f"Starting translation to {lang}")
        translated_files = translator.translate_all(lang, file_paths)

        if translated_files:
            logger.info(
                f"Successfully translated {len(translated_files)} files to {lang}"
            )

            # Create PR if enabled
            if config.create_pr:
                pr_url = translator.create_pull_request(lang, translated_files)
                if pr_url:
                    logger.info(f"Pull request created: {pr_url}")
        else:
            logger.warning(f"No files were translated to {lang}")

    logger.info("Translation process completed!")


if __name__ == "__main__":
    main()
