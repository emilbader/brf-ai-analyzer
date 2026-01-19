# Description

AI-powered assistant for analyzing housing association's annual reports.

## Setup

Install dependencies with `uv`:

```bash
uv sync
```

## Usage

Add a report to `documents/original/` in PDF format. The AI will convert it to text and analyze it based on the guidelines provided in `.github/copilot-instructions.md`. The analysis will be saved in the `reports/` directory.

### Convert PDF to text

```bash
uv run pdf_ocr_converter.py documents/original/<filename>.pdf
```

The analysis includes insights on the association's financial health, potential risks, and improvement opportunities.