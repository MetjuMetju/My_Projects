import os
import zipfile
import smtplib
import mimetypes
from email.message import EmailMessage
from pathlib import Path
import ssl
import json
import html

DOCUMENTS_DIR = Path.home() / "Documents/Backup"
BACKUP_ZIP = Path.home() / "my_bckp.zip"

# SMTP_SERVER = "smtp.gmail.com"
SMTP_SERVER = "mail2.gratex.com"

SMTP_PORT = 587  # Using STARTTLS port
EMAIL = "mstanik@gratex.com"

PASSWORD_FILE = Path.home() / "email_p.txt"
SUBJECT = "my_bckp.zip"

def get_email_password():
    try:
        with open(PASSWORD_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading password file: {e}")
        exit(1)

EMAIL_PASSWORD = get_email_password()

def get_directory_size(directory):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size

def list_files_with_sizes(directory):
    files_list = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = Path(dirpath) / f
            size_kb = os.path.getsize(fp) / 1024
            files_list.append((str(fp), size_kb))
    return files_list

def create_zip(source_dir, zip_file):
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, _, filenames in os.walk(source_dir):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, source_dir)
                zipf.write(filepath, arcname)

def send_email(zip_path):
    msg = EmailMessage()
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = SUBJECT
    msg.set_content("Attached is the backup of your Documents folder.")

    with open(zip_path, 'rb') as f:
        file_data = f.read()
        maintype, subtype = mimetypes.guess_type(zip_path)[0].split('/')
        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=zip_path.name)

    print("Connecting to SMTP with STARTTLS...")
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.set_debuglevel(1)
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print("Email sent.")

def parse_bookmarks(bookmark_node):
    """Recursively parse Chrome bookmark JSON nodes and generate HTML."""
    html_output = ""
    if bookmark_node.get("type") == "folder":
        name = html.escape(bookmark_node.get("name", ""))
        html_output += f'<DT><H3>{name}</H3>\n<DL><p>\n'
        for child in bookmark_node.get("children", []):
            html_output += parse_bookmarks(child)
        html_output += '</DL><p>\n'
    elif bookmark_node.get("type") == "url":
        name = html.escape(bookmark_node.get("name", ""))
        url = html.escape(bookmark_node.get("url", ""))
        html_output += f'<DT><A HREF="{url}">{name}</A>\n'
    return html_output

def convert_bookmarks_json_to_html(json_path, html_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON bookmarks file: {e}")
        return False

    html_header = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten by Chrome. -->
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
'''

    html_footer = '</DL><p>\n'

    roots = data.get("roots", {})
    html_content = ""
    for root_key in ["bookmark_bar", "other", "synced"]:
        if root_key in roots:
            html_content += parse_bookmarks(roots[root_key])

    full_html = html_header + html_content + html_footer

    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(full_html)
    except Exception as e:
        print(f"Error writing HTML bookmarks file: {e}")
        return False

    print(f"Converted '{json_path}' to HTML bookmarks file '{html_path}'")
    return True

if __name__ == "__main__":
    # Paths for bookmarks JSON and output HTML
    chrome_bookmarks_json = DOCUMENTS_DIR / "bookmarks/Bookmarks"
    bookmarks_html = DOCUMENTS_DIR / "bookmarks/Bookmarks.html"

    # Convert bookmarks JSON to HTML for backup
    if chrome_bookmarks_json.exists():
        convert_bookmarks_json_to_html(chrome_bookmarks_json, bookmarks_html)
    else:
        print(f"Bookmarks JSON file not found at {chrome_bookmarks_json}")

    # List files before backup
    print("\n--- PREVIEW FILE LIST FOR BACKUP ---\n")
    files = list_files_with_sizes(DOCUMENTS_DIR)
    print("Files to back up:")
    for filepath, size_kb in sorted(files):
        print(f" - {filepath}  ({size_kb:.1f} KB)")

    size_bytes = get_directory_size(DOCUMENTS_DIR)
    size_mb = size_bytes / (1024 * 1024)
    print(f"\nTotal directory size: {size_mb:.2f} MB")

    proceed = input("Proceed with backup? (y/n): ").strip().lower()
    if proceed != "y":
        print("Backup canceled.")
        exit(0)

    print("\nCreating zip archive...")
    create_zip(DOCUMENTS_DIR, BACKUP_ZIP)

    print(f"Sending {BACKUP_ZIP.name} to {EMAIL}...")
    send_email(BACKUP_ZIP)

    print("Done.")

