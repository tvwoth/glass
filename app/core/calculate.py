import math
from typing import Optional, Dict, List, Tuple


def calculate(input_data: Dict, config: Dict) -> Dict:
    """
    Main calculation function. Accepts input parameters and configuration,
    returns calculated geometry.
    
    Args:
        input_data: {'n1': float|None, 'n2': float|None, 'n4': float|None, 'angle_EF': float|None}
        config: Configuration with geometry parameters
        
    Returns:
        Dictionary with calculated n1, n2, n4, angle_EF and points
    """
    # Extract input parameters
    n1 = input_data.get("n1")
    n2 = input_data.get("n2")
    n4 = input_data.get("n4")
    angle_EF = input_data.get("angle_EF")
    
    # Validate that exactly 3 parameters are provided
    params = {'n1': n1, 'n2': n2, 'n4': n4, 'angle_EF': angle_EF}
    given_params = sum(1 for v in params.values() if v is not None)
    if given_params != 3:
        raise ValueError("Необходимо ввести ровно три параметра")
    
    # Extract configuration parameters
    a_x = config.get("a_x", 0)
    a_y = config.get("a_y", 0)
    b_x = config.get("b_x", a_x)
    c_x = config.get("c_x", 0)
    d_x = config.get("d_x", c_x)
    cd_len = config.get("cd_len", 0)
    de_len = config.get("de_len", 0)
    fg_len = config.get("fg_len", 0)
    gh_len = config.get("gh_len", 0)
    hi_len = config.get("hi_len", 0)
    j_x = config.get("j_x", 0)
    jk_len = config.get("jk_len", 0)
    hcor = config.get("hcor", 0)
    k_x = config.get("k_x", j_x)
    k_y = config.get("k_y", a_y)
    rev = config.get("rev", False)
    
    # Validate input parameters
    if angle_EF is not None:
        if not (0 <= angle_EF <= 10):
            raise ValueError("Угол наклона должен быть в диапазоне 0°–10°")
        angle_D = 180 + angle_EF
    else:
        angle_D = None
    
    # Validate that at least one positive parameter is given
    for name, value in params.items():
        if value is not None and value <= 0 and name != 'angle_EF':
            raise ValueError(f"Длина {name} должна быть положительной")
    
    # Validate that configuration is not all zeros
    if all(v == 0 for v in [c_x, cd_len, de_len, fg_len, gh_len, hi_len, j_x, jk_len]):
        raise ValueError("Выберите конфигурацию или введите значения H")
    
    # Apply correction to n4
    if n4 is not None:
        n4 = n4 + hcor
    
    # Calculate missing parameters
    if n1 is None:
        n1 = _calculate_missing_n1(
            n2, n4, angle_EF, c_x, d_x, cd_len, de_len, fg_len, 
            gh_len, hi_len, j_x, k_y, jk_len, rev
        )
    elif n2 is None:
        n2 = _calculate_missing_n2(
            n1, n4, angle_EF, c_x, d_x, cd_len, de_len, fg_len, 
            gh_len, hi_len, j_x, k_y, jk_len, rev
        )
    elif n4 is None:
        n4 = _calculate_missing_n4(
            n1, n2, angle_EF, c_x, d_x, cd_len, de_len, fg_len, 
            gh_len, hi_len, j_x, k_y, jk_len, rev
        )
    elif angle_EF is None:
        angle_D = _calculate_missing_angle_D(
            n1, n2, n4, c_x, d_x, cd_len, de_len, fg_len, 
            gh_len, hi_len, j_x, k_y, jk_len, rev
        )
        angle_EF = angle_D - 180
    
    # Calculate alpha for point calculations
    alpha = 270 - angle_D
    
    # Calculate all points
    points = calculate_points(
        n1, n2, angle_D, a_x, a_y, b_x, c_x, d_x, cd_len, de_len, 
        fg_len, gh_len, hi_len, j_x, k_x, k_y, jk_len, alpha, rev
    )
    
    return {
        "n1": n1,
        "n2": n2,
        "n4": n4,
        "angle_EF": angle_EF,
        "angle_D": angle_D,
        "points": points
    }


