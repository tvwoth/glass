"""
Configuration helper functions for parsing and applying parameters.
"""
from typing import Any, Optional


def parse_h_params(form) -> dict[str, Optional[float]]:
    """Parse H-parameters from form data."""
    def parse_float(key: str) -> Optional[float]:
        raw = form.get(key)
        if raw is None or raw == '':
            return None
        return float(raw)

    j_x = -abs(parse_float('j_x')) if form.get('j_x') else None
    c_x = -abs(parse_float('c_x')) if form.get('c_x') else None
    return {
        'j_x': j_x,
        'c_x': c_x,
        'cd_len': parse_float('cd_len'),
        'de_len': parse_float('de_len'),
        'fg_len': parse_float('fg_len'),
        'gh_len': parse_float('gh_len'),
        'hi_len': parse_float('hi_len'),
        'jk_len': parse_float('jk_len'),
        'hcor': parse_float('hcor'),
    }


def apply_h_params(calculator, params: dict[str, Optional[float]]) -> None:
    """Apply configuration parameters to calculator."""
    calculator.set_j_x(params['j_x'])
    calculator.set_c_x(params['c_x'])
    calculator.set_cd_len(params['cd_len'])
    calculator.set_de_len(params['de_len'])
    calculator.set_fg_len(params['fg_len'])
    calculator.set_gh_len(params['gh_len'])
    calculator.set_hi_len(params['hi_len'])
    calculator.set_jk_len(params['jk_len'])
    calculator.set_hcor(params['hcor'])