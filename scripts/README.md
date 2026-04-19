# Scripts

This directory contains standalone helper scripts.

## Extract Text Targets from Annotated PDFs

### Name

`extract_pdf_annotations.py`

### Purpose

Extracts page number, highlighted target text, annotation comment, and nearby context from a commented PDF.

Intended for CLI-based review workflows where advisor or reviewer comments are delivered as annotated PDFs.

### Requirements

- `python3`
- `pdftotext`

The script uses only the Python standard library plus `pdftotext -bbox-layout`.

### Example

```sh
python3 extract_pdf_annotations.py commented.pdf --text-pdf clean.pdf --format markdown > comments.md
```

### Regression Test

```sh
python3 -m unittest tests.test_extract_pdf_annotations
```

### Notes

- `--text-pdf clean.pdf` should point to the clean PDF that was originally shared with the advisor or reviewer before annotations were added.
- In normal review workflows, students usually already have this file because they exported it themselves and sent it by email, chat, or file upload before receiving the commented PDF back.
- Keep the clean PDF and the commented PDF as a matched pair for the same version of the document.
- Use simple versioned filenames such as `thesis-v12.pdf` and `thesis-v12-commented.pdf` to avoid mixing revisions.
