"""
Core calculation interface.
This module is a THIN WRAPPER around the new core ContourCalculator.

The mathematical logic is entirely in calculator.py (ContourCalculator class).
calculate.py provides a functional (stateless) interface for convenience.

WARNING: Do NOT put any mathematical logic directly in this file.
All calculations must go through the ContourCalculator class.
"""
import math
from typing import Optional, Dict, List, Tuple

from .calculator import ContourCalculator


def calculate(input_data: Dict, config: Dict) -> Dict:
    """
    Main calculation function. Accepts input parameters and configuration,
    returns calculated geometry.
    
    This is a thin wrapper around ContourCalculator.
    
    Args:
        input_data: {'n1': float|None, 'n2': float|None, 'n4': float|None, 'angle_EF': float|None}
        config: Configuration with geometry parameters
            Valid keys: j_x, c_x, cd_len, de_len, fg_len, gh_len, hi_len, jk_len, hcor, rev
        
    Returns:
        Dictionary with calculated n1, n2, n4, angle_EF, angle_D, alpha, points
    """
    # Extract input parameters
    n1 = input_data.get("n1")
    n2 = input_data.get("n2")
    n4 = input_data.get("n4")
    angle_EF = input_data.get("angle_EF")
    
    # Create calculator instance and apply config
    calc = ContourCalculator()
    _apply_config(calc, config)
    
    rev = config.get("rev", False)
    calc.set_directions(REV=rev)
    
    # Perform calculation
    points = calc.calculate(n1, n2, n4, angle_EF)
    
    return {
        "n1": calc.n1,
        "n2": calc.n2,
        "n4": calc.n4,
        "n3": calc.get_n3(),
        "angle_EF": calc.angle_EF,
        "angle_D": calc.angle_D,
        "alpha": calc.alpha,
        "points": points,
    }


def _apply_config(calc: ContourCalculator, config: Dict) -> None:
    """Apply configuration parameters to calculator."""
    # Note: parse_h_params in config_service.py applies -abs() to j_x and c_x
    # This function does NOT apply that transformation - it uses values as-is.
    # The sign handling is done at the UI/API layer, not in the math core.
    
    if "j_x" in config and config["j_x"] is not None:
        calc.set_j_x(config["j_x"])
    if "c_x" in config and config["c_x"] is not None:
        calc.set_c_x(config["c_x"])
    if "cd_len" in config and config["cd_len"] is not None:
        calc.set_cd_len(config["cd_len"])
    if "de_len" in config and config["de_len"] is not None:
        calc.set_de_len(config["de_len"])
    if "fg_len" in config and config["fg_len"] is not None:
        calc.set_fg_len(config["fg_len"])
    if "gh_len" in config and config["gh_len"] is not None:
        calc.set_gh_len(config["gh_len"])
    if "hi_len" in config and config["hi_len"] is not None:
        calc.set_hi_len(config["hi_len"])
    if "jk_len" in config and config["jk_len"] is not None:
        calc.set_jk_len(config["jk_len"])
    if "hcor" in config and config["hcor"] is not None:
        calc.set_hcor(config["hcor"])