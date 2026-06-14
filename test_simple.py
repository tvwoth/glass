"""
Simplified test script that tests the core calculate function directly
without importing through the Flask app.
"""

import sys
import os
import json

# Test just the core calculate module
from app.core.calculate import calculate

def test_calculate_function():
    """Test the refactored calculate function"""
    print("="*60)
    print("Testing Core Calculate Function")
    print("="*60)
    
    # Configuration from "Премьер комплект YP01YP02YP03G01"
    config = {
        "a_x": 0,
        "a_y": 0,
        "b_x": 0,
        "c_x": -160,
        "d_x": -160,
        "cd_len": 65,
        "de_len": 20,
        "fg_len": 20,
        "gh_len": 70,
        "hi_len": 43.5,
        "j_x": -48,
        "jk_len": 8.5,
        "hcor": 80,
        "k_x": -48,
        "k_y": 0,
        "rev": False,
    }
    
    test_cases = [
        ("n1 given, find n2, n4", {
            "n1": 100,
            "n2": None,
            "n4": None,
            "angle_EF": 5
        }),
        ("n2 given, find n1, n4", {
            "n1": None,
            "n2": 50,
            "n4": None,
            "angle_EF": 5
        }),
        ("n4 given, find n1, n2", {
            "n1": None,
            "n2": None,
            "n4": 120,
            "angle_EF": 5
        }),
    ]
    
    all_passed = True
    
    for test_name, input_data in test_cases:
        print(f"\n Test: {test_name}")
        print(f" Input: n1={input_data.get('n1')}, n2={input_data.get('n2')}, " +
              f"n4={input_data.get('n4')}, angle_EF={input_data.get('angle_EF')}")
        
        try:
            result = calculate(input_data, config)
            
            print(f" ✓ Calculation successful:")
            print(f"   n1={result['n1']:.2f}, n2={result['n2']:.2f}, " +
                  f"n4={result['n4']:.2f}, angle_EF={result['angle_EF']:.2f}°")
            
            # Verify results make sense
            if result['n1'] <= 0 or result['n2'] <= 0 or result['n4'] <= 0:
                print(f"   ✗ Invalid result - all lengths should be positive")
                all_passed = False
            else:
                print(f"   ✓ All parameters are positive")
                
                # Print points
                labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
                print(f"\n   Points calculated:")
                for label, (x, y) in zip(labels, result['points']):
                    print(f"    {label}: ({x:8.2f}, {y:8.2f})")
            
        except Exception as e:
            print(f" ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All tests PASSED")
    else:
        print("✗ Some tests FAILED")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = test_calculate_function()
    sys.exit(0 if success else 1)
