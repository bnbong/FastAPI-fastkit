# 번역 가이드

이 가이드는 FastAPI-fastkit 문서 번역에 기여하는 방법을 설명합니다.

## 원본과 번역 정책

> **영어 (`en`)가 FastAPI-fastkit 문서의 기준이 되는 원문입니다.** 다른 모든 언어는 번역 대상이며, 릴리스 단위로든 개별 페이지 단위로든 영어 원문보다 뒤처질 수 있습니다.
>
> 번역된 페이지가 영어 페이지와 다르면, 번역이 따라잡을 때까지 **영어 페이지를 신뢰하세요**. 번역은 기여자들이 도달한 완성도 그대로 배포됩니다 — 부분 번역이 정상이고 자연스러운 상태입니다.

이 정책을 사용자 관점에서 설명하는 페이지는 [번역 현황](../reference/translation-status.md)입니다. 그 페이지에는 각 언어의 실제 완성도와, 아직 번역되지 않은 페이지가 어떻게 표시되는지(요약하면 영어 원문으로 대체됨)가 정리돼 있습니다.

리포지토리 루트의 `CHANGELOG.md` 역시 영어를 기준으로 유지합니다. 어떤 언어에서 `changelog.md` 페이지를 제공하더라도, 별도의 번역본 changelog를 유지하기보다는 이 영문 기준 changelog를 링크하거나 포함하는 방식으로 다루는 것이 현재 정책입니다.

번역에 기여할 때는 사용자가 언어 선택기에서 짐작하지 않아도 무엇이 가능한지 알 수 있도록, 현황 페이지의 표도 함께 갱신해 주세요.

## 개요

FastAPI-fastkit은 AI 기반 자동 번역 시스템을 사용해 문서를 여러 언어로 번역합니다. 이 시스템은 다음과 같은 방식으로 동작합니다:

- 영어로 작성된 원본 문서를 읽고
- AI API(OpenAI 또는 Anthropic)를 사용해 콘텐츠를 번역하며
- 번역 결과를 언어별 디렉터리에 저장하고
- 검토용 GitHub Pull Request를 생성합니다

자동화는 초안을 만들어 주는 역할일 뿐이며, 머지 전에는 여전히 사람의 검토가 필요합니다. AI가 생성한 번역은 PR에서 `draft` 상태로 표시하고, 머지 전에 해당 언어에 능숙한 사용자가 검토해야 합니다.

## 지원 언어

아래는 현재 문서 사이트에서 **빌드 대상으로 설정된** 언어 목록입니다. 빌드 대상으로 등록되어 있다고 해서 그 언어의 페이지가 모두 번역되었다는 뜻은 **아닙니다**. 실제 완성도는 [번역 현황](../reference/translation-status.md) 페이지를 참고하세요.

- 🇰🇷 한국어 (ko)
- 🇯🇵 일본어 (ja)
- 🇨🇳 중국어 (zh)
- 🇪🇸 스페인어 (es)
- 🇫🇷 프랑스어 (fr)
- 🇩🇪 독일어 (de)

## 사전 요구 사항

### 1. 번역 의존성 설치

```bash
# pip 로 설치
pip install openai anthropic

# 또는 pdm 사용
pdm install -G translation
```

### 2. API 키 설정

OpenAI 또는 Anthropic 의 API 키가 필요합니다:

```bash
# OpenAI
export TRANSLATION_API_KEY="sk-..."

# 또는 Anthropic
export TRANSLATION_API_KEY="sk-ant-..."
```

### 3. GitHub CLI 설치 (선택)

자동 PR 생성을 위해:

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# 인증
gh auth login
```

## 사용법

### Make 명령 사용 (권장)

번역을 실행하는 가장 쉬운 방법은 다음과 같습니다:

```bash
# 모든 언어로 모든 문서 번역
make translate

# 특정 언어로만 번역
make translate LANG=ko

# API 제공자와 모델 지정
make translate LANG=ko PROVIDER=openai MODEL=gpt-4
make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
```

### 스크립트 직접 실행

#### 모든 문서 번역

지원하는 모든 언어로 모든 문서를 번역:

```bash
python scripts/translate.py --api-provider openai
```

### 특정 언어만 번역

한국어로만 번역:

```bash
python scripts/translate.py --target-lang ko --api-provider openai
```

### 특정 파일만 번역

특정 문서 파일만 번역:

```bash
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/installation.md user-guide/quick-start.md \
  --api-provider openai
```

### PR 생성 건너뛰기

GitHub PR을 만들지 않고 번역만 수행하려면:

```bash
python scripts/translate.py --target-lang ko --no-pr --api-provider openai
```

### Anthropic Claude 사용

OpenAI 대신 Anthropic Claude 사용:

```bash
python scripts/translate.py \
  --target-lang ko \
  --api-provider anthropic \
  --api-key "sk-ant-..."
