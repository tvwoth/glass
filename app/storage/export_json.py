"""
JSON export for calculation results.
"""
import json
from typing import Dict, Any


def export_json(result: Dict[str, Any], output_path: str) -> None:
    """
    Export calculation results to JSON file.
    
    Args:
        result: Calculation result dictionary from calculate()
        output_path: Path to save the JSON file
    """
    serializable = {
        "n1": result.get("n1"),
        "n2": result.get("n2"),
        "n3": result.get("n3"),
        "n4": result.get("n4"),
        "angle_EF": result.get("angle_EF"),
        "angle_D": result.get("angle_D"),
        "points": [[float(x), float(y)] for x, y in result.get("points", [])],
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)