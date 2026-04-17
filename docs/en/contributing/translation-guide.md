# Translation Guide

This guide explains how to contribute translations for FastAPI-fastkit documentation.

## Overview

FastAPI-fastkit uses an automated translation system powered by AI to translate documentation into multiple languages. The system:

- Reads source documentation in English
- Translates content using AI APIs (OpenAI or Anthropic)
- Saves translations to language-specific directories
- Creates GitHub Pull Requests for review

## Supported Languages

Currently supported languages:

- 🇰🇷 Korean (ko)
- 🇯🇵 Japanese (ja)
- 🇨🇳 Chinese (zh)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)

## Prerequisites

### 1. Install Translation Dependencies

```bash
# Install using pip
pip install openai anthropic

# Or using pdm
pdm install -G translation
```

### 2. Set Up API Keys

You need an API key from either OpenAI or Anthropic:

```bash
# For OpenAI
export TRANSLATION_API_KEY="sk-..."

# Or for Anthropic
export TRANSLATION_API_KEY="sk-ant-..."
```

### 3. Install GitHub CLI (Optional)

For automatic PR creation:

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

## Usage

### Using Make Commands (Recommended)

The easiest way to run translations:

```bash
# Translate all docs to all languages
make translate

# Translate to specific language
make translate LANG=ko

# Specify API provider and model
make translate LANG=ko PROVIDER=openai MODEL=gpt-4
make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
```

### Using Script Directly

#### Translate All Documentation

Translate all documentation to all supported languages:

```bash
python scripts/translate.py --api-provider openai
```

### Translate to Specific Language

Translate only to Korean:

```bash
python scripts/translate.py --target-lang ko --api-provider openai
```

### Translate Specific Files

Translate only specific documentation files:

```bash
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/installation.md user-guide/quick-start.md \
  --api-provider openai
```

### Skip PR Creation

Translate without creating a GitHub PR:

```bash
python scripts/translate.py --target-lang ko --no-pr --api-provider openai
```

### Use Anthropic Claude

Use Anthropic's Claude instead of OpenAI:

```bash
python scripts/translate.py \
  --target-lang ko \
  --api-provider anthropic \
  --api-key "sk-ant-..."
```

## Directory Structure

After translation, the documentation structure will look like this:

```
docs/
├── en/                    # English (original)
│   ├── index.md
│   ├── user-guide/
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── ...
│   ├── tutorial/
│   └── ...
├── ko/                    # Korean
│   ├── index.md
│   ├── user-guide/
│   └── ...
├── ja/                    # Japanese
├── zh/                    # Chinese
├── es/                    # Spanish
├── fr/                    # French
├── de/                    # German
├── css/                   # Shared assets
├── js/                    # Shared assets
└── img/                   # Shared assets
```

## Translation Workflow

### 1. Write Documentation in English

All documentation should first be written in English in the `docs/` directory:

```bash
# Create new documentation
vim docs/user-guide/new-feature.md
```

### 2. Run Translation

Once the English documentation is complete, run the translation script:

```bash
python scripts/translate.py --target-lang ko
```

### 3. Review Pull Request

The script will create a Pull Request with the translations. Review the PR:

1. Check that markdown formatting is preserved
2. Verify technical terms are handled correctly
3. Ensure code examples remain unchanged
4. Check for language-specific issues

### 4. Approve and Merge (for maintainers)

Once the translation is verified:

```bash
gh pr review <pr-number> --approve
gh pr merge <pr-number>
```

### 5. Deploy Documentation

The documentation site will automatically rebuild with the new translations.

## Translation Configuration

Edit `scripts/translation_config.json` to customize:

```json
{
  "source_language": "en",
  "target_languages": [
    {
      "code": "ko",
      "name": "Korean",
      "native_name": "한국어",
      "enabled": true
    }
  ],
  "translation_settings": {
    "default_api_provider": "openai",
    "batch_size": 5,
    "preserve_formatting": true
  },
  "github_settings": {
    "create_pr_by_default": true,
    "branch_prefix": "translation"
  }
}
```

## Best Practices

### For Source Documentation

1. **Use Clear Language**: Write clear, simple English that translates well
2. **Consistent Terminology**: Use consistent technical terms
3. **Proper Code Blocks**: Always specify language in code blocks
4. **Link Verification**: Ensure all internal links use relative paths

### For Translation Review

1. **Technical Terms**: Verify technical terms are appropriate for target language
2. **Cultural Context**: Check if examples need localization
3. **Formatting**: Ensure all markdown formatting is preserved
4. **Code Integrity**: Verify code blocks are unchanged

## Troubleshooting

### API Rate Limits

If you hit API rate limits, translate in smaller batches:

```bash
# Translate only user guide
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/*.md
```

### Translation Quality Issues

If translations are poor quality:

1. Check your API key is valid
2. Try a different AI provider
3. Break down complex documents into smaller sections
4. Manually review and edit the translation

### GitHub PR Fails

If PR creation fails:

```bash
# Translate without PR
python scripts/translate.py --target-lang ko --no-pr

# Manually create PR
git checkout -b translation/ko
git add docs/ko/
git commit -m "Add Korean translations"
git push -u origin translation/ko
gh pr create --title "Add Korean translations"
```

## Manual Translation

You can also translate manually:

1. Copy English file to target language directory:
```bash
mkdir -p docs/ko/user-guide
cp docs/en/user-guide/installation.md docs/ko/user-guide/installation.md
```

2. Edit the file in your preferred editor
3. Commit and create a PR

## Language Switching

The documentation site includes a language switcher in the top navigation. Users can:

1. Click the language selector
2. Choose their preferred language
3. Navigate through translated documentation

## Contributing New Languages

To add a new language:

1. Edit `scripts/translation_config.json`:
```json
{
  "code": "pt",
  "name": "Portuguese",
  "native_name": "Português",
  "enabled": true
}
```

2. Update `mkdocs.yml`:
```yaml
- locale: pt
  name: Português
  build: true
```

3. Run translation:
```bash
python scripts/translate.py --target-lang pt
```

## Need Help?

- **Issues**: Report translation issues on [GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- **Contributing**: See [CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)

## Translation Quality Standards

All translations must meet these standards:

- ✅ Preserve all markdown formatting
- ✅ Keep code blocks unchanged
- ✅ Maintain technical terminology appropriately
- ✅ Use proper grammar and spelling
- ✅ Follow language-specific conventions
- ✅ Test all links work correctly

Thank you for contributing to FastAPI-fastkit translations! 🌍
