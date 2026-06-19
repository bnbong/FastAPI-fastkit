# 翻译指南

本指南说明如何为 FastAPI-fastkit 文档贡献翻译。

## 权威来源与翻译政策

> **英文(`en`)是 FastAPI-fastkit 文档的权威来源。** 其他所有语言都是翻译目标,可能在某个版本或单个页面上落后于英文。
>
> 当翻译页面与英文页面不一致时,**请以英文页面为准**,直到翻译跟上为止。翻译以贡献者达到的进度发布 —— 部分覆盖是正常且符合预期的。

与该政策相对应的用户视角说明是 [翻译状态](../reference/translation-status.md) 页面,它会列出每个语言的实际完成度,以及尚未翻译时 MkDocs 的呈现方式(简而言之:回退到英文)。

仓库根目录的 `CHANGELOG.md` 也保持英文,作为权威发布历史。如果某个语言提供了 `changelog.md` 页面,该页面应当链接或包含规范的英文 changelog,而不要单独维护一份翻译过的 changelog —— 除非将来项目政策做出明确调整。

每次贡献翻译时,也请同步更新状态页中的表格,这样用户无需从语言切换器中猜测就能知道有哪些可用内容。

## 总览

FastAPI-fastkit 使用一套基于 AI 的自动化翻译系统,把文档翻译成多种语言。该系统会:

- 读取英文源文档
- 使用 AI API(OpenAI 或 Anthropic)翻译内容
- 将翻译结果保存到对应语言目录
- 创建 GitHub Pull Request 以供评审

自动化只提供起点,合并前**仍需人工评审**。AI 生成的翻译在 PR 中应标记为「draft」,并由该语言的熟练使用者评审后再合入。

## 支持的语言

以下是文档站当前**会构建**的语言。仅仅配置了构建目标**并不**意味着该语言已被翻译 —— 真实完成度请参阅 [翻译状态](../reference/translation-status.md)。

- 🇰🇷 韩文(ko)
- 🇯🇵 日文(ja)
- 🇨🇳 中文(zh)
- 🇪🇸 西班牙文(es)
- 🇫🇷 法文(fr)
- 🇩🇪 德文(de)

## 前置条件

### 1. 安装翻译相关依赖

```bash
# Install using pip
pip install openai anthropic

# Or using pdm
pdm install -G translation
```

### 2. 配置 API key

您需要 OpenAI 或 Anthropic 任一家的 API key:

```bash
# For OpenAI
export TRANSLATION_API_KEY="sk-..."

# Or for Anthropic
export TRANSLATION_API_KEY="sk-ant-..."
```

### 3. 安装 GitHub CLI(可选)

用于自动创建 PR:

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

## 使用方式

### 使用 Make 命令(推荐)

运行翻译最便捷的方式:

```bash
# Translate all docs to all languages
make translate

# Translate to specific language
make translate LANG=ko

# Specify API provider and model
make translate LANG=ko PROVIDER=openai MODEL=gpt-4
make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
```

### 直接使用脚本

#### 翻译全部文档

把全部文档翻译为所有支持的语言:

```bash
python scripts/translate.py --api-provider openai
```

### 翻译为指定语言

仅翻译为韩文:

```bash
python scripts/translate.py --target-lang ko --api-provider openai
```

### 翻译指定文件

只翻译特定的文档文件:

```bash
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/installation.md user-guide/quick-start.md \
  --api-provider openai
```

### 跳过 PR 创建

翻译但不创建 GitHub PR:

```bash
python scripts/translate.py --target-lang ko --no-pr --api-provider openai
```

### 使用 Anthropic Claude

使用 Anthropic 的 Claude 代替 OpenAI:

```bash
python scripts/translate.py \
  --target-lang ko \
  --api-provider anthropic \
  --api-key "sk-ant-..."
```

## 目录结构

完成翻译后,文档结构形如:

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

## 翻译工作流

### 1. 用英文撰写文档

所有文档都应先用英文写在 `docs/` 目录:

```bash
# Create new documentation
vim docs/user-guide/new-feature.md
```

### 2. 运行翻译

英文文档完成后,运行翻译脚本:

```bash
python scripts/translate.py --target-lang ko
```

### 3. 评审 Pull Request

脚本会创建包含翻译结果的 Pull Request。评审时请:

1. 检查 markdown 格式是否保留
2. 核对技术术语是否处理得当
3. 确认代码示例未被改动
4. 检查与目标语言相关的具体问题

### Changelog 政策

- 仓库根目录的 `CHANGELOG.md` 保持英文。
- 不要开启「把根 changelog 中的发布历史改写成其他语言」的翻译 PR。
- 如果某个语言需要 changelog 页面,请把 `docs/<locale>/changelog.md` 视为规范英文 changelog 的包装页或入口页。

### 4. 批准并合并(面向维护者)

翻译核对完毕后:

```bash
gh pr review <pr-number> --approve
gh pr merge <pr-number>
```

### 5. 部署文档

文档站会自动重建,新增的翻译会随之上线。

## 翻译配置

编辑 `scripts/translation_config.json` 进行定制:

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

## 最佳实践

### 源文档相关

1. **使用清晰的语言**:让英文表达清楚、简洁,便于翻译
2. **术语一致**:对技术术语保持一致
3. **正确使用代码块**:始终在代码块上标明语言
4. **链接核对**:内部链接都使用相对路径

### 翻译评审相关

1. **技术术语**:确认这些术语在目标语言下是否恰当
2. **文化语境**:判断示例是否需要本地化
3. **格式**:保留全部 markdown 格式
4. **代码完整性**:确认代码块未被改动

## 故障排查

### 触发 API 限流

如果触发 API 限流,可按更小的批次翻译:

```bash
# Translate only user guide
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/*.md
```

### 翻译质量问题

若翻译质量不佳:

1. 检查 API key 是否有效
2. 换一家 AI provider 试试
3. 把复杂文档拆成更小的章节
4. 手动评审并修订翻译

### GitHub PR 创建失败

如果 PR 创建失败:

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

## 手动翻译

也可以完全手动翻译:

1. 把英文文件复制到目标语言目录:
```bash
mkdir -p docs/ko/user-guide
cp docs/en/user-guide/installation.md docs/ko/user-guide/installation.md
```

2. 用您喜欢的编辑器编辑该文件
3. 提交并创建 PR

## 语言切换

文档站顶部导航中包含语言切换器,用户可以:

1. 点击语言选择器
2. 选择心仪的语言
3. 在翻译过的文档间浏览

## 贡献新语言

要新增一种语言:

1. 编辑 `scripts/translation_config.json`:
```json
{
  "code": "pt",
  "name": "Portuguese",
  "native_name": "Português",
  "enabled": true
}
```

2. 更新 `mkdocs.yml`:
```yaml
- locale: pt
  name: Português
  build: true
```

3. 运行翻译:
```bash
python scripts/translate.py --target-lang pt
```

## 需要帮助?

- **Issues**:在 [GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues) 反馈翻译问题
- **Discussions**:在 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions) 提问
- **Contributing**:参见 [CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)

## 翻译质量标准

所有翻译都必须达到以下标准:

- ✅ 保留全部 markdown 格式
- ✅ 保持代码块原样不动
- ✅ 妥善处理技术术语
- ✅ 语法与拼写正确
- ✅ 遵循目标语言的约定
- ✅ 验证所有链接可用

感谢您为 FastAPI-fastkit 的翻译工作贡献力量!🌍
