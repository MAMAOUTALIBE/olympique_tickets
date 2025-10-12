#!/usr/bin/env python3
"""
Convertit un fichier Markdown en PDF à l'aide de xhtml2pdf.

Usage :
    python tools/export_markdown_pdf.py chemin/source.md chemin/cible.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path

from base64 import b64encode

from markdown import markdown
from xhtml2pdf import pisa


DEFAULT_LOGO_CANDIDATES = [
    Path("im/anneau.png"),
    Path("static/im/anneau.png"),
    Path("static/img/anneau.png"),
    Path("static/admin/assets/img/anneau.png"),
    Path("static/admin/assets/img/anneaux.png"),
]


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.5;
            margin: 2cm;
            color: #222;
        }}
        h1, h2, h3 {{
            color: #0b5394;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 6px 8px;
            text-align: left;
        }}
        pre {{
            background: #f4f4f4;
            padding: 8px;
            overflow: auto;
        }}
        code {{
            font-family: "Courier New", Courier, monospace;
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            margin-bottom: 24px;
            border-bottom: 2px solid #0b5394;
            padding-bottom: 12px;
        }}
        .logo {{
            height: 80px;
            width: auto;
            margin-right: 18px;
            display: block;
        }}
        .header-text {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .header-title {{
            font-size: 18pt;
            font-weight: bold;
            color: #0b5394;
            margin: 0;
        }}
        .header-subtitle {{
            font-size: 12pt;
            color: #555;
            margin: 4px 0 0 0;
        }}
        main {{
            margin-top: 16px;
        }}
    </style>
</head>
<body>
{header}
<main>
{body}
</main>
</body>
</html>
"""


def resolve_logo_path() -> Path | None:
    for candidate in DEFAULT_LOGO_CANDIDATES:
        if candidate.exists():
            return candidate.resolve()
    return None


def build_header_html() -> str:
    logo_path = resolve_logo_path()
    if not logo_path:
        return ""

    suffix = logo_path.suffix.lower()
    mime_type = "image/png"
    if suffix in {".jpg", ".jpeg"}:
        mime_type = "image/jpeg"
    elif suffix == ".svg":
        mime_type = "image/svg+xml"

    with logo_path.open("rb") as image_file:
        encoded_logo = b64encode(image_file.read()).decode("ascii")

    img_tag = (
        f'<img class="logo" src="data:{mime_type};base64,{encoded_logo}" '
        f'alt="Logo Jeux Olympiques" />'
    )
    header = "".join(
        [
            "<div class=\"header\">",
            img_tag,
            "<div class=\"header-text\">",
            "<p class=\"header-title\">Jeux Olympiques</p>",
            "<p class=\"header-subtitle\">Rapport de couverture des tests automatisés</p>",
            "</div>",
            "</div>",
        ]
    )
    return header


def convert_markdown_to_pdf(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {source}")

    markdown_text = source.read_text(encoding="utf-8")
    html_body = markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code"],
    )
    header_html = build_header_html()
    full_html = TEMPLATE.format(body=html_body, header=header_html)

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as output:
        result = pisa.CreatePDF(src=full_html, dest=output, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"Erreur lors de la génération du PDF : {result.err}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 1

    source = Path(argv[1]).resolve()
    target = Path(argv[2]).resolve()

    try:
        convert_markdown_to_pdf(source, target)
    except Exception as exc:  # pragma: no cover - rapporter clairement l'erreur
        print(f"[ERREUR] {exc}", file=sys.stderr)
        return 1

    print(f"PDF généré : {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
