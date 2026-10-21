"""Build the single-file HTML report from site.json.

Usage:
    python3 build_report.py <path/to/site.json> [output.html]

Embeds site.json into assets/report-template.html and writes index.html next to
site.json (or to the given output path). Warns about screenshot / wireframe
paths that do not exist so broken images are caught before opening the report.
"""
import json
import os
import sys

PLACEHOLDER = "/*__SITE_DATA__*/null"
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "report-template.html")


def referenced_paths(data):
    def shots(block):
        return [shot.get("src") for shot in (block or {}).get("shots", [])]

    paths = shots(data.get("global"))
    for page in data.get("pages", []):
        paths += shots(page)
        if page.get("sections"):
            paths.append(f"wireframes/{page['id']}.svg")
    paths += [item.get("image") for item in (data.get("tokens") or {}).get("components", [])]
    return [path for path in paths if path]


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    data_path = os.path.abspath(argv[1])
    base_dir = os.path.dirname(data_path)
    out_path = os.path.abspath(argv[2]) if len(argv) > 2 else os.path.join(base_dir, "index.html")

    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    for key in ("site", "pages"):
        if key not in data:
            print(f"site.json is missing required key: {key}", file=sys.stderr)
            return 1

    missing = [path for path in referenced_paths(data) if not os.path.exists(os.path.join(base_dir, path))]
    for path in missing:
        print(f"warning: missing file referenced by site.json: {path}", file=sys.stderr)

    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()
    if PLACEHOLDER not in template:
        print("template placeholder not found", file=sys.stderr)
        return 1
    # Escape "</" so page text such as "</script>" cannot terminate the inline script.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, payload)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{out_path} ({len(data['pages'])} pages, {len(missing)} missing files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
