Filesure Internship Take-Home Assignment
This repository contains the solution for the Filesure Internship Take-Home Assignment, extracting structured data from a Form ADT-1 PDF, generating a JSON output, creating an AI-style summary, and handling embedded attachments.
Files

extractor.py: Python script to extract data, generate JSON, and create a summary.
output.json: Extracted structured data in JSON format.
summary.txt: AI-generated summary and attachment summaries.
attachments/: Contains embedded PDFs (e.g., consent letters) extracted from the input PDF.
demo.mp4: Video demo explaining the solution.
Form ADT-1-29092023_signed.pdf: Input PDF (not included in repo).

Requirements

Python 3.8+
Libraries: PyMuPDF (1.23.0+), optionally pytesseract, pdf2image for OCRpip install PyMuPDF pytesseract pdf2image



How to Run

Place Form ADT-1-29092023_signed.pdf in the project directory.
Run the script:python extractor.py


Outputs:
output.json: Structured data.
summary.txt: Summary and attachment insights.
attachments/: Extracted attachments.



Assumptions

Form fields are prioritized for accurate data extraction.
Appointment type “ARGM” is mapped to “Reappointment.”
Attachment names are derived from form fields and sanitized.
OCR is used for scanned PDFs if needed.

Video Demo
The demo (6 minutes) demonstrates:

Running the script.
Explaining dynamic extraction and fixes for address and attachments.
Showing JSON, summary, and attachment outputs.
Discussing assumptions and limitations.

Notes

Ensure PyMuPDF is version 1.23.0+ (pip install --upgrade PyMuPDF).
For scanned PDFs, install Tesseract and Poppler for OCR.
Attachment names are mapped to meaningful names using form fields.
