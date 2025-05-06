import os
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime


def export_summary_to_pdf(player_name, summary_text, plot_funcs, output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'exports'))):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{player_name.replace(' ', '_')}_summary_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    with PdfPages(filepath) as pdf:
        # Add a text-only summary page
        from matplotlib import pyplot as plt
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        wrapped = "\n".join(summary_text.split("\n"))
        ax.text(0.01, 0.99, wrapped, fontsize=10, va='top', ha='left', wrap=True)
        pdf.savefig(fig)
        plt.close(fig)

        # Add each plot on its own page
        for func in plot_funcs:
            fig, ax = plt.subplots(figsize=(6, 6) if "plot_strike_zone" in func.__code__.co_names else (6, 4))
            func(ax)
            pdf.savefig(fig, bbox_inches='tight')  # ✅ ensures the full plot (including legend) is saved
            plt.close(fig)

    return filepath
