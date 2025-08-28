
# Legal Document Converter (Plain English and Bullet Summary)

This project converts legal documents (PDF, DOCX, TXT) into:
1) **Plain-English** versions that preserve all content and context.
2) **Bullet-point summaries** per section that retain legal meaning.

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U openai python-docx pdfplumber PyPDF2 reportlab tqdm
```

## Configure API Key 

```bash
# macOS / Linux
export OPENAI_API_KEY="sk-..."

# Windows (PowerShell)
setx OPENAI_API_KEY "sk-..."
```

## Run

```bash
python legal_converter.py --input ./in --output ./out --model gpt-4o-mini --formats docx,txt
```

- Use `--workers 3` to process multiple files in parallel.
- The script writes outputs under `out/<DocumentName>/` as:
  - `<DocumentName>_plainEnglish.docx`
  - `<DocumentName>_summary.docx`
  - (and optionally .txt / .pdf if selected)

## Notes

- **DOCX**: Section detection uses real heading styles when available (Heading 1/2/3).
- **PDF/TXT**: Sections are detected with regex heuristics (Article/Section/numbered headings). If none are found, the whole document is treated as a single section.
- The script automatically splits long sections into chunks to stay within model limits.
- Each chunk is rewritten and summarized separately; results are concatenated per section.
- A basic quality check flags unusually short or placeholder-like outputs to the log.
- Logging is written to `out/processing.log`.

## Troubleshooting

- If you see rate limit errors, reduce `--workers` to 1 and re-run.
- If a PDF is scanned (image-based), text extraction may be empty. In that case, run OCR first (e.g., `ocrmypdf`), then try again.
