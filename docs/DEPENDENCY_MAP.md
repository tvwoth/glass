# Dependency Map: contour_calculator.py

## Class: ContourCalculator

### Properties (state)
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| A_X | float | 0 | Point A X coordinate |
| A_Y | float | 0 | Point A Y coordinate |
| B_X | float = A_X | 0 | Point B X coordinate |
| C_X | float | 0 | Point C X coordinate |
| D_X = C_X | float | 0 | Point D X coordinate |
| CD_LEN | float | 0 | Segment CD length |
| DE_LEN | float | 0 | Segment DE length |
| FG_LEN | float | 0 | Segment FG length |
| GH_LEN | float | 0 | Segment GH length |
| HI_LEN | float | 0 | Segment HI length |
| J_X | float | 0 | Point J X coordinate |
| JK_LEN | float | 0 | Segment JK length |
| HCOR | float | 0 | Correction for n4 |
| K_X = J_X | float | 0 | Point K X coordinate |
| K_Y = A_Y | float | 0 | Point K Y coordinate |
| REV | bool | False | Reverse direction flag |
| n1 | float | None | Calculated/input parameter 1 |
| n2 | float | None | Calculated/input parameter 2 |
| n4 | float | None | Calculated/input parameter 4 (WITH hcor applied) |
| angle_D | float | None | Angle D (180 + angle_EF) |
| alpha | float | None | 270 - angle_D |
| angle_EF | float | None | Input angle (0-10) |

### Methods

| Method | Input | Output | Called From | Description |
|--------|-------|--------|-------------|-------------|
| `__init__()` | - | - | Constructor | Initializes state, loads default config |
| `load_config(file)` | str path | image str or None | `load_config_by_name()` | Loads JSON config, sets properties |
| `set_j_x(val)` | float | - | `apply_h_params()` | Sets J_X and K_X |
| `set_c_x(val)` | float | - | `apply_h_params()` | Sets C_X and D_X |
| `set_cd_len(val)` | float | - | `apply_h_params()` | Sets CD_LEN |
| `set_de_len(val)` | float | - | `apply_h_params()` | Sets DE_LEN |
| `set_fg_len(val)` | float | - | `apply_h_params()` | Sets FG_LEN |
| `set_gh_len(val)` | float | - | `apply_h_params()` | Sets GH_LEN |
| `set_hi_len(val)` | float | - | `apply_h_params()` | Sets HI_LEN |
| `set_jk_len(val)` | float | - | `apply_h_params()` | Sets JK_LEN |
| `set_hcor(val)` | float | - | `apply_h_params()` | Sets HCOR |
| `set_directions(REV)` | bool | - | `index()` route | Sets REV flag |
| `calculate(n1,n2,n4,angle_EF)` | 4 floats (3 required) | list of 11 points | `index()` route | Main calculation entry point |
| `_calculate_points_to_i(n1,n2,angle_D)` | 3 floats | list of 9 points | `_calculate_missing_*` | Internal: calculates A through I |
| `_calculate_missing_n1(n2,n4,angle_EF)` | 3 floats | float n1 | `calculate()` | Binary search for n1 |
| `_calculate_missing_n2(n1,n4,angle_EF)` | 3 floats | float n2 | `calculate()` | Binary search for n2 |
| `_calculate_missing_n4(n1,n2,angle_EF)` | 3 floats | float n4 | `calculate()` | Direct calculation of n4 |
| `_calculate_missing_angle_D(n1,n2,n4)` | 3 floats | float angle_D | `calculate()` | Binary search for angle_D |
| `calculate_a()` | - | (x,y) | `calculate_points()` | Point A coordinate |
| `calculate_b()` | - | (x,y) | `calculate_points()` | Point B coordinate |
| `calculate_c()` | - | (x,y) | `calculate_points()` | Point C coordinate |
| `calculate_d(c_y)` | float | (x,y) | `calculate_points()` | Point D coordinate |
| `calculate_e(d_x,d_y,alpha_rad)` | 3 floats | (x,y) | `calculate_points()` | Point E coordinate |
| `calculate_f(e_x,e_y,alpha_rad)` | 3 floats | (x,y) | `calculate_points()` | Point F coordinate |
| `calculate_g(f_x,f_y,alpha_rad)` | 3 floats | (x,y) | `calculate_points()` | Point G coordinate |
| `calculate_h(g_x,g_y)` | 2 floats | (x,y) | `calculate_points()` | Point H coordinate |
| `calculate_i(g_x,g_y)` | 2 floats | (x,y) | `calculate_points()` | Point I coordinate |
| `calculate_j()` | - | (x,y) | `calculate_points()` | Point J coordinate |
| `calculate_k()` | - | (x,y) | `calculate_points()` | Point K coordinate |
| `calculate_points()` | - | list of 11 points | `calculate()` | Calculates all 11 points |
| `get_n3()` | - | float or None | `index()` route | Returns n4 - HCOR |
| `get_angle_EF()` | - | float | `index()` route | Returns angle_D - 180 |

### External Function
| Function | Input | Output | Called From | Description |
|----------|-------|--------|-------------|-------------|
| `generate_plot(points, output_path)` | points list, str path | - (saves file) | `index()` route | Generates matplotlib plot |

## Critical: n4 vs n3 distinction
- **n4** (internal): stored as `self.n4 = input_n4 + HCOR` (corrected value)
- **n3** (display): accessed via `get_n3()` = `self.n4 - HCOR` (original input value)
- This MUST be preserved exactly

## Difference between contour_calculator.py and calculate.py
1. contour_calculator uses class with state; calculate.py uses pure functions
2. contour_calculator stores n4 (with hcor) and provides get_n3(); calculate.py returns n4 directly
3. contour_calculator._calculate_missing_angle_D duplicates point calc inline; same in calculate.py
4. contour_calculator uses self.A_X, self.A_Y, self.B_X, self.K_X, self.K_Y from state; calculate.py passes them explicitly
5. **Key**: parse_h_params applies `-abs()` for j_x and c_x - making them negative. This sign convention MUST be preserved.