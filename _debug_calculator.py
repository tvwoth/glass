"""
Debug script: understand actual contour_calculator behavior.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.calculator.contour_calculator import ContourCalculator

calc = ContourCalculator()
calc.set_j_x(-48)
calc.set_c_x(-160)
calc.set_cd_len(65)
calc.set_de_len(20)
calc.set_fg_len(20)
calc.set_gh_len(70)
calc.set_hi_len(43.5)
calc.set_jk_len(8.5)
calc.set_hcor(80)

# Test 1: n1=100, n2=50, n4=None, angle_EF=5
print("="*60)
print("Test 1: n1=100, n2=50, n4=None, angle_EF=5")
calc.set_directions(REV=False)
try:
    pts = calc.calculate(n1=100, n2=50, n4=None, angle_EF=5)
    print(f"OK. n1={calc.n1}, n2={calc.n2}, n4={calc.n4}, angle_EF={calc.angle_EF}, angle_D={calc.angle_D}")
    print(f"A={pts[0]}, B={pts[1]}, C={pts[2]}, D={pts[3]}, E={pts[4]}")
    print(f"F={pts[5]}, G={pts[6]}, H={pts[7]}, I={pts[8]}, J={pts[9]}, K={pts[10]}")
except ValueError as e:
    print(f"FAILED: {e}")

# Test 2: n1=-10, n2=50, n4=120, angle_EF=None
print()
print("="*60)
print("Test 2: n1=-10, n2=50, n4=120, angle_EF=None")
calc2 = ContourCalculator()
calc2.set_j_x(-48)
calc2.set_c_x(-160)
calc2.set_cd_len(65)
calc2.set_de_len(20)
calc2.set_fg_len(20)
calc2.set_gh_len(70)
calc2.set_hi_len(43.5)
calc2.set_jk_len(8.5)
calc2.set_hcor(80)
calc2.set_directions(REV=False)
try:
    pts = calc2.calculate(n1=-10, n2=50, n4=120, angle_EF=None)
    print(f"OK: n1={calc2.n1}")
except ValueError as e:
    print(f"FAILED: {e}")

# Test 3: n1=None, n2=50, n4=120, angle_EF=5 
print()
print("="*60)
print("Test 3: n1=None, n2=50, n4=120, angle_EF=5")
calc3 = ContourCalculator()
calc3.set_j_x(-48)
calc3.set_c_x(-160)
calc3.set_cd_len(65)
calc3.set_de_len(20)
calc3.set_fg_len(20)
calc3.set_gh_len(70)
calc3.set_hi_len(43.5)
calc3.set_jk_len(8.5)
calc3.set_hcor(80)
calc3.set_directions(REV=False)
try:
    pts = calc3.calculate(n1=None, n2=50, n4=120, angle_EF=5)
    print(f"OK. n1={calc3.n1}, n2={calc3.n2}, n4={calc3.n4}")
except ValueError as e:
    print(f"FAILED: {e}")

# Test 4: n1=100, n2=None, n4=120, angle_EF=5
print()
print("="*60)
print("Test 4: n1=100, n2=None, n4=120, angle_EF=5")
calc4 = ContourCalculator()
calc4.set_j_x(-48)
calc4.set_c_x(-160)
calc4.set_cd_len(65)
calc4.set_de_len(20)
calc4.set_fg_len(20)
calc4.set_gh_len(70)
calc4.set_hi_len(43.5)
calc4.set_jk_len(8.5)
calc4.set_hcor(80)
calc4.set_directions(REV=False)
try:
    pts = calc4.calculate(n1=100, n2=None, n4=120, angle_EF=5)
    print(f"OK. n1={calc4.n1}, n2={calc4.n2}, n4={calc4.n4}")
except ValueError as e:
    print(f"FAILED: {e}")

# Test 5: Test negative parameters
print()
print("="*60)
print("Test 5: n1=100, n2=-50, n4=120, angle_EF=None")
calc5 = ContourCalculator()
calc5.set_j_x(-48)
calc5.set_c_x(-160)
calc5.set_cd_len(65)
calc5.set_de_len(20)
calc5.set_fg_len(20)
calc5.set_gh_len(70)
calc5.set_hi_len(43.5)
calc5.set_jk_len(8.5)
calc5.set_hcor(80)
calc5.set_directions(REV=False)
try:
    pts = calc5.calculate(n1=100, n2=-50, n4=120, angle_EF=None)
    print(f"OK (unexpected): {calc5.n1}, {calc5.n2}, {calc5.n4}")
except ValueError as e:
    print(f"FAILED: {e}")

# Test 6: n4 > 10 and angle_EF=None (angle missing)
print()
print("="*60)
print("Test 6: n1=100, n2=50, n4=120 (stored as 200), angle_EF=None")
calc6 = ContourCalculator()
calc6.set_j_x(-48)
calc6.set_c_x(-160)
calc6.set_cd_len(65)
calc6.set_de_len(20)
calc6.set_fg_len(20)
calc6.set_gh_len(70)
calc6.set_hi_len(43.5)
calc6.set_jk_len(8.5)
calc6.set_hcor(80)
calc6.set_directions(REV=False)
try:
    pts = calc6.calculate(n1=100, n2=50, n4=120, angle_EF=None)
    print(f"OK. n1={calc6.n1}, n2={calc6.n2}, n4={calc6.n4}, angle_EF={calc6.angle_EF}")
except ValueError as e:
    print(f"FAILED: {e}")