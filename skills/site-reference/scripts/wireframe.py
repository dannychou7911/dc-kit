"""Generate schematic layout wireframes (SVG) from site.json.

Usage:
    python3 wireframe.py <path/to/site.json> [page ids...]

Writes <site.json dir>/wireframes/<page-id>.svg. Each section row aligns the
desktop and mobile blocks with the same number; heights are compressed (not to
scale) and the measured height is printed on each block. Section layouts are
documented in references/site-data-schema.md.
"""
import json
import math
import os
import sys
from xml.sax.saxutils import escape

FONT = "PingFang TC, Noto Sans TC, Microsoft JhengHei, Helvetica, Arial, sans-serif"
C_IMG, C_IMG_LINE = "#d4d8de", "#a3abb7"
C_TEXT, C_HEAD = "#cbd2db", "#7b8594"
C_INK, C_MUTED = "#1e293b", "#64748b"

MARGIN, D_W, GAP, M_W = 24, 480, 48, 190
LABEL_H = 30  # band reserved for the number badge and name
CAPTION_H = 16

out = []
accent = "#ffcc00"
accent_ink = "#111111"


# ------------------------------------------------------------------ primitives
def rect(x, y, w, h, fill, rx=0, stroke="none", dash=None, opacity=1):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" '
               f'fill="{fill}" stroke="{stroke}"{dash_attr} fill-opacity="{opacity}"/>')


def text(x, y, s, size=12, fill=C_INK, weight="normal", anchor="start"):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
               f'text-anchor="{anchor}" font-family="{FONT}">{escape(str(s))}</text>')


def text_width(s, size):
    return sum(size if ord(ch) > 0x2E80 else size * 0.58 for ch in str(s))


def fit(s, size, max_w):
    s = str(s)
    if text_width(s, size) <= max_w:
        return s
    while s and text_width(s + "…", size) > max_w:
        s = s[:-1]
    return s + "…"


def img(x, y, w, h, rx=4):
    if w <= 2 or h <= 2:
        return
    rect(x, y, w, h, C_IMG, rx)
    out.append(f'<path d="M{x:.1f},{y:.1f} L{x + w:.1f},{y + h:.1f} M{x + w:.1f},{y:.1f} L{x:.1f},{y + h:.1f}" '
               f'stroke="{C_IMG_LINE}" stroke-width="1"/>')


def lines(x, y, w, n, gap=9, center=False):
    for i in range(n):
        lw = w * (0.6 if i == n - 1 and n > 1 else 1)
        lx = x + (w - lw) / 2 if center else x
        rect(lx, y + i * gap, lw, 4, C_TEXT, 2)


def heading(x, y, w, h=9):
    rect(x, y, w, h, C_HEAD, 3)


def button(x, y, w, h=14):
    rect(x, y, w, h, accent, h / 2)


def circle(cx, cy, r, fill):
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>')


def logo(x, y, w, h):
    rect(x, y, w, h, "#e5e7eb", 3, stroke="#c7ccd4")


def frame(x, y, w, h, dark=False, shade=False):
    fill = "#1f2937" if dark else ("#f5f6f8" if shade else "#ffffff")
    rect(x, y, w, h, fill, 0, stroke="#9aa3af", dash="4 3")


def badge(x, y, w, num, name, real, dark=False):
    circle(x + 13, y + 13, 10, accent)
    text(x + 13, y + 17, num, 11, accent_ink, "bold", "middle")
    real_w = text_width(real, 10) + 10
    text(x + 28, y + 17, fit(name, 12, w - 34 - real_w), 12, "#ffffff" if dark else C_INK, "bold")
    text(x + w - 6, y + 17, real, 10, "#cbd5e1" if dark else C_MUTED, anchor="end")


def grid_cells(x, y, w, h, cols, rows, gap=8, limit=None):
    cols, rows = max(cols, 1), max(rows, 1)
    cw = (w - gap * (cols - 1)) / cols
    ch = (h - gap * (rows - 1)) / rows
    for r in range(rows):
        for c in range(cols):
            if limit is not None and r * cols + c >= limit:
                return
            yield x + c * (cw + gap), y + r * (ch + gap), cw, ch


