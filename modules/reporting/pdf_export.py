#!/usr/bin/env python3
"""
pdf_export.py — Export PDF des rapports HTML
Usage : python3 pdf_export.py <rapport.html> [rapport.pdf]
"""

import sys
import os
import argparse
from datetime import datetime

def export_pdf(html_path, pdf_path=None):
    try:
        from weasyprint import HTML, CSS
        WEASYPRINT = True
    except ImportError:
        WEASYPRINT = False

    if not os.path.exists(html_path):
        print(f"[x] Fichier introuvable : {html_path}")
        sys.exit(1)

    if not pdf_path:
        pdf_path = html_path.replace(".html", ".pdf")

    print(f"[*] Conversion → {pdf_path}")

    if WEASYPRINT:
        # CSS supplémentaire pour l'impression PDF
        print_css = CSS(string="""
            @page {
                size: A4;
                margin: 1.5cm 1.5cm 2cm 1.5cm;
                @bottom-center {
                    content: "Security Toolbox — Page " counter(page) " / " counter(pages);
                    font-size: 10px;
                    color: #999;
                }
            }
            body {
                font-size: 12px;
            }
            pre {
                max-height: none !important;
                overflow: visible !important;
                font-size: 9px;
                page-break-inside: avoid;
            }
            .section {
                page-break-inside: avoid;
            }
            header {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
            .stats {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
        """)
        HTML(filename=html_path).write_pdf(pdf_path, stylesheets=[print_css])
        size = os.path.getsize(pdf_path)
        print(f"[+] PDF généré → {pdf_path} ({size//1024} Ko)")
    else:
        # Fallback : conversion basique sans weasyprint
        print("[!] weasyprint non disponible — export HTML uniquement")
        print(f"[i] Installez weasyprint : pip install weasyprint")
        sys.exit(1)

def export_all(output_dir):
    """Convertit tous les rapports HTML d'un dossier en PDF"""
    import glob
    html_files = glob.glob(os.path.join(output_dir, "**", "report*.html"), recursive=True)
    if not html_files:
        print("[!] Aucun rapport HTML trouvé")
        return
    print(f"[*] {len(html_files)} rapport(s) trouvé(s)")
    for f in html_files:
        export_pdf(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export PDF des rapports Security Toolbox")
    parser.add_argument("--html",   help="Fichier HTML à convertir")
    parser.add_argument("--pdf",    help="Fichier PDF de sortie (optionnel)")
    parser.add_argument("--all",    help="Convertir tous les rapports d'un dossier")
    args = parser.parse_args()

    if args.all:
        export_all(args.all)
    elif args.html:
        export_pdf(args.html, args.pdf)
    else:
        parser.print_help()
        sys.exit(1)
