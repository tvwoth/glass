"""
PDF export for calculation results.
"""
import os
from typing import Dict, Any


def export_pdf(result: Dict[str, Any], output_path: str, image_path: str = None, config_name: str = None) -> None:
    """
    Export calculation results to PDF file.
    Includes date, app version, config name, parameters, results, and contour image.
    
    Uses matplotlib as PDF backend for simplicity.
    
    Args:
        result: Calculation result dictionary from calculate()
        output_path: Path to save the PDF file
        image_path: Optional path to contour image to embed
        config_name: Optional configuration name
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from datetime import datetime
    from app.version import APP_VERSION
    
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    fig.suptitle("Результаты расчёта контура", fontsize=16, fontweight='bold')
    
    # App version and date
    plt.figtext(0.1, 0.95, f"Версия: {APP_VERSION}", fontsize=10)
    plt.figtext(0.1, 0.93, f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", fontsize=10)
    
    # Config name
    if config_name:
        plt.figtext(0.1, 0.91, f"Конфигурация: {config_name}", fontsize=10)
    
    # Parameters
    params_text = (
        f"n1 = {result.get('n1', 'N/A')}\n"
        f"n2 = {result.get('n2', 'N/A')}\n"
        f"n3 = {result.get('n3', 'N/A')}\n"
        f"n4 = {result.get('n4', 'N/A')}\n"
        f"angle_EF = {result.get('angle_EF', 'N/A')}°\n"
        f"angle_D = {result.get('angle_D', 'N/A')}°"
    )
    plt.figtext(0.1, 0.85, f"Параметры:\n{params_text}", fontsize=10, verticalalignment='top')
    
    # Points
    points = result.get("points", [])
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    coords_text = "\n".join([f"{label}: ({p[0]:.2f}, {p[1]:.2f})" for label, p in zip(labels, points)])
    plt.figtext(0.1, 0.6, f"Координаты точек:\n{coords_text}", fontsize=9, verticalalignment='top')
    
    # Plot contour
    if points:
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.35])
        x = [p[0] for p in points] + [points[0][0]]
        y = [p[1] for p in points] + [points[0][1]]
        ax.plot(x, y, marker='o')
        for label, (px, py) in zip(labels, points):
            ax.annotate(label, (px, py), xytext=(5, 5), textcoords='offset points', fontsize=8)
        ax.grid(True)
        ax.invert_yaxis()
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
    
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)