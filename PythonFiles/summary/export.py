
import os
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import matplotlib.pyplot as plt

def export_summary_to_pdf(player_name: str, summary_text: str, plot_funcs: list, 
                          output_dir: str = None) -> str:
    """Export summary and plots to a PDF file."""
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'exports'))

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{player_name.replace(' ', '_')}_summary_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    with PdfPages(filepath) as pdf:
        # Add summary text page
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        ax.text(0.05, 0.95, summary_text, va='top', wrap=True, fontsize=10)
        pdf.savefig(fig)
        plt.close(fig)

        # Add each plot
        for plot_func in plot_funcs:
            fig, ax = plt.subplots()
            plot_func(ax)
            pdf.savefig(fig)
            plt.close(fig)

    return filepath
