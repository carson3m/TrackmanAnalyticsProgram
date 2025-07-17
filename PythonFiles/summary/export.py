from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from PIL import Image as PILImage
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
import os
import tempfile
from datetime import datetime

def export_summary_to_pdf(player_name, summary_text, plot_funcs, metrics_df=None):
    output_dir = "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/exports"
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{player_name}_summary_{date_str}.pdf"
    pdf_path = os.path.join(output_dir, filename)

    page_width, page_height = landscape(letter)
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
    elements = []

    # ---------- METRICS TABLE ----------
    if metrics_df is not None and not metrics_df.empty:
        data = [list(metrics_df.columns)] + metrics_df.astype(str).values.tolist()
        table = Table(data, repeatRows=1)

        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe4f0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ])
        for i in range(1, len(data)):
            bg_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
            style.add("BACKGROUND", (0, i), (-1, i), bg_color)

        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 20))

    # ---------- PLOT EXPORT ----------
    for i, plot_func in enumerate(plot_funcs):
        # Make large figure with good aspect ratio
        fig, ax = plt.subplots(figsize=(9, 5.5))  # roughly matches PDF layout
        plot_func(ax)
        fig.tight_layout()

        img_path = os.path.join(tempfile.gettempdir(), f"plot_temp_{i}.png")
        fig.savefig(img_path, dpi=100)
        plt.close(fig)

        # Read actual image size
        pil_img = PILImage.open(img_path)
        img_width_px, img_height_px = pil_img.size
        img_width_pts = img_width_px * 72 / 100
        img_height_pts = img_height_px * 72 / 100

        # Scale image down to fit inside PDF frame
        max_width = page_width - 100
        max_height = page_height - 350 if i == 0 else page_height - 100  # less room on page 1

        scale = min(max_width / img_width_pts, max_height / img_height_pts, 1.0)
        scaled_w = img_width_pts * scale
        scaled_h = img_height_pts * scale

        elements.append(Image(img_path, width=scaled_w, height=scaled_h))

        if i == 0 and len(plot_funcs) > 1:
            elements.append(PageBreak())

    doc.build(elements)
    return pdf_path
