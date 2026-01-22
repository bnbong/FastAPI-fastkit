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
import logging
import os
import subprocess
import sys
import time
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
    api_provider: str = "openai"  # openai, github, etc.
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None  # Custom API endpoint (e.g., GitHub Models)
    model_name: str = "gpt-4o-mini"  # Default model name
    create_pr: bool = True
    branch_prefix: str = "translation"
    # Rate limit handling settings
    max_retries: int = 5  # Maximum number of retries on rate limit
    retry_delay: float = 60.0  # Initial delay between retries (seconds)
    request_delay: float = 2.0  # Delay between consecutive API requests (seconds)


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
    """OpenAI API translator (compatible with GitHub Models API)."""

    # Approximate token limits for different models (conservative estimates)
    MODEL_TOKEN_LIMITS = {
        "gpt-5": 3000,  # GitHub Models gpt-5 has ~4000 limit, use 3000 for safety
        "openai/gpt-5": 3000,
        "gpt-4o": 12000,
        "openai/gpt-4o": 12000,
        "gpt-4o-mini": 12000,
        "openai/gpt-4o-mini": 12000,
    }
    DEFAULT_TOKEN_LIMIT = 3000  # Conservative default

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model_name: str = "openai/gpt-4o-mini",
        max_retries: int = 5,
        retry_delay: float = 60.0,
        request_delay: float = 2.0,
        max_chunk_chars: Optional[int] = None,
    ):
        super().__init__(api_key)
        self.base_url = base_url
        self.model_name = model_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.request_delay = request_delay
        self._client = None
        # Estimate max chars based on token limit (roughly 4 chars per token for English)
        token_limit = self.MODEL_TOKEN_LIMITS.get(model_name, self.DEFAULT_TOKEN_LIMIT)
        self.max_chunk_chars = max_chunk_chars or (
            token_limit * 3
        )  # Conservative: 3 chars per token

    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            import openai

            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url

            self._client = openai.OpenAI(**client_kwargs)
        return self._client

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if the error is a rate limit error."""
        error_str = str(error).lower()
        return any(
            keyword in error_str
            for keyword in [
                "rate limit",
                "ratelimit",
                "429",
                "too many requests",
                "quota",
            ]
        )

    def _is_payload_too_large_error(self, error: Exception) -> bool:
        """Check if the error is a payload too large error."""
        error_str = str(error).lower()
        return any(
            keyword in error_str
            for keyword in [
                "413",
                "payload too large",
                "tokens_limit_reached",
                "too large",
            ]
        )

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks that fit within token limits.

        Tries to split at natural boundaries (paragraphs, headers) to maintain context.
        """
        if len(text) <= self.max_chunk_chars:
            return [text]

        chunks = []
        current_chunk = ""

        # Split by double newlines (paragraphs) first
        paragraphs = text.split("\n\n")

        for para in paragraphs:
            # If adding this paragraph would exceed the limit
            if len(current_chunk) + len(para) + 2 > self.max_chunk_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # If a single paragraph is too large, split by lines
                if len(para) > self.max_chunk_chars:
                    lines = para.split("\n")
                    for line in lines:
                        if len(current_chunk) + len(line) + 1 > self.max_chunk_chars:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = ""

                            # If a single line is still too large, force split
                            if len(line) > self.max_chunk_chars:
                                for i in range(0, len(line), self.max_chunk_chars):
                                    chunks.append(line[i : i + self.max_chunk_chars])
                            else:
                                current_chunk = line
                        else:
                            current_chunk += ("\n" if current_chunk else "") + line
                else:
                    current_chunk = para
            else:
                current_chunk += ("\n\n" if current_chunk else "") + para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _translate_single_chunk(
        self,
        text: str,
        target_lang: str,
        source_lang: str,
        is_continuation: bool = False,
    ) -> str:
        """Translate a single chunk of text."""
        client = self._get_client()

        if is_continuation:
            # Simplified prompt for continuation chunks
            prompt = f"""Continue translating the following text to {target_lang}.
Maintain the same style and formatting as before.
IMPORTANT: Preserve all markdown formatting, code blocks, and technical terms.

Text:

{text}

Provide only the translated text without any additional commentary."""
        else:
            prompt = self.get_translation_prompt(text, target_lang, source_lang)

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = self.retry_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Rate limit hit. Waiting {wait_time:.1f}s before retry {attempt}/{self.max_retries}..."
                    )
                    time.sleep(wait_time)

                # Build API call parameters - GPT-5 doesn't support temperature
                api_params = {
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional technical documentation translator.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                }

                # Only add temperature for models that support it
                if "gpt-5" not in self.model_name.lower():
                    api_params["temperature"] = 0.3

                response = client.chat.completions.create(**api_params)

                response_content = response.choices[0].message.content
                if response_content is None:
                    return text

                time.sleep(self.request_delay)
                return response_content.strip()

            except Exception as e:
                last_error = e
                if self._is_rate_limit_error(e):
                    if attempt < self.max_retries:
                        continue
                    else:
                        logger.error(
                            f"Max retries ({self.max_retries}) exceeded due to rate limiting."
                        )
                        raise
                else:
                    raise

        if last_error:
            raise last_error
        return text

    def translate(self, text: str, target_lang: str, source_lang: str = "en") -> str:
        """Translate text, automatically chunking if necessary."""
        try:
            import openai
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            raise

        # Try direct translation first
        try:
            return self._translate_single_chunk(text, target_lang, source_lang)
        except Exception as e:
            if not self._is_payload_too_large_error(e):
                logger.error(f"Translation failed: {e}")
                raise

            # If payload too large, split into chunks and translate each
            logger.info(f"Document too large, splitting into chunks for translation...")
            chunks = self._split_text_into_chunks(text)
            logger.info(f"Split into {len(chunks)} chunks")

            translated_chunks = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Translating chunk {i + 1}/{len(chunks)}...")
                try:
                    translated = self._translate_single_chunk(
                        chunk, target_lang, source_lang, is_continuation=(i > 0)
                    )
                    translated_chunks.append(translated)
                except Exception as chunk_error:
                    logger.error(f"Failed to translate chunk {i + 1}: {chunk_error}")
                    raise

            return "\n\n".join(translated_chunks)
        return text


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

        if self.config.api_provider in ("openai", "github"):
            # For GitHub Models, set default base_url if not provided
            base_url = self.config.api_base_url
            if self.config.api_provider == "github" and not base_url:
                base_url = "https://models.github.ai/inference"

            return OpenAITranslator(
                api_key=self.config.api_key,
                base_url=base_url,
                model_name=self.config.model_name,
                max_retries=self.config.max_retries,
                retry_delay=self.config.retry_delay,
                request_delay=self.config.request_delay,
            )
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
        choices=["openai", "github"],
        default="openai",
        help="AI API provider for translation (openai or github)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for translation service. Can also be set via TRANSLATION_API_KEY (OpenAI) or GITHUB_TOKEN (GitHub) environment variable.",
    )
    parser.add_argument(
        "--api-base-url",
        type=str,
        help="Custom API base URL. Defaults to https://models.github.ai/inference for github provider.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Model name to use for translation (default: gpt-4o-mini). For GitHub, use format like 'openai/gpt-4o-mini'.",
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
    # Rate limit handling options
    parser.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Maximum number of retries on rate limit errors (default: 5)",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=60.0,
        help="Initial delay in seconds between retries (uses exponential backoff, default: 60.0)",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=2.0,
        help="Delay in seconds between consecutive API requests to avoid rate limits (default: 2.0)",
    )

    args = parser.parse_args()

    # Get API key from args or environment (support both TRANSLATION_API_KEY and GITHUB_TOKEN)
    api_key = args.api_key or os.getenv("TRANSLATION_API_KEY")
    if not api_key and args.api_provider == "github":
        api_key = os.getenv("GITHUB_TOKEN")
    if not api_key:
        env_var = (
            "GITHUB_TOKEN" if args.api_provider == "github" else "TRANSLATION_API_KEY"
        )
        logger.error(
            f"API key is required. Provide via --api-key or {env_var} environment variable."
        )
        sys.exit(1)

    # Setup configuration
    config = TranslationConfig(
        api_provider=args.api_provider,
        api_key=api_key,
        api_base_url=args.api_base_url,
        model_name=args.model,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        request_delay=args.request_delay,
        create_pr=not args.no_pr,
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