def _calculate_points_to_i(
    n1: float, n2: float, angle_D: float,
    a_x: float, a_y: float, b_x: float, c_x: float, d_x: float,
    cd_len: float, de_len: float, fg_len: float, gh_len: float,
    hi_len: float, k_y: float, rev: bool
) -> List[Tuple[float, float]]:
    """Calculate points A through I based on n1, n2 and angle_D"""
    alpha_rad = math.radians(270 - angle_D)
    cos_alpha = math.cos(alpha_rad)
    sin_alpha = math.sin(alpha_rad)
    
    points = [
        (a_x, a_y),        # A
        (b_x, -n1),        # B
        (c_x, -n1),        # C
    ]
    
    # D
    c_x_coord, c_y_coord = points[2]
    d_y = c_y_coord + cd_len if rev else c_y_coord - cd_len
    points.append((d_x, d_y))
    
    # E
    d_x_coord, d_y_coord = points[3]
    e_x = d_x_coord - de_len * cos_alpha if rev else d_x_coord + de_len * cos_alpha
    e_y = d_y_coord + de_len * sin_alpha if rev else d_y_coord - de_len * sin_alpha
    points.append((e_x, e_y))
    
    # F
    e_x_coord, e_y_coord = points[4]
    f_x = e_x_coord + n2 * math.cos(alpha_rad + math.pi / 2)
    f_y = e_y_coord - n2 * math.sin(alpha_rad + math.pi / 2)
    points.append((f_x, f_y))
    
    # G
    f_x_coord, f_y_coord = points[5]
    points.append((f_x_coord - fg_len * cos_alpha, f_y_coord + fg_len * sin_alpha))
    
    # H
    g_x_coord, g_y_coord = points[6]
    points.append((g_x_coord, g_y_coord + gh_len))
    
    # I
    points.append((g_x_coord + hi_len, g_y_coord + gh_len))
    
    return points


def _calculate_missing_n1(
    n2: float, n4: float, angle_EF: float,
    c_x: float, d_x: float, cd_len: float, de_len: float, fg_len: float,
    gh_len: float, hi_len: float, j_x: float, k_y: float, jk_len: float,
    rev: bool
) -> float:
    """Find n1 using binary search when n1 is missing"""
    angle_D = 180 + angle_EF
    
    def calc_n4(n1_val):
        points = _calculate_points_to_i(
            n1_val, n2, angle_D, 0, 0, 0, c_x, d_x,
            cd_len, de_len, fg_len, gh_len, hi_len, k_y, rev
        )
        i_x, i_y = points[8]
        j_y = k_y - jk_len
        return math.sqrt((i_x - j_x) ** 2 + (i_y - j_y) ** 2)
    
    n1_min, n1_max = 0, 3000
    tolerance = 0.01
    for _ in range(100):
        n1_mid = (n1_min + n1_max) / 2
        error = calc_n4(n1_mid) - n4
        if abs(error) < tolerance:
            return n1_mid
        elif error > 0:
            n1_max = n1_mid
        else:
            n1_min = n1_mid
    
    raise ValueError("Не удалось найти длину n1")


def _calculate_missing_n2(
    n1: float, n4: float, angle_EF: float,
    c_x: float, d_x: float, cd_len: float, de_len: float, fg_len: float,
    gh_len: float, hi_len: float, j_x: float, k_y: float, jk_len: float,
    rev: bool
) -> float:
    """Find n2 using binary search when n2 is missing"""
    angle_D = 180 + angle_EF
    
    def calc_n4(n2_val):
        points = _calculate_points_to_i(
            n1, n2_val, angle_D, 0, 0, 0, c_x, d_x,
            cd_len, de_len, fg_len, gh_len, hi_len, k_y, rev
        )
        i_x, i_y = points[8]
        j_y = k_y - jk_len
        return math.sqrt((i_x - j_x) ** 2 + (i_y - j_y) ** 2)
    
    n2_min, n2_max = 0, 3000
    tolerance = 0.01
    for _ in range(100):
        n2_mid = (n2_min + n2_max) / 2
        error = calc_n4(n2_mid) - n4
        if abs(error) < tolerance:
            return n2_mid
        elif error > 0:
            n2_max = n2_mid
        else:
            n2_min = n2_mid
    
    raise ValueError("Не удалось найти длину n2")


def _calculate_missing_n4(
    n1: float, n2: float, angle_EF: float,
    c_x: float, d_x: float, cd_len: float, de_len: float, fg_len: float,
    gh_len: float, hi_len: float, j_x: float, k_y: float, jk_len: float,
    rev: bool
) -> float:
    """Calculate n4 directly when n4 is missing"""
    angle_D = 180 + angle_EF
    points = _calculate_points_to_i(
        n1, n2, angle_D, 0, 0, 0, c_x, d_x,
        cd_len, de_len, fg_len, gh_len, hi_len, k_y, rev
    )
    i_x, i_y = points[8]
    j_y = k_y - jk_len
    n4_val = math.sqrt((i_x - j_x) ** 2 + (i_y - j_y) ** 2)
    return n4_val


