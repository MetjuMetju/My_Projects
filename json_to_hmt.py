import json
from pathlib import Path
import sys
import html

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
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

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

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Converted '{json_path}' to importable HTML bookmarks file '{html_path}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 json_to_html.py /path/to/Bookmarks /path/to/output.html")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    html_path = Path(sys.argv[2])

    if not json_path.exists():
        print(f"Error: JSON file '{json_path}' does not exist.")
        sys.exit(1)

    convert_bookmarks_json_to_html(json_path, html_path)

