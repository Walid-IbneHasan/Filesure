# Filesure Internship Take-Home Assignment

This repository contains the solution for the Filesure Internship Take-Home Assignment, which involves:

- Extracting structured data from a Form ADT-1 PDF
- Generating a JSON output
- Creating an AI-style summary
- Handling embedded attachments

---

## 📁 Files

| File/Folder                                 | Description                                                         |
|----------------------------------------------|---------------------------------------------------------------------|
| `extractor.py`                              | Python script to extract data, generate JSON, and create a summary. |
| `output.json`                               | Extracted structured data in JSON format.                           |
| `summary.txt`                               | AI-generated summary and attachment summaries.                      |
| `attachments/`                              | Contains embedded PDFs (e.g., consent letters) extracted from the input PDF. |
| `demo.mp4`                                  | Video demo explaining the solution.                                 |
| `Form ADT-1-29092023_signed.pdf` *(not included)* | Input PDF.                                                         |

---

## 🛠 Requirements

- **Python** 3.8+
- **Libraries:**
  - [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) (version 1.23.0+)
  - [pytesseract](https://pypi.org/project/pytesseract/) *(optional, for OCR)*
  - [pdf2image](https://pypi.org/project/pdf2image/) *(optional, for OCR)*

Install dependencies:
pip install PyMuPDF pytesseract pdf2image


---

## 🚀 How to Run

1. Place `Form ADT-1-29092023_signed.pdf` in the project directory.
2. Run the extraction script:
    ```
    python extractor.py
    ```

### Outputs

- `output.json`: Structured data
- `summary.txt`: Summary and attachment insights
- `attachments/`: Extracted attachments

---

## ⚙️ Assumptions

- **Form fields** are prioritized for accurate data extraction.
- Appointment type **“ARGM”** is mapped to **“Reappointment.”**
- Attachment names are derived from form fields and sanitized.
- **OCR** is used for scanned PDFs if needed.

---

## 🎥 Video Demo

The demo (`demo.mp4`, 6 minutes) demonstrates:

- Running the script
- Explaining dynamic extraction and fixes for address and attachments
- Showing JSON, summary, and attachment outputs
- Discussing assumptions and limitations

---

## 📝 Notes

- Ensure **PyMuPDF** is version **1.23.0+**  
  *(Upgrade if necessary: `pip install --upgrade PyMuPDF`)*
- For scanned PDFs, install **Tesseract** and **Poppler** for OCR support.
- Attachment names are mapped to meaningful names using form fields.

---
