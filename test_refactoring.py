"""
Test script to verify that the new calculate() function produces identical results
to the old ContourCalculator class.
"""

import sys
import json
import os

# Add the app directory to the path
sys.path.insert(0, '/app' if os.path.exists('/app') else 'c:/Users/I/contr/contour-app')

from app.calculator.contour_calculator import ContourCalculator
from app.core.calculate import calculate


def test_basic_calculation():
    """Test a basic calculation with known parameters"""
    print("=" * 60)
    print("TEST 1: Basic calculation with Premier kit config")
    print("=" * 60)
    
    # Configuration from "Премьер комплект YP01YP02YP03G01"
    config = {
        "j_x": -48,
        "c_x": -160,
        "cd_len": 65,
        "de_len": 20,
        "fg_len": 20,
        "gh_len": 70,
        "hi_len": 43.5,
        "jk_len": 8.5,
        "hcor": 80,
    }
    
    input_data = {
        "n1": 100,
        "n2": None,
        "n4": None,
        "angle_EF": 5
    }
    
    # Test with old implementation
    print("\n1. Testing OLD implementation (ContourCalculator)...")
    calculator = ContourCalculator()
    calculator.load_config(os.path.join(os.path.dirname(__file__), 'app', 'configs', 'Премьер комплект YP01YP02YP03G01.json'))
    
    try:
        old_points = calculator.calculate(
            n1=input_data['n1'],
            n2=input_data['n2'],
            n4=input_data['n4'],
            angle_EF=input_data['angle_EF']
        )
        print(f"  ✓ Old calculation succeeded")
        print(f"    n1 = {calculator.n1:.2f}")
        print(f"    n2 = {calculator.n2:.2f}")
        print(f"    n4 = {calculator.n4:.2f}")
        print(f"    angle_EF = {calculator.get_angle_EF():.2f}°")
    except Exception as e:
        print(f"  ✗ Old calculation failed: {e}")
        return False
    
    # Test with new implementation
    print("\n2. Testing NEW implementation (calculate function)...")
    try:
        result = calculate(input_data, config)
        print(f"  ✓ New calculation succeeded")
        print(f"    n1 = {result['n1']:.2f}")
        print(f"    n2 = {result['n2']:.2f}")
        print(f"    n4 = {result['n4']:.2f}")
        print(f"    angle_EF = {result['angle_EF']:.2f}°")
    except Exception as e:
        print(f"  ✗ New calculation failed: {e}")
        return False
    
    # Compare results
    print("\n3. Comparing results...")
    tolerance = 0.01  # Allow 0.01 unit difference due to floating point precision
    
    n1_match = abs(calculator.n1 - result['n1']) < tolerance
    n2_match = abs(calculator.n2 - result['n2']) < tolerance
    n4_match = abs(calculator.n4 - result['n4']) < tolerance
    angle_match = abs(calculator.get_angle_EF() - result['angle_EF']) < tolerance
    
    print(f"  n1:       {calculator.n1:.4f} vs {result['n1']:.4f} {'✓' if n1_match else '✗'}")
    print(f"  n2:       {calculator.n2:.4f} vs {result['n2']:.4f} {'✓' if n2_match else '✗'}")
    print(f"  n4:       {calculator.n4:.4f} vs {result['n4']:.4f} {'✓' if n4_match else '✗'}")
    print(f"  angle_EF: {calculator.get_angle_EF():.4f}° vs {result['angle_EF']:.4f}° {'✓' if angle_match else '✗'}")
    
    # Compare points
    print("\n4. Comparing calculated points...")
    points_match = True
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    
    for i, (label, old_point) in enumerate(zip(labels, old_points)):
        new_point = result['points'][i]
        dist = ((old_point[0] - new_point[0])**2 + (old_point[1] - new_point[1])**2)**0.5
        match = dist < tolerance
        points_match = points_match and match
        status = '✓' if match else '✗'
        print(f"  {label}: Old({old_point[0]:8.2f}, {old_point[1]:8.2f}) vs New({new_point[0]:8.2f}, {new_point[1]:8.2f}) {status}")
    
    all_match = n1_match and n2_match and n4_match and angle_match and points_match
    
    print("\n" + ("=" * 60))
    print(f"TEST 1 RESULT: {'✓ PASSED' if all_match else '✗ FAILED'}")
    print("=" * 60)
    
    return all_match


def test_all_parameter_combinations():
    """Test different parameter combinations"""
    print("\n" + "=" * 60)
    print("TEST 2: Testing all parameter combinations")
    print("=" * 60)
    
    config = {
        "j_x": -48,
        "c_x": -160,
        "cd_len": 65,
        "de_len": 20,
        "fg_len": 20,
        "gh_len": 70,
        "hi_len": 43.5,
        "jk_len": 8.5,
        "hcor": 80,
    }
    
    test_cases = [
        ("n1 + n2 + angle_EF", {"n1": 100, "n2": 50, "angle_EF": 5, "n4": None}),
        ("n1 + n4 + angle_EF", {"n1": 100, "n4": 100, "angle_EF": 5, "n2": None}),
        ("n2 + n4 + angle_EF", {"n2": 50, "n4": 100, "angle_EF": 5, "n1": None}),
    ]
    
    all_passed = True
    
    for test_name, input_data in test_cases:
        print(f"\n  Testing: {test_name}")
        
        # Old implementation
        calculator = ContourCalculator()
        try:
            for key, val in config.items():
                if key == "j_x":
                    calculator.set_j_x(val)
                elif key == "c_x":
                    calculator.set_c_x(val)
                elif key == "cd_len":
                    calculator.set_cd_len(val)
                elif key == "de_len":
                    calculator.set_de_len(val)
                elif key == "fg_len":
                    calculator.set_fg_len(val)
                elif key == "gh_len":
                    calculator.set_gh_len(val)
                elif key == "hi_len":
                    calculator.set_hi_len(val)
                elif key == "jk_len":
                    calculator.set_jk_len(val)
                elif key == "hcor":
                    calculator.set_hcor(val)
            
            old_points = calculator.calculate(
                n1=input_data['n1'],
                n2=input_data['n2'],
                n4=input_data['n4'],
                angle_EF=input_data['angle_EF']
            )
        except Exception as e:
            print(f"    ✗ Old: {e}")
            all_passed = False
            continue
        
        # New implementation
        try:
            result = calculate(input_data, config)
        except Exception as e:
            print(f"    ✗ New: {e}")
            all_passed = False
            continue
        
        # Compare
        tolerance = 0.01
        match = (
            abs(calculator.n1 - result['n1']) < tolerance and
            abs(calculator.n2 - result['n2']) < tolerance and
            abs(calculator.n4 - result['n4']) < tolerance
        )
        
        status = "✓" if match else "✗"
        print(f"    {status} n1={result['n1']:.2f}, n2={result['n2']:.2f}, n4={result['n4']:.2f}")
        all_passed = all_passed and match
    
    print("\n" + "=" * 60)
    print(f"TEST 2 RESULT: {'✓ PASSED' if all_passed else '✗ FAILED'}")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    print("\n🧪 RUNNING VERIFICATION TESTS FOR REFACTORED CALCULATOR\n")
    
    test1_passed = test_basic_calculation()
    test2_passed = test_all_parameter_combinations()
    
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✓ ALL TESTS PASSED - Refactoring is successful!")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED - Review the differences above")
        sys.exit(1)