def _calculate_missing_angle_D(
    n1: float, n2: float, n4: float,
    c_x: float, d_x: float, cd_len: float, de_len: float, fg_len: float,
    gh_len: float, hi_len: float, j_x: float, k_y: float, jk_len: float,
    rev: bool
) -> float:
    """Find angle_D using binary search when angle_EF is missing"""
    
    def calc_n4_for_angle(angle_D_rad):
        alpha_rad = math.radians(270 - math.degrees(angle_D_rad))
        cos_alpha = math.cos(alpha_rad)
        sin_alpha = math.sin(alpha_rad)
        
        points = [
            (0, 0),              # A
            (0, -n1),            # B
            (c_x, -n1),          # C
        ]
        
        # D
        c_x_coord, c_y_coord = points[2]
        d_y = c_y_coord + cd_len if rev else c_y_coord - cd_len
        points.append((d_x, d_y))
        
        # E
        d_x_coord, d_y_coord = points[3]
        e_x = d_x_coord - de_len * cos_alpha if rev else d_x_coord + de_len * cos_alpha
        e_y = d_y_coord + de_len * sin_alpha if rev else d_y_coord - de_len * sin_alpha
        points.append((e_x, e_y))
        
        # F
        e_x_coord, e_y_coord = points[4]
        f_x = e_x_coord + n2 * math.cos(alpha_rad + math.pi / 2)
        f_y = e_y_coord - n2 * math.sin(alpha_rad + math.pi / 2)
        points.append((f_x, f_y))
        
        # G
        f_x_coord, f_y_coord = points[5]
        points.append((f_x_coord - fg_len * cos_alpha, f_y_coord + fg_len * sin_alpha))
        
        # H
        g_x_coord, g_y_coord = points[6]
        points.append((g_x_coord, g_y_coord + gh_len))
        
        # I
        points.append((g_x_coord + hi_len, g_y_coord + gh_len))
        
        i_x, i_y = points[8]
        j_y = k_y - jk_len
        return math.sqrt((i_x - j_x) ** 2 + (i_y - j_y) ** 2)
    
    D_min = math.radians(0)
    D_max = math.radians(360)
    tolerance = 0.01
    max_iterations = 100
    current_D = math.radians(180)
    calculated_n4 = calc_n4_for_angle(current_D)
    
    for _ in range(max_iterations):
        error = calculated_n4 - n4
        if abs(error) < tolerance:
            return math.degrees(current_D)
        if error > 0:
            D_max = current_D
            current_D = (D_min + current_D) / 2
        else:
            D_min = current_D
            current_D = (current_D + D_max) / 2
        calculated_n4 = calc_n4_for_angle(current_D)
    
    raise ValueError("Не удалось найти угол D. Возможно, заданная длина IJ недостижима.")


def calculate_points(
    n1: float, n2: float, angle_D: float,
    a_x: float, a_y: float, b_x: float, c_x: float, d_x: float,
    cd_len: float, de_len: float, fg_len: float, gh_len: float,
    hi_len: float, j_x: float, k_x: float, k_y: float, jk_len: float,
    alpha: float, rev: bool
) -> List[Tuple[float, float]]:
    """Calculate all points A through K"""
    if any(x is None for x in [n1, n2, angle_D]):
        raise ValueError("Одно или несколько параметров не определены")
    
    alpha_rad = math.radians(alpha)
    cos_alpha = math.cos(alpha_rad)
    sin_alpha = math.sin(alpha_rad)
    
    points = [
        (a_x, a_y),           # A
        (b_x, -n1),           # B
        (c_x, -n1),           # C
    ]
    
    # D
    c_x_coord, c_y_coord = points[2]
    d_y = c_y_coord + cd_len if rev else c_y_coord - cd_len
    points.append((d_x, d_y))
    
    # E
    d_x_coord, d_y_coord = points[3]
    e_x = d_x_coord - de_len * cos_alpha if rev else d_x_coord + de_len * cos_alpha
    e_y = d_y_coord + de_len * sin_alpha if rev else d_y_coord - de_len * sin_alpha
    points.append((e_x, e_y))
    
    # F
    e_x_coord, e_y_coord = points[4]
    f_x = e_x_coord + n2 * math.cos(alpha_rad + math.pi / 2)
    f_y = e_y_coord - n2 * math.sin(alpha_rad + math.pi / 2)
    points.append((f_x, f_y))
    
    # G
    f_x_coord, f_y_coord = points[5]
    points.append((f_x_coord - fg_len * cos_alpha, f_y_coord + fg_len * sin_alpha))
    
    # H
    g_x_coord, g_y_coord = points[6]
    points.append((g_x_coord, g_y_coord + gh_len))
    
    # I
    points.append((g_x_coord + hi_len, g_y_coord + gh_len))
    
    # J
    j_y = k_y - jk_len
    points.append((j_x, j_y))
    
    # K
    points.append((k_x, k_y))
    
    return points
