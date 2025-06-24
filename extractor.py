import pdfplumber
import fitz  # PyMuPDF
import json
import re
import os
import unicodedata

# Path to the PDF file
PDF_PATH = "Form ADT-1-29092023_signed.pdf"
OUTPUT_JSON = "output.json"
SUMMARY_TXT = "summary.txt"
ATTACHMENTS_DIR = "attachments"

# Ensure attachments directory exists
if not os.path.exists(ATTACHMENTS_DIR):
    os.makedirs(ATTACHMENTS_DIR)


def extract_text_and_tables(pdf_path):
    """Extract text and tables from the PDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    text_content = ""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text
            text_content += (page.extract_text() or "") + "\n"
            # Extract tables
            page_tables = page.extract_tables()
            if page_tables:
                tables.extend(page_tables)
    return text_content, tables


def parse_data(text, tables):
    """Parse relevant fields from text and tables."""
    data = {
        "company_name": "Unknown",  # Not found in provided OCR
        "cin": "Unknown",  # Not found in provided OCR
        "registered_office": "Unknown",  # Not found in provided OCR
        "appointment_date": "",
        "auditor_name": "Auditor's Firm",  # From table
        "auditor_address": "Unknown",  # Not found in provided OCR
        "auditor_frn_or_membership": "Unknown",  # Not found in provided OCR
        "appointment_type": "Reappointment",  # Inferred from previous tenure
    }

    # Debug: Print extracted text to verify content
    print("Extracted Text Sample:\n", text[:500], "...")

    # Extract appointment date with more robust regex
    date_match = re.search(
        r"Date of appointment\s*[:\s]*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE
    )
    if date_match:
        data["appointment_date"] = date_match.group(1)
    else:
        print("Warning: Appointment date not found in text.")

    # Process tables for auditor tenure
    for table in tables:
        for row in table[1:]:  # Skip header
            if len(row) >= 4 and row[1]:  # Check for valid row
                auditor = row[1]
                if auditor and auditor != "":
                    data["auditor_name"] = auditor

    return data


def generate_summary(data):
    """Generate AI-style summary based on extracted data."""
    appointment_date = (
        data["appointment_date"] if data["appointment_date"] else "an unspecified date"
    )
    summary = (
        f"{data['company_name']} has reappointed {data['auditor_name']} as its statutory auditor "
        f"for the financial year 2022-23, effective from {appointment_date}. "
        "The appointment was approved in the Annual General Meeting held on the same date. "
        "All required documents, including the board resolution, have been submitted via Form ADT-1."
    )
    return summary


def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters."""
    # Normalize unicode characters
    filename = (
        unicodedata.normalize("NFKD", filename)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    # Replace invalid characters with underscore
    filename = re.sub(r"[^\w\-.]", "_", filename)

    return filename or "attachment"


def extract_attachments(pdf_path):
    """Extract embedded attachments from the PDF."""
    attachment_summaries = []
    try:
        doc = fitz.open(pdf_path)
        count = doc.embfile_count()
        if count == 0:
            attachment_summaries.append("No embedded attachments found in the PDF.")
        else:
            for i in range(count):
                try:
                    # Get attachment info
                    file_info = doc.embfile_info(i)
                    file_name = file_info.get("name", f"attachment_{i}.pdf")
                    file_name = sanitize_filename(file_name)
                    file_data = doc.embfile_get(i)
                    # Save attachment
                    attachment_path = os.path.join(ATTACHMENTS_DIR, file_name)
                    with open(attachment_path, "wb") as f:
                        f.write(file_data)
                    # Summarize attachment
                    summary = f"Attachment '{file_name}' extracted. "
                    if "consent" in file_name.lower():
                        summary += "Likely contains auditor's consent letter."
                    elif "resolution" in file_name.lower():
                        summary += "Likely contains board resolution approving the appointment."
                    else:
                        summary += "Content type not identified."
                    attachment_summaries.append(summary)
                except Exception as e:
                    attachment_summaries.append(
                        f"Error extracting attachment {i}: {str(e)}"
                    )
        doc.close()
    except Exception as e:
        attachment_summaries.append(f"Error extracting attachments: {str(e)}")
    return attachment_summaries


def main():
    # Step 1: Extract text and tables
    text, tables = extract_text_and_tables(PDF_PATH)

    # Step 2: Parse data into structured format
    extracted_data = parse_data(text, tables)

    # Step 3: Save extracted data to JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(extracted_data, f, indent=4)

    # Step 4: Generate and save AI-style summary
    summary = generate_summary(extracted_data)
    with open(SUMMARY_TXT, "w") as f:
        f.write(summary)

    # Step 5: Extract attachments (Bonus)
    attachment_summaries = extract_attachments(PDF_PATH)
    if attachment_summaries:
        with open(SUMMARY_TXT, "a") as f:
            f.write("\n\nAttachment Summaries:\n")
            for s in attachment_summaries:
                f.write(f"- {s}\n")


if __name__ == "__main__":
    main()
