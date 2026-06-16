"""
CSV export for calculation results.
"""
import csv
from typing import Dict, Any


def export_csv(result: Dict[str, Any], output_path: str) -> None:
    """
    Export calculation results to CSV file.
    
    Args:
        result: Calculation result dictionary from calculate()
        output_path: Path to save the CSV file
    """
    points = result.get("points", [])
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Параметр", "Значение"])
        writer.writerow(["n1", result.get("n1")])
        writer.writerow(["n2", result.get("n2")])
        writer.writerow(["n3", result.get("n3")])
        writer.writerow(["n4", result.get("n4")])
        writer.writerow(["angle_EF", result.get("angle_EF")])
        writer.writerow(["angle_D", result.get("angle_D")])
        writer.writerow([])
        writer.writerow(["Точка", "X", "Y"])
        for label, (x, y) in zip(labels, points):
            writer.writerow([label, f"{x:.4f}", f"{y:.4f}"])