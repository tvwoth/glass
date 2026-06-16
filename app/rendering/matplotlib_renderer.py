"""
Matplotlib-based renderer for contour visualization.
No mathematical logic - only visualization.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Tuple


def render(points: List[Tuple[float, float]], output_path: str = "plot.png") -> None:
    """
    Render contour points as a plot image.
    
    Args:
        points: List of 11 (x, y) coordinate tuples (A through K)
        output_path: Path to save the PNG image
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(6, 4))
    x = [p[0] for p in points] + [points[0][0]]
    y = [p[1] for p in points] + [points[0][1]]
    ax.plot(x, y, marker='o')
    
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    for label, (px, py) in zip(labels, points):
        ax.annotate(label, (px, py), xytext=(5, 5), textcoords='offset points')
    
    coords_text = "\n".join([f"{label}: ({p[0]:.2f}, {p[1]:.2f})" for label, p in zip(labels, points)])
    ax.text(0.05, 0.95, coords_text, transform=ax.transAxes, fontsize=8, verticalalignment='top')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)
    ax.invert_yaxis()
    
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)
    x_margin = (x_max - x_min) * 0.1 or 50
    y_margin = (y_max - y_min) * 0.1 or 50
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)