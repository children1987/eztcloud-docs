import html
import re
import subprocess
from datetime import datetime
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
SITE_DIR = ROOT / "site"
OUT_DIR = ROOT / "deliverables"
COMBINED_HTML = SITE_DIR / "combined_for_pdf.html"
OUT_PDF = OUT_DIR / "EZtCloud文档中心-交付版.pdf"


def flatten_nav(nav, out):
    for item in nav:
        if isinstance(item, dict):
            for title, value in item.items():
                if isinstance(value, str) and value.lower().endswith(".md"):
                    out.append((title, value))
                elif isinstance(value, list):
                    flatten_nav(value, out)


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\-\u4e00-\u9fff]", "", s)
    return s or "section"


def md_to_html(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=[
            "extra",
            "toc",
            "tables",
            "fenced_code",
            "codehilite",
            "attr_list",
            "md_in_html",
            "pymdownx.superfences",
        ]
    )
    return md.convert(md_text)


def find_edge() -> str:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    raise FileNotFoundError("未找到 Microsoft Edge，可执行文件不存在")


def build_cover() -> str:
    date_text = datetime.now().strftime("%Y-%m-%d")
    return f"""
<section class=\"cover\">
  <img class=\"cover-logo\" src=\"{(OUT_DIR / 'logo_for_pdf.png').resolve().as_uri()}\" alt=\"logo\" />
  <h1>EZtCloud 文档中心</h1>
  <div class=\"meta\">
    <p><strong>文档类型：</strong>产品使用与接口文档</p>
    <p><strong>生成日期：</strong>{date_text}</p>
  </div>
</section>
"""


def build_toc(pages):
    items = []
    for idx, (title, _) in enumerate(pages, start=1):
        anchor = f"sec-{idx}-{slugify(title)}"
        items.append(f"<li><a href=\"#{anchor}\">{html.escape(title)}</a></li>")

    return f"""
<section class=\"toc-section\">
  <h1>目录</h1>
  <ul class=\"toc\">
    {''.join(items)}
  </ul>
</section>
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    mkdocs_yml = ROOT / "mkdocs.yml"
    cfg = yaml.unsafe_load(mkdocs_yml.read_text(encoding="utf-8"))
    nav = cfg.get("nav", [])

    pages = []
    flatten_nav(nav, pages)

    parts = [build_cover(), build_toc(pages)]
    for idx, (title, md_rel) in enumerate(pages, start=1):
        md_path = DOCS_DIR / md_rel
        if not md_path.exists():
            continue

        text = md_path.read_text(encoding="utf-8")
        body_html = md_to_html(text)

        anchor = f"sec-{idx}-{slugify(title)}"
        safe_title = html.escape(title)
        section_html = f"""
<section class=\"doc-section\" id=\"{anchor}\">
  <div class=\"doc-head\">{safe_title}</div>
  <h1>{safe_title}</h1>
  {body_html}
</section>
"""
        parts.append(section_html)

    base_href = DOCS_DIR.resolve().as_uri() + "/"

    final_html = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>EZtCloud文档中心（交付版）</title>
  <base href=\"{base_href}\" />
  <style>
    @page {{ size: A4; margin: 16mm 14mm; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; color: #1f2937; line-height: 1.6; font-size: 12px; margin: 0; background: #fff; }}
    h1, h2, h3, h4 {{ color: #0f172a; page-break-after: avoid; }}
    h1 {{ font-size: 24px; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin: 0 0 14px; }}
    h2 {{ font-size: 18px; margin-top: 22px; }}
    h3 {{ font-size: 15px; margin-top: 18px; }}
    p, li {{ orphans: 3; widows: 3; }}
    pre {{ background: #f7f7f9; border: 1px solid #eee; border-radius: 6px; padding: 10px; overflow: auto; white-space: pre-wrap; word-break: break-word; }}
    code {{ font-family: Consolas, "Courier New", monospace; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 6px 8px; vertical-align: top; }}
    img {{ max-width: 100%; height: auto; }}
    a {{ color: #0b5bd3; text-decoration: none; }}
    .cover {{ min-height: 255mm; padding: 28mm 8mm 0; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; page-break-after: always; border: 1px solid #e5e7eb; }}
    .cover-logo {{ width: 160px; margin-bottom: 18mm; }}
    .cover .subtitle {{ font-size: 18px; color: #4b5563; margin-top: 6px; }}
    .cover .meta {{ margin-top: 22mm; text-align: left; width: 78%; font-size: 14px; }}
    .toc-section {{ page-break-after: always; }}
    .toc {{ list-style: none; padding: 0; margin: 0; }}
    .toc li {{ padding: 6px 0; border-bottom: 1px dotted #d1d5db; font-size: 14px; }}
    .doc-section {{ page-break-before: always; position: relative; }}
    .doc-head {{ position: absolute; top: -10mm; right: 0; font-size: 10px; color: #9ca3af; }}
  </style>
</head>
<body>
{''.join(parts)}
</body>
</html>
"""

    COMBINED_HTML.write_text(final_html, encoding="utf-8")

    edge = find_edge()
    cmd = [
        edge,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(OUT_PDF)}",
        COMBINED_HTML.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True)

    print(str(OUT_PDF))


if __name__ == "__main__":
    main()