# ------------------------------------------------------------------ layouts
# Each draws inside the content box (x, y, w, h) below the label band.
def draw_nav(x, y, w, h, spec, mobile):
    cy = y + h / 2
    rect(x + 12, cy - 7, 44 if mobile else 56, 14, accent, 3)
    if mobile:
        for i in range(3):
            rect(x + w - 28, cy - 6 + i * 5, 16, 2.5, C_HEAD, 1)
    else:
        for i in range(6):
            rect(x + w - 250 + i * 32, cy - 2, 24, 4, C_HEAD, 2)
        rect(x + w - 50, cy - 7, 38, 14, "#ffffff", 7, stroke=C_HEAD)


def draw_hero(x, y, w, h, spec, mobile):
    img(x, y, w, h, 0)
    bw = min(w * 0.6, 220)
    rect(x + (w - bw) / 2, y + h / 2 - 22, bw, 12, "#8f98a6", 3)
    rect(x + (w - bw * 0.7) / 2, y + h / 2 - 4, bw * 0.7, 5, "#b6bdc8", 2)
    button(x + (w - 80) / 2, y + h / 2 + 10, 80)


def draw_carousel(x, y, w, h, spec, mobile):
    img(x, y, w, h - 12, 0)
    mid = y + (h - 12) / 2 + 5
    text(x + 8, mid, "‹", 16, C_INK, "bold")
    text(x + w - 8, mid, "›", 16, C_INK, "bold", "end")
    for i in range(5):
        circle(x + w / 2 - 20 + i * 10, y + h - 5, 2.5, accent if i == 0 else C_TEXT)


def draw_banner(x, y, w, h, spec, mobile):
    img(x, y, w, h, 0)
    rect(x + (w - 140) / 2 if not mobile else x + (w - 100) / 2, y + h / 2 - 6, 140 if not mobile else 100, 12, "#8f98a6", 3)


