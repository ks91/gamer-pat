# Bibliography Strategy

This note records a practical strategy for mixed Japanese and English references in this WBS thesis prototype.

## Current Baseline

- Japanese samples use BibTeX with the local `wbsapalike.bst`.
- English sample uses BibTeX with the local `wbsplain.bst`.
- The local styles currently start from TeX Live's `apalike` and `plain` styles.

## Practical Problem

`apalike` is reasonable as a starting point, but it does not natively solve all issues for Japanese references:

- Japanese personal names are not always formatted naturally.
- Punctuation and spacing rules remain English-oriented.
- Mixed Japanese and English entries may look uneven in one list.

## Recommended WBS Operation

For actual thesis writing in this project, use the following rule of thumb:

1. Use `wbsapalike` for Japanese manuscripts.
2. Use `wbsplain` for English manuscripts, because the English Word template indicates a numbered references list.
3. Keep all references in BibTeX from the beginning.
4. When the bibliography stabilizes, inspect the rendered list and fix only the visible problems that matter to supervisors.
5. If the supervisor wants stricter Japanese bibliography conventions, keep refining the local `wbsapalike.bst`.

## Two Realistic Paths

### Path A: Minimal change

- Keep `apalike`.
- In this repository, that means keeping `wbsapalike` close to `apalike`.
- Use `note`, `author`, and `key` fields carefully in Japanese entries.
- Accept minor English-style punctuation in the bibliography.

This is the lowest-risk option for the current `platex + jlreq` workflow.

### Path B: Stronger Japanese support

- Move to a Japanese-aware bibliography style or a custom local `.bst`.
- In this repository, that means evolving `wbsapalike.bst` beyond its current baseline.
- Potentially migrate later to `biblatex` if the toolchain is also updated.

This gives better bibliography control, but it increases implementation cost.

## Example Local Policy

For WBS-style operation, the following local policy is defensible:

- Use one bibliography list for both Japanese and English references.
- Sort by author-year when that remains readable.
- Prefer full author names as entered in the `.bib` file.
- Allow Japanese entries to retain Japanese titles and publisher names without forced romanization.
- Prioritize consistency and supervisor acceptance over strict conformance to any external style manual.

## Japanese Entry Example

For Japanese manuscripts, the local style supports `jaauthor` and `jacitelabel` so that in-text citations and bibliography rendering can remain natural in Japanese.

Example:

```bibtex
@book{otaki2016keieisenryaku,
  author = {Seiichi Otaki and Kazuyori Kanai and Hideo Yamada and Satoshi Iwata},
  jaauthor = {大滝 精一・金井 一頼・山田 英夫・岩田 智},
  jacitelabel = {大滝ほか},
  title = {経営戦略: 論理性・創造性・社会性の追求 第3版},
  publisher = {有斐閣},
  year = {2016}
}
```

Use `author` for BibTeX stability, and add `jaauthor` / `jacitelabel` when the Japanese manuscript should show Japanese-friendly names or labels.

## Build Reminder

Japanese samples:

```sh
platex sample-degree-ja.tex
bibtex sample-degree-ja
platex sample-degree-ja.tex
platex sample-degree-ja.tex
dvipdfmx sample-degree-ja.dvi
```

English sample:

```sh
pdflatex sample-degree-en.tex
bibtex sample-degree-en
pdflatex sample-degree-en.tex
pdflatex sample-degree-en.tex
```
