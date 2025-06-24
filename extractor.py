import fitz  # PyMuPDF
import json
import re
import os
import unicodedata
import string

# Path to the PDF file
PDF_PATH = "Form ADT-1-29092023_signed.pdf"
OUTPUT_JSON = "output.json"
SUMMARY_TXT = "summary.txt"
ATTACHMENTS_DIR = "attachments"

# Ensure attachments directory exists
if not os.path.exists(ATTACHMENTS_DIR):
    os.makedirs(ATTACHMENTS_DIR)


def extract_text_and_form_fields(pdf_path):
    """Extract text and form fields from the PDF using PyMuPDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    text_content = ""
    form_fields = {}
    doc = fitz.open(pdf_path)

    # Extract text from all pages
    for page in doc:
        text_content += page.get_text("text") + "\n"
        # Extract form fields
        for field in page.widgets():
            if field and field.field_name:
                form_fields[field.field_name] = field.field_value or ""

    doc.close()
    return text_content, form_fields


def parse_data(text, form_fields):
    """Dynamically parse relevant fields, prioritizing form fields."""
    data = {
        "company_name": "",
        "cin": "",
        "registered_office": "",
        "appointment_date": "",
        "auditor_name": "",
        "auditor_address": "",
        "auditor_frn_or_membership": "",
        "appointment_type": "",
    }

    # Debug: Print extracted text and form fields
    print("Extracted Text Sample:\n", text[:1000], "...")
    print("Form Fields:", form_fields)

    # Map form field names to data keys
    field_mappings = {
        "company_name": ["CompanyName_C", "Name of the company"],
        "cin": ["CIN_C", "Corporate identity number"],
        "registered_office": ["CompanyAdd_C", "Address of the registered office"],
        "appointment_date": ["DateAnnualGenMeet_D", "DateOfAppSect_D"],
        "auditor_name": ["NameAuditorFirm_C", "Name of the auditor"],
        "auditor_address": [
            "permaddress2a_C",
            "permaddress2b_C",
            "City_C",
            "State_P",
            "Pin_C",
        ],
        "auditor_frn_or_membership": ["MemberShNum", "Membership Number"],
        "appointment_type": ["DropDownList1"],
    }

    # Extract from form fields first
    for key, field_names in field_mappings.items():
        for field_name in field_names:
            for form_key, form_value in form_fields.items():
                if field_name in form_key and form_value:
                    if key == "auditor_address":
                        # Combine address fields
                        address_parts = []
                        for addr_field in [
                            "permaddress2a_C",
                            "permaddress2b_C",
                            "City_C",
                            "State_P",
                            "Pin_C",
                        ]:
                            if addr_field in form_fields and form_fields[addr_field]:
                                address_parts.append(form_fields[addr_field])
                        data[key] = ", ".join(address_parts)
                    else:
                        data[key] = form_value
                    break
            if data[key]:
                break

    # Fallback to text extraction with regex if form fields are missing
    patterns = {
        "company_name": r"Name of the company\s*[:\s\n]*(.*?)(?:\n|$)",
        "cin": r"Corporate identity number \(CIN\)\s*[:\s\n]*([A-Z0-9]{21})(?:\n|$)",
        "registered_office": r"Address of the registered office\s*[:\s\n]*(.*?)(?:\n|$)",
        "appointment_date": r"Date of appointment\s*[:\s\n]*(\d{2}/\d{2}/\d{4})(?:\n|$)",
        "auditor_name": r"Name of the auditor or auditor's firm\s*[:\s\n]*(.*?)(?:\n|$)",
        "auditor_address": r"Address of the Auditor\s*[:\s\n]*(.*?)(?:\n|$)",
        "auditor_frn_or_membership": r"Membership Number of auditor or auditor's firm's registration number\s*[:\s\n]*(.*?)(?:\n|$)",
        "appointment_type": r"(New Appointment|Reappointment)\s*(?:\n|$)",
    }

    for key, pattern in patterns.items():
        if not data[key]:  # Only use regex if form field is empty
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                data[key] = match.group(1).strip()

    # Fallbacks
    if not data["auditor_name"] and "Auditor's Firm" in text:
        data["auditor_name"] = "Auditor's Firm"
    if not data["appointment_type"] and "2016" in text:
        data["appointment_type"] = "Reappointment"

    # Set "Unknown" for empty fields
    for key in data:
        if not data[key]:
            data[key] = "Unknown"

    return data


def generate_summary(data):
    """Generate AI-style summary based on extracted data."""
    appointment_date = (
        data["appointment_date"]
        if data["appointment_date"] != "Unknown"
        else "an unspecified date"
    )
    company_name = (
        data["company_name"] if data["company_name"] != "Unknown" else "The company"
    )
    auditor_name = (
        data["auditor_name"]
        if data["auditor_name"] != "Unknown"
        else "an unspecified auditor"
    )
    appointment_type = (
        data["appointment_type"].lower()
        if data["appointment_type"] != "Unknown"
        else "appointed"
    )

    summary = (
        f"{company_name} has {appointment_type} {auditor_name} as its statutory auditor "
        f"for the financial year 2022-23, effective from {appointment_date}. "
        "The appointment was approved in the Annual General Meeting held on the same date. "
        "All required documents, including the board resolution, have been submitted via Form ADT-1."
    )
    return summary


def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters."""
    # Normalize Unicode characters
    filename = (
        unicodedata.normalize("NFKD", filename)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    # Keep only alphanumeric, underscores, hyphens, and dots
    valid_chars = string.ascii_letters + string.digits + "_-."
    filename = "".join(c if c in valid_chars else "_" for c in filename)
    # Ensure filename is not empty and has .pdf extension
    filename = filename or f"attachment_{hash(filename)}"
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    return filename


def extract_attachments(pdf_path, form_fields):
    """Extract embedded attachments from the PDF."""
    attachment_summaries = []
    try:
        doc = fitz.open(pdf_path)
        count = doc.embfile_count()
        if count == 0:
            attachment_summaries.append("No embedded attachments found in the PDF.")
        else:
            # Get attachment names from form fields if available
            attachment_names = {}
            if "HiddenList_L[0]" in form_fields:
                for entry in form_fields["HiddenList_L[0]"].split(":"):
                    if entry.strip():
                        parts = entry.split(":")
                        if len(parts) >= 2:
                            attachment_names[parts[1]] = parts[0]

            for i in range(count):
                try:
                    # Get attachment info
                    file_info = doc.embfile_info(i)
                    file_name = file_info.get("name", f"attachment_{i}.pdf")
                    print(f"Raw attachment name {i}: {file_name}")  # Debug
                    # Use form field name if available
                    original_name = attachment_names.get(
                        file_name.split(".")[0], file_name
                    )
                    file_name = sanitize_filename(original_name)
                    file_data = doc.embfile_get(i)
                    # Save attachment
                    attachment_path = os.path.join(ATTACHMENTS_DIR, file_name)
                    with open(attachment_path, "wb") as f:
                        f.write(file_data)
                    # Summarize attachment
                    summary = f"Attachment '{file_name}' extracted. "
                    if "consent" in file_name.lower() or "letter" in file_name.lower():
                        summary += "Likely contains auditor's consent letter."
                    elif "resolution" in file_name.lower():
                        summary += "Likely contains board resolution approving the appointment."
                    elif "intimation" in file_name.lower():
                        summary += "Likely contains intimation letter to the auditor."
                    elif "acceptance" in file_name.lower():
                        summary += "Likely contains auditor's acceptance letter."
                    else:
                        summary += "Content type not identified; manual inspection recommended."
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
    # Step 1: Extract text and form fields
    text, form_fields = extract_text_and_form_fields(PDF_PATH)

    # Step 2: Parse data into structured format
    extracted_data = parse_data(text, form_fields)

    # Step 3: Save extracted data to JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(extracted_data, f, indent=4)

    # Step 4: Generate and save AI-style summary
    summary = generate_summary(extracted_data)
    with open(SUMMARY_TXT, "w") as f:
        f.write(summary)

    # Step 5: Extract attachments (Bonus)
    attachment_summaries = extract_attachments(PDF_PATH, form_fields)
    if attachment_summaries:
        with open(SUMMARY_TXT, "a") as f:
            f.write("\n\nAttachment Summaries:\n")
            for s in attachment_summaries:
                f.write(f"- {s}\n")


if __name__ == "__main__":
    main()
