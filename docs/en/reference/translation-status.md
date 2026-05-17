# Translation status

FastAPI-fastkit ships docs in several languages, but those translations
are **not at parity**. This page is the single source of truth for what
is actually translated where, what gets shown when a page hasn't been
translated, and how to help.

## Source of truth

> **English (`en`) is the source of truth.** All product, CLI, and API
> behaviour described in the docs is authored against the English files
> first. Other locales are translations of those English sources and may
> lag behind a release.
>
> If a translated page disagrees with the English page, **trust the
> English page** until the translation is updated.

The English files live under [`docs/en/`](https://github.com/bnbong/FastAPI-fastkit/tree/main/docs/en).
Every other locale (`docs/ko/`, `docs/ja/`, ...) is a translation
target.

The repository-root `CHANGELOG.md` is part of that English source of
truth. Locale-specific `changelog.md` pages may exist as wrappers or
entry points, but they intentionally reuse the canonical English
release history instead of maintaining translated copies.

## Per-locale completeness

The numbers below count Markdown pages in each locale's directory tree
relative to the English source. They reflect what's actually present in
the repository — not what shows up in the language switcher (which the
next section explains).

| Locale | Status | Markdown pages | Notes |
|---|---|---:|---|
| 🇬🇧 English (`en`) | ✅ Source of truth | 26 / 26 | Authoritative. |
| 🇰🇷 Korean (`ko`) | ✅ Complete | 26 / 26 | All locale pages are present. Phase 1: top-level + core user-guide; Phase 2: remaining user-guide + all tutorials; Phase 3: contributing + reference. `docs/ko/changelog.md` intentionally reuses the canonical English `CHANGELOG.md`. |
| 🇯🇵 Japanese (`ja`) | ✅ Complete | 26 / 26 | All locale pages are present. Phase 1: top-level + core user-guide; Phase 2: remaining user-guide + all tutorials; Phase 3: contributing + reference. `docs/ja/changelog.md` intentionally reuses the canonical English `CHANGELOG.md`. |
| 🇨🇳 Chinese (`zh`) | 🔴 Skeleton | 0 / 26 | Build target only. Every page falls back to English. |
| 🇪🇸 Spanish (`es`) | ✅ Complete | 26 / 26 | All locale pages are present. Phase 1: top-level + core user-guide; Phase 2: remaining user-guide + all tutorials; Phase 3: contributing + reference. `docs/es/changelog.md` intentionally reuses the canonical English `CHANGELOG.md`. |
| 🇫🇷 French (`fr`) | ✅ Complete | 26 / 26 | All locale pages are present. Phase 1: top-level + core user-guide; Phase 2: remaining user-guide + all tutorials; Phase 3: contributing + reference. `docs/fr/changelog.md` intentionally reuses the canonical English `CHANGELOG.md`. |
| 🇩🇪 German (`de`) | ✅ Complete | 26 / 26 | All locale pages are present. Phase 1: top-level + core user-guide; Phase 2: remaining user-guide + all tutorials; Phase 3: contributing + reference. `docs/de/changelog.md` intentionally reuses the canonical English `CHANGELOG.md`. |

*Snapshot verified 2026-05-17; de row recounted for the current branch after Phase 3 (contributing + reference) landed. German now has all locale pages present, while `docs/de/changelog.md` intentionally points to the canonical English changelog.* These counts are maintained by hand;
to recount the current state from the repo root, run:

```console
$ for loc in en ko ja zh es fr de; do
    echo "$loc: $(find docs/$loc -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  done
```

If the recount disagrees with the table, the table is stale — please
update it (or open a PR / issue noting the drift).

Legend:

- ✅ **Source of truth** — the locale we author against.
- 🟡 **Partial** — some pages translated; missing pages fall back.
- 🔴 **Skeleton** — language switcher entry exists, but no translated
  pages are checked in yet. The site renders English content under the
  translated nav labels.

## How fallback works

The docs site uses
[`mkdocs-static-i18n`](https://github.com/ultrabug/mkdocs-static-i18n)
with `fallback_to_default: true`. This means:

- For each translated locale, MkDocs only writes pages that exist in
  that locale's directory.
- For every page **not** present in a locale, the build falls back to
  the English version of that page.
- The site-wide language switcher always lists every configured locale
  regardless of how many pages each one has, because the build emits a
  reachable URL for each (page → fallback to English if needed).

So a 🔴 Skeleton entry in the language switcher is **not** a promise
that the docs are translated — only that the locale build target is
configured. The behaviour is intentional (out-of-tree contributors can
incrementally translate a page at a time without breaking the link
graph), but it makes the language switcher look more complete than the
underlying content actually is.

## How to read the docs site

- **Always default to English** if you want the most accurate, current
  information.
- **Use a translated locale** only after checking this page for the
  locale's status. If it's 🟡 or 🔴 and you hit a topic that hasn't been
  translated, you're reading an English fallback under a translated nav
  label.

## How to help

The current rollout is **one tracking issue per locale**, with the work
broken into **phases** — for example `ko` is being landed across
Phase 1 (top-level + core user-guide), Phase 2 (remaining user-guide +
all tutorials), Phase 3 (contributing + reference). Each phase ships
as its own PR so reviewers can sign off on a coherent slice without
waiting for the entire locale to be finished.

If you'd like to contribute:

1. Read the [Translation Guide](../contributing/translation-guide.md)
   for the workflow, tooling, and style conventions.
2. **Check or open the locale tracking issue first.** If a locale
   already has an open tracking issue, claim a phase (or a specific
   page within a phase) there so the work doesn't double up. If no
   tracking issue exists for the locale you want to work on, open one
   that lists which pages belong to which phase, then start with
   Phase 1.
3. **One PR per phase is the preferred shape.** Smaller "fix this
   single page" PRs are still welcome — especially for correcting an
   out-of-sync translation — but for net-new locale work, batching by
   phase keeps glossary decisions and cross-link wording consistent
   across the slice.
4. Open the PR adding files under `docs/<locale>/<same path>`. Keep
   filenames identical to the English source so MkDocs picks them up
   automatically.
5. Treat localized changelog pages as wrappers around the canonical
   English `CHANGELOG.md` unless project policy explicitly changes.
6. Update this page's table to reflect the new completeness count
   (use the recount snippet at the top of this page) and bump the
   "Snapshot verified" date so reviewers can see when it was last
   reconciled. Note in the "Notes" column which phase has landed if
   the locale is still partial.

Bug reports about translated pages going out of sync with the English
source are welcome — please link the English page and the translated
page so we can triage.

## Why we ship 🔴 Skeleton locales at all

Two reasons:

1. **Predictable URL space.** Each locale already has its `/<locale>/`
   subtree reachable, so when a translated page lands the link is
   stable from day one — including links published in this guide.
2. **Lower contributor friction.** Contributors translating a single
   page don't have to also wire a new locale build into MkDocs config —
   they just drop the file in.

If a locale stays at 🔴 Skeleton with no contribution activity for an
extended period, we may revisit whether to keep its build target
enabled. That decision is tracked separately and is **not** something
this status page silently changes.