def draw_text(x, y, w, h, spec, mobile):
    heading(x + (w - 120) / 2, y + 6, 120, 10)
    n = spec.get("rows") or max(2, min(8, int((h - 30) // 10)))
    lines(x + w * 0.12, y + 26, w * 0.76, n, center=True)


def draw_split(x, y, w, h, spec, mobile):
    pad = 12
    if mobile:
        ih = h * 0.45
        img(x + pad, y + 4, w - pad * 2, ih)
        ty = y + ih + 14
        heading(x + (w - 100) / 2, ty, 100, 9)
        n = max(1, min(8, int((h - ih - 50) // 9)))
        lines(x + pad, ty + 18, w - pad * 2, n, center=True)
        return
    half = (w - pad * 3) / 2
    left, right = (x + pad, x + pad * 2 + half)
    image_x, text_x = (right, left) if spec.get("reverse") else (left, right)
    img(image_x, y + 4, half, h - 8)
    ty = y + max(8, h / 2 - 40)
    heading(text_x, ty, half * 0.7, 10)
    lines(text_x, ty + 20, half, max(2, min(6, int((h - 60) // 14))))
    button(text_x, ty + 20 + 6 * 9 + 8, 80)


def draw_cards(x, y, w, h, spec, mobile):
    cols, rows = spec["cols"], spec["rows"]
    pad = 10
    for cx, cy, cw, ch in grid_cells(x + pad, y + 4, w - pad * 2, h - 8, cols, rows, limit=spec.get("items")):
        img(cx, cy, cw, ch * 0.62)
        if ch > 30:
            heading(cx, cy + ch * 0.62 + 5, cw * 0.7, 5)
        if ch > 44:
            rect(cx, cy + ch * 0.62 + 14, cw * 0.9, 3, C_TEXT, 2)


def draw_icons(x, y, w, h, spec, mobile):
    cols, rows = spec["cols"], spec["rows"]
    for cx, cy, cw, ch in grid_cells(x + 14, y + 4, w - 28, h - 8, cols, rows, gap=14, limit=spec.get("items")):
        circle(cx + cw / 2, cy + 9, 8, "#fde68a")
        if ch > 26:
            heading(cx + cw * 0.15, cy + 22, cw * 0.7, 6)
        if ch > 40:
            lines(cx, cy + 34, cw, max(1, min(4, int((ch - 34) // 9))), center=True)


def draw_logos(x, y, w, h, spec, mobile):
    for cx, cy, cw, ch in grid_cells(x + 16, y + 6, w - 32, h - 12, spec["cols"], spec["rows"], gap=12, limit=spec.get("items")):
        lh = min(ch, 26)
        logo(cx, cy + (ch - lh) / 2, cw, lh)


def draw_list(x, y, w, h, spec, mobile):
    rows = spec["rows"]
    for cx, cy, cw, ch in grid_cells(x + 12, y + 4, w - 24, h - 8, 1, rows, gap=10):
        iw = min(cw * 0.32, ch * 1.6)
        img(cx, cy, iw, ch)
        heading(cx + iw + 10, cy + 4, (cw - iw - 10) * 0.6, 7)
        if ch > 26:
            lines(cx + iw + 10, cy + 18, cw - iw - 10, max(1, min(3, int((ch - 18) // 9))))


def draw_tabs(x, y, w, h, spec, mobile):
    tabs = max(spec.get("cols") or 4, 1)
    pad = 10
    tw = min(70, (w - pad * 2 - (tabs - 1) * 6) / tabs)
    for i in range(tabs):
        rect(x + pad + i * (tw + 6), y + 4, tw, 14, accent if i == 0 else "#e5e7eb", 7)
    box_y = y + 26
    rect(x + pad, box_y, w - pad * 2, h - 30, "#f8fafc", 4, stroke="#e2e8f0")
    inner = box_y + 8
    if mobile:
        img(x + pad + 8, inner, w - pad * 2 - 16, (h - 46) * 0.5)
        lines(x + pad + 8, inner + (h - 46) * 0.5 + 8, w - pad * 2 - 16, 3)
    else:
        half = (w - pad * 2 - 24) / 2
        img(x + pad + 8, inner, half, h - 46)
        heading(x + pad + 16 + half, inner + 4, half * 0.6, 8)
        lines(x + pad + 16 + half, inner + 20, half, max(2, min(6, int((h - 70) // 10))))


def draw_form(x, y, w, h, spec, mobile):
    fields = spec.get("rows") or 4
    pad = 16
    fw = w - pad * 2 if mobile else w * 0.6
    fx = x + (w - fw) / 2
    usable = h - 30
    step = min(26, usable / fields)
    for i in range(fields):
        rect(fx, y + 4 + i * step, fw * 0.3, 3, C_HEAD, 2)
        rect(fx, y + 10 + i * step, fw, max(step - 12, 6), "#ffffff", 3, stroke="#cbd5e1")
    button(fx, y + 6 + fields * step, 90)


def draw_cta(x, y, w, h, spec, mobile):
    heading(x + (w - 140) / 2, y + h / 2 - 18, 140, 10)
    button(x + (w - 96) / 2, y + h / 2 + 2, 96)


def draw_stats(x, y, w, h, spec, mobile):
    for cx, cy, cw, ch in grid_cells(x + 16, y + 4, w - 32, h - 8, spec["cols"], spec["rows"], gap=12, limit=spec.get("items")):
        rect(cx + cw * 0.2, cy + ch / 2 - 12, cw * 0.6, 14, C_HEAD, 3)
        rect(cx + cw * 0.3, cy + ch / 2 + 7, cw * 0.4, 4, C_TEXT, 2)


def draw_media(x, y, w, h, spec, mobile):
    img(x + 10, y + 4, w - 20, h - 8)


def draw_embed(x, y, w, h, spec, mobile):
    rect(x + 10, y + 4, w - 20, h - 8, "#eef2f7", 4, stroke="#94a3b8", dash="6 4")
    text(x + w / 2, y + h / 2 + 4, "嵌入內容", 11, C_MUTED, anchor="middle")


def draw_footer(x, y, w, h, spec, mobile):
    cols = 1 if mobile else (spec.get("cols") or 4)
    pad = 16
    body_h = h - 30
    for cx, cy, cw, ch in grid_cells(x + pad, y + 6, w - pad * 2, body_h, cols, 1, gap=20):
        rect(cx if not mobile else cx + cw / 2 - 30, cy, 60, 8, "#9ca3af", 2)
        n = max(1, min(5, int((ch - 16) // 10)))
        for i in range(n):
            lw = cw * 0.6
            rect(cx if not mobile else cx + (cw - lw) / 2, cy + 18 + i * 10, lw, 4, "#6b7280", 2)
    rect(x + 10, y + h - 20, w - 20, 1, "#4b5563")
    rect(x + w / 2 - 70, y + h - 12, 140, 4, "#6b7280", 2)


def draw_blank(x, y, w, h, spec, mobile):
    pass


LAYOUTS = {
    "nav": draw_nav, "hero": draw_hero, "carousel": draw_carousel, "banner": draw_banner,
    "text": draw_text, "split": draw_split, "cards": draw_cards, "icons": draw_icons,
    "logos": draw_logos, "list": draw_list, "tabs": draw_tabs, "form": draw_form,
    "cta": draw_cta, "stats": draw_stats, "media": draw_media, "embed": draw_embed,
    "footer": draw_footer, "blank": draw_blank,
}
GRID_LAYOUTS = {"cards", "icons", "logos", "stats"}
# Minimum content height so dense layouts stay readable.
MIN_CONTENT = {"nav": 22, "cards": 70, "icons": 70, "logos": 40, "list": 60, "tabs": 90, "form": 80,
               "split": 90, "footer": 70, "text": 40}


# ------------------------------------------------------------------ section model
def resolve(section, device):
    """Merge section-level settings with the device override."""
    spec = {k: v for k, v in section.items() if k not in ("desktop", "mobile")}
    override = section.get(device) or {}
    spec.update(override)
    spec.setdefault("layout", "blank")
    if spec["layout"] not in LAYOUTS:
        print(f"warning: unknown layout '{spec['layout']}' in section '{section.get('name')}', drawing as blank",
              file=sys.stderr)
        spec["layout"] = "blank"
    if spec["layout"] in GRID_LAYOUTS or spec["layout"] == "list":
        desktop = {**section, **(section.get("desktop") or {})}
        d_cols = desktop.get("cols") or (1 if spec["layout"] == "list" else 3)
        d_rows = desktop.get("rows") or 1
        # Total item count stays the same across devices; only the grid reflows.
        spec.setdefault("items", d_cols * d_rows)
        if device == "mobile" and "cols" not in override:
            spec["cols"] = 1 if spec["layout"] in ("icons", "list") else min(d_cols, 2)
        spec["cols"] = spec.get("cols") or d_cols
        if device == "mobile" and "rows" not in override:
            spec["rows"] = math.ceil(d_cols * d_rows / spec["cols"])
        spec["rows"] = spec.get("rows") or d_rows
        spec["drawn_rows"] = min(spec["rows"], 6)
        if spec["drawn_rows"] < spec["rows"]:
            spec["items"] = min(spec["items"], spec["cols"] * spec["drawn_rows"])
    return spec


def real_label(spec):
    if spec.get("hidden"):
        return "不顯示"
    h = spec.get("h")
    if isinstance(h, (int, float)):
        return f"{int(h):,}px"
    return str(h) if h else "—"


def schematic_height(spec):
    if spec.get("hidden"):
        return 60
    h = spec.get("h")
    base = 40 + math.sqrt(h) * 5.2 if isinstance(h, (int, float)) and h > 0 else 90
    layout = spec["layout"]
    if layout in GRID_LAYOUTS or layout == "list":
        per_row = {"cards": 46, "icons": 56, "logos": 26, "stats": 40, "list": 34}[layout]
        base = max(base, LABEL_H + spec["drawn_rows"] * per_row + 12)
    base = max(base, LABEL_H + MIN_CONTENT.get(layout, 30) + 8)
    if spec.get("caption"):
        base += CAPTION_H
    return round(min(max(base, 64), 420))


def draw_block(x, y, w, h, spec, num, name, mobile):
    if spec.get("hidden"):
        rect(x, y, w, h, "#f8fafc", 0, stroke="#cbd5e1", dash="2 4")
        badge(x, y, w, num, name, "不顯示")
        text(x + w / 2, y + h / 2 + 12, "此裝置不顯示", 10, C_MUTED, anchor="middle")
        return
    layout = spec["layout"]
    dark = layout == "footer"
    frame(x, y, w, h, dark=dark, shade=layout in ("cta", "stats", "logos"))
    content_h = h - LABEL_H - 6 - (CAPTION_H if spec.get("caption") else 0)
    draw_spec = dict(spec)
    if "drawn_rows" in spec:
        draw_spec["rows"] = spec["drawn_rows"]
    LAYOUTS[layout](x, y + LABEL_H, w, content_h, draw_spec, mobile)
    if spec.get("rows", 0) > spec.get("drawn_rows", spec.get("rows", 0)):
        text(x + w / 2, y + LABEL_H + content_h + 4, "⋮", 12, C_MUTED, "bold", "middle")
    if spec.get("caption"):
        text(x + w / 2, y + h - 6, fit(spec["caption"], 10, w - 12), 10,
             "#cbd5e1" if dark else C_MUTED, anchor="middle")
    badge(x, y, w, num, name, real_label(spec), dark)


# ------------------------------------------------------------------ page
def legend(x, y):
    img(x, y, 22, 14, 2); text(x + 28, y + 11, "圖片／影片", 11, "#475569")
    lines(x + 104, y + 2, 30, 2, gap=6); text(x + 140, y + 11, "文字", 11, "#475569")
    heading(x + 180, y + 3, 30, 8); text(x + 216, y + 11, "標題", 11, "#475569")
    button(x + 258, y + 1, 34, 12); text(x + 298, y + 11, "按鈕", 11, "#475569")
    logo(x + 340, y + 1, 30, 12); text(x + 376, y + 11, "logo", 11, "#475569")
    circle(x + 424, y + 7, 8, accent); text(x + 424, y + 11, "1", 9, accent_ink, "bold", "middle")
    text(x + 438, y + 11, "區塊編號（對應結構清單）", 11, "#475569")


def build_page(page, viewports, out_path):
    global out
    d_x, m_x = MARGIN, MARGIN + D_W + GAP
    width = m_x + M_W + MARGIN
    top = 118
    y = top
    body = []
    for index, section in enumerate(page.get("sections") or [], start=1):
        name = section.get("name", f"區塊 {index}")
        d_spec, m_spec = resolve(section, "desktop"), resolve(section, "mobile")
        d_h, m_h = schematic_height(d_spec), schematic_height(m_spec)
        out = []
        draw_block(d_x, y, D_W, d_h, d_spec, index, name, False)
        draw_block(m_x, y, M_W, m_h, m_spec, index, section.get("shortName", name), True)
        body.extend(out)
        y += max(d_h, m_h) + 14
    height = y + 24

    out = []
    rect(0, 0, width, height, "#fafafa")
    text(MARGIN, 34, fit(page.get("name", page["id"]), 20, width - MARGIN * 2), 20, C_INK, "bold")
    text(MARGIN, 56, "版面區塊示意圖：只表示區塊位置與排列，不含實際內容；高度依比例壓縮，右上角為實測高度。", 11, C_MUTED)
    legend(MARGIN, 72)
    text(d_x, top - 10, fit(f"Desktop（{viewports.get('desktop', '1440')}）", 13, D_W), 13, C_INK, "bold")
    text(m_x, top - 10, fit(f"Mobile（{viewports.get('mobile', '390')}）", 13, M_W), 13, C_INK, "bold")
    header = out

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}">\n' + "\n".join(header + body) + "\n</svg>\n")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(out_path, width, height)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    data_path = os.path.abspath(argv[1])
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    global accent, accent_ink
    options = data.get("options") or {}
    accent = options.get("accent", accent)
    accent_ink = options.get("accentInk", accent_ink)
    viewports = (data.get("site") or {}).get("viewports") or {}
    pages = {page["id"]: page for page in data.get("pages", [])}
    targets = argv[2:] or list(pages)
    missing = [page_id for page_id in targets if page_id not in pages]
    if missing:
        print(f"unknown page ids: {', '.join(missing)}", file=sys.stderr)
        return 1
    out_dir = os.path.join(os.path.dirname(data_path), "wireframes")
    os.makedirs(out_dir, exist_ok=True)
    for page_id in targets:
        if not pages[page_id].get("sections"):
            print(f"skip {page_id}: no sections", file=sys.stderr)
            continue
        build_page(pages[page_id], viewports, os.path.join(out_dir, f"{page_id}.svg"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