```

## 디렉터리 구조

번역이 끝난 뒤 문서 구조는 다음과 같습니다:

```
docs/
├── en/                    # 영어 (원본)
│   ├── index.md
│   ├── user-guide/
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── ...
│   ├── tutorial/
│   └── ...
├── ko/                    # 한국어
│   ├── index.md
│   ├── user-guide/
│   └── ...
├── ja/                    # 일본어
├── zh/                    # 중국어
├── es/                    # 스페인어
├── fr/                    # 프랑스어
├── de/                    # 독일어
├── css/                   # 공유 자산
├── js/                    # 공유 자산
└── img/                   # 공유 자산
```

## 번역 워크플로

### 1. 영어로 문서 작성

모든 문서는 먼저 `docs/` 디렉터리에 영어로 작성해야 합니다:

```bash
# 새 문서 작성
vim docs/user-guide/new-feature.md
```

### 2. 번역 실행

영어 문서 작성이 끝나면 번역 스크립트를 실행하세요:

```bash
python scripts/translate.py --target-lang ko
```

### 3. Pull Request 검토

스크립트가 번역 결과로 Pull Request를 생성합니다. PR을 검토할 때는 다음 사항을 확인하세요:

1. 마크다운 형식이 보존됐는지 확인
2. 기술 용어가 적절히 처리됐는지 검증
3. 코드 예제가 그대로 유지됐는지 확인
4. 언어별 특수 이슈가 없는지 점검

### changelog 정책

- 리포지토리 루트의 `CHANGELOG.md` 는 영어로 유지합니다.
- 루트 changelog 자체를 다른 언어로 다시 작성하는 것을 목표로 한 번역 PR은 열지 마세요.
- 어떤 언어에서 changelog 페이지가 필요하다면, `docs/<locale>/changelog.md` 는 영문 기준 changelog로 들어가는 래퍼나 진입점으로 취급하세요.

### 4. 승인과 머지 (메인테이너용)

번역이 검증되면:

```bash
gh pr review <pr-number> --approve
gh pr merge <pr-number>
```

### 5. 문서 배포

문서 사이트가 자동으로 새 번역을 반영해 다시 빌드됩니다.

## 번역 설정

`scripts/translation_config.json`을 편집해 동작을 조정할 수 있습니다:

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

## 모범 사례

### 원본 문서 작성 시

1. **명확한 표현**: 번역이 잘 되도록 명확하고 단순한 영어로 작성
2. **일관된 용어**: 기술 용어는 일관되게 사용
3. **올바른 코드 블록**: 코드 블록에 항상 언어를 지정
4. **링크 검증**: 내부 링크는 모두 상대 경로 사용

### 번역 검토 시

1. **기술 용어**: 기술 용어가 대상 언어에 적절한지 검증
2. **문화적 맥락**: 예제가 현지화되어야 하는지 확인
3. **형식**: 모든 마크다운 형식이 보존됐는지 확인
4. **코드 무결성**: 코드 블록이 그대로 유지됐는지 검증

## 문제 해결

### API 레이트 제한

API 레이트 제한에 걸리면, 더 작은 단위로 번역하세요:

```bash
# user guide 만 번역
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/*.md
```

### 번역 품질 문제

번역 품질이 떨어진다면:

1. API 키가 유효한지 확인
2. 다른 AI 제공자 시도
3. 복잡한 문서를 더 작은 섹션으로 나누기
4. 직접 검토하고 수정

### GitHub PR 실패

PR 생성이 실패한다면:

```bash
# PR 없이 번역만
python scripts/translate.py --target-lang ko --no-pr

# 직접 PR 생성
git checkout -b translation/ko
git add docs/ko/
git commit -m "Add Korean translations"
git push -u origin translation/ko
gh pr create --title "Add Korean translations"
```

## 수동 번역

직접 손으로 번역할 수도 있습니다:

1. 영어 파일을 대상 언어 디렉터리에 복사:

```bash
mkdir -p docs/ko/user-guide
cp docs/en/user-guide/installation.md docs/ko/user-guide/installation.md
```

2. 선호하는 에디터로 파일을 편집
3. 커밋 후 PR 생성

## 언어 전환

문서 사이트 상단에는 언어 선택기가 있습니다. 사용자는 다음과 같은 순서로 활용할 수 있습니다:

1. 언어 선택기 클릭
2. 선호하는 언어 선택
3. 번역된 문서 탐색

## 새 언어 추가하기

새 언어를 추가하려면:

1. `scripts/translation_config.json` 편집:

```json
{
  "code": "pt",
  "name": "Portuguese",
  "native_name": "Português",
  "enabled": true
}
```

2. `mkdocs.yml` 갱신:

```yaml
- locale: pt
  name: Português
  build: true
```

3. 번역 실행:

```bash
python scripts/translate.py --target-lang pt
```

## 도움이 필요하신가요?

- **Issues**: 번역 관련 이슈는 [GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)에 등록
- **Discussions**: 질문은 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)에서 논의
- **기여 안내**: [CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md) 참고

## 번역 품질 기준

모든 번역은 다음 기준을 충족해야 합니다:

- ✅ 모든 마크다운 형식을 보존
- ✅ 코드 블록을 그대로 유지
- ✅ 기술 용어를 적절하게 다룸
- ✅ 올바른 문법과 맞춤법 사용
- ✅ 언어별 컨벤션을 따름
- ✅ 모든 링크가 정상 동작하는지 테스트

FastAPI-fastkit 번역에 기여해 주셔서 감사합니다! 🌍
