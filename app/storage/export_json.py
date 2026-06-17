"""
JSON export for calculation results.
"""
import json
from typing import Dict, Any
from datetime import datetime


def export_json(result: Dict[str, Any], output_path: str, metadata: Dict[str, Any] = None) -> None:
    """
    Export calculation results to JSON file.
    
    Args:
        result: Calculation result dictionary from calculate()
        output_path: Path to save the JSON file
        metadata: Optional metadata dict with keys: app_version, timestamp, config_name, config, input
    """
    from app.version import APP_VERSION
    
    serializable = {
        "app_version": APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "config_name": metadata.get("config_name") if metadata else None,
        "config": metadata.get("config", {}) if metadata else {},
        "input": metadata.get("input", {}) if metadata else {},
        "result": {
            "n1": result.get("n1"),
            "n2": result.get("n2"),
            "n3": result.get("n3"),
            "n4": result.get("n4"),
            "angle_EF": result.get("angle_EF"),
            "angle_D": result.get("angle_D"),
            "points": [[float(x), float(y)] for x, y in result.get("points", [])],
        }
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
