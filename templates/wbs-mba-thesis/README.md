# WBS MBA Thesis LaTeX Package

This directory is the distributable package for the Waseda Business School thesis prototype.

## Included Files

- `wbsmba.cls`: main class file
- `wbsapalike.bst`: local author-year BibTeX style for Japanese documents
- `wbsplain.bst`: local numbered BibTeX style for English documents
- `bibliography-guide.md`: notes on bibliography handling
- `sample-degree-ja.tex` / `.bib` / `.pdf`: Japanese degree thesis sample
- `sample-project-ja.tex` / `.bib` / `.pdf`: Japanese project thesis sample
- `sample-degree-en.tex` / `.bib` / `.pdf`: English degree thesis sample

## Document Types

- Japanese MBA degree thesis
- Japanese project research thesis
- English MBA degree thesis

## Build

Japanese degree thesis sample:

```sh
platex sample-degree-ja.tex
bibtex sample-degree-ja
platex sample-degree-ja.tex
platex sample-degree-ja.tex
dvipdfmx sample-degree-ja.dvi
```

Japanese project thesis sample:

```sh
platex sample-project-ja.tex
bibtex sample-project-ja
platex sample-project-ja.tex
platex sample-project-ja.tex
dvipdfmx sample-project-ja.dvi
```

English degree thesis sample:

```sh
pdflatex sample-degree-en.tex
bibtex sample-degree-en
pdflatex sample-degree-en.tex
pdflatex sample-degree-en.tex
```

## Notes

- The Japanese samples use `jlreq` with standard Arabic section numbering.
- Japanese in-text citations are rendered in a Japanese-friendly style such as `(淺羽・牛島, 2010)` and `(石井ほか, 1996)`.
- Japanese bibliography entries can use `jaauthor` and `jacitelabel` in `.bib` files.
- English references are numbered to match the English Word template more closely.

## Distribution Hint

If this package is moved into the GAMER PAT repository, keep this directory intact and publish it as a single subtree or release asset.
The original Word templates are intentionally not included in this distributable package.
