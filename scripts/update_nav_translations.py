#!/usr/bin/env python3
# --------------------------------------------------------------------------
# Update navigation translations in mkdocs.yml automatically.
#
# This script reads navigation items from mkdocs.yml and generates translations
# for all configured languages using AI translation APIs.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, List

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_nav_items(nav_config: List[Any]) -> List[str]:
    """Extract all navigation item titles from nav configuration."""
    items = []

    def extract_recursive(nav_item: Any) -> None:
        if isinstance(nav_item, dict):
            for key, value in nav_item.items():
                items.append(key)
                if isinstance(value, list):
                    for sub_item in value:
                        extract_recursive(sub_item)
        elif isinstance(nav_item, str):
            items.append(nav_item)

    for item in nav_config:
        extract_recursive(item)

    return items


def translate_nav_item(
    text: str, target_lang: str, api_key: str = "", provider: str = "openai"
) -> str:
    """Translate a navigation item to target language."""
    # Language-specific translations (add more as needed)
    translations = {
        "ko": {
            "Home": "홈",
            "User Guide": "사용자 가이드",
            "Installation": "설치",
            "Quick Start": "빠른 시작",
            "Creating Projects": "프로젝트 생성",
            "Adding Routes": "라우트 추가",
            "Using Templates": "템플릿 사용",
            "CLI Reference": "CLI 레퍼런스",
            "Tutorial": "튜토리얼",
            "Getting Started": "시작하기",
            "Your First Project": "첫 번째 프로젝트",
            "Implementing Basic API Server": "기본 API 서버 구현",
            "Implementing Asynchronous CRUD API": "비동기 CRUD API 구현",
            "Database Integration": "데이터베이스 통합",
            "Docker Deployment": "Docker 배포",
            "Implementing Custom Response Handling": "커스텀 응답 처리 구현",
            "Implementing MCP Server": "MCP 서버 구현",
            "Contributing": "기여하기",
            "Development Setup": "개발 환경 설정",
            "Code Guidelines": "코드 가이드라인",
            "Template Creation Guide": "템플릿 생성 가이드",
            "Translation Guide": "번역 가이드",
            "Reference": "레퍼런스",
            "FAQ": "자주 묻는 질문",
            "Template Quality Assurance": "템플릿 품질 보증",
            "Changelog": "변경 로그",
        },
        "ja": {
            "Home": "ホーム",
            "User Guide": "ユーザーガイド",
            "Tutorial": "チュートリアル",
            "Contributing": "貢献",
            "Reference": "リファレンス",
            "Changelog": "変更履歴",
        },
        "zh": {
            "Home": "首页",
            "User Guide": "用户指南",
            "Tutorial": "教程",
            "Contributing": "贡献",
            "Reference": "参考",
            "Changelog": "更新日志",
        },
        "es": {
            "Home": "Inicio",
            "User Guide": "Guía del Usuario",
            "Tutorial": "Tutorial",
            "Contributing": "Contribuir",
            "Reference": "Referencia",
            "Changelog": "Registro de Cambios",
        },
        "fr": {
            "Home": "Accueil",
            "User Guide": "Guide de l'Utilisateur",
            "Tutorial": "Tutoriel",
            "Contributing": "Contribuer",
            "Reference": "Référence",
            "Changelog": "Journal des Modifications",
        },
        "de": {
            "Home": "Startseite",
            "User Guide": "Benutzerhandbuch",
            "Tutorial": "Tutorial",
            "Contributing": "Beitragen",
            "Reference": "Referenz",
            "Changelog": "Änderungsprotokoll",
        },
    }

    # Return pre-defined translation if available
    if target_lang in translations and text in translations[target_lang]:
        return translations[target_lang][text]

    # If API key is provided, use AI translation
    if api_key:
        # TODO: add another AI provider
        try:
            if provider == "openai":
                import openai

                client_openai = openai.OpenAI(api_key=api_key)
                response = client_openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a translator. Translate only the text, no explanations.",
                        },
                        {
                            "role": "user",
                            "content": f"Translate '{text}' to {target_lang}",
                        },
                    ],
                    temperature=0.3,
                    max_tokens=50,
                )
                response_content = response.choices[0].message.content
                if response_content is None:
                    return text
                return response_content.strip()
        except Exception as e:
            logger.warning(f"AI translation failed for '{text}': {e}")

    # Return original text if no translation available
    return text


def update_mkdocs_nav_translations(
    mkdocs_path: Path, api_key: str = "", provider: str = "openai"
) -> None:
    """Update nav_translations in mkdocs.yml file."""
    logger.info(f"Reading {mkdocs_path}")

    with open(mkdocs_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Extract navigation items
    nav_items = extract_nav_items(config.get("nav", []))
    logger.info(f"Found {len(nav_items)} navigation items")

    # Get languages from i18n plugin config
    i18n_config = None
    for plugin in config.get("plugins", []):
        if isinstance(plugin, dict) and "i18n" in plugin:
            i18n_config = plugin["i18n"]
            break

    if not i18n_config:
        logger.error("i18n plugin not found in mkdocs.yml")
        return

    # Update translations for each language
    for lang_config in i18n_config["languages"]:
        locale = lang_config.get("locale")
        if locale == "en":
            continue  # Skip English

        logger.info(f"Updating translations for {locale}")

        if "nav_translations" not in lang_config:
            lang_config["nav_translations"] = {}

        # Translate each nav item
        for item in nav_items:
            if item not in lang_config["nav_translations"]:
                translated = translate_nav_item(item, locale, api_key, provider)
                lang_config["nav_translations"][item] = translated
                logger.info(f"  {item} -> {translated}")

    # Write updated config
    logger.info(f"Writing updated config to {mkdocs_path}")
    with open(mkdocs_path, "w", encoding="utf-8") as f:
        yaml.dump(
            config, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )

    logger.info("Navigation translations updated successfully")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update navigation translations in mkdocs.yml"
    )
    parser.add_argument(
        "--mkdocs-file", type=str, default="mkdocs.yml", help="Path to mkdocs.yml file"
    )
    parser.add_argument(
        "--api-key", type=str, help="API key for AI translation (optional)"
    )
    parser.add_argument(
        "--api-provider",
        type=str,
        choices=["openai", "anthropic"],
        default="openai",
        help="AI API provider",
    )

    args = parser.parse_args()

    mkdocs_path = Path(args.mkdocs_file)
    if not mkdocs_path.exists():
        logger.error(f"File not found: {mkdocs_path}")
        sys.exit(1)

    # Get API key from args or environment
    api_key = args.api_key or os.getenv("TRANSLATION_API_KEY")

    update_mkdocs_nav_translations(mkdocs_path, api_key or "", args.api_provider)


if __name__ == "__main__":
    main()
