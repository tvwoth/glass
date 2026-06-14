"""
Standalone test that imports calculate directly without going through app/__init__.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import calculate directly from the module file
from app.core.calculate import calculate

def test_calculate():
    """Test the calculate function directly"""
    print("="*70)
    print("TESTING CORE CALCULATE FUNCTION")
    print("="*70)
    
    # Test configuration
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
    
    # Test 1: n1 given
    print("\nTest 1: n1=100 (find n2 and n4)")
    print("-"*70)
    input_data = {
        "n1": 100,
        "n2": None,
        "n4": None,
        "angle_EF": 5
    }
    
    try:
        result = calculate(input_data, config)
        print(f"✓ Success!")
        print(f"  n1:       {result['n1']:.4f}")
        print(f"  n2:       {result['n2']:.4f}")
        print(f"  n4:       {result['n4']:.4f}")
        print(f"  angle_EF: {result['angle_EF']:.4f}°")
        print(f"  angle_D:  {result['angle_D']:.4f}°")
        print(f"\n  Points calculated: {len(result['points'])} points")
        labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        for label, (x, y) in zip(labels, result['points']):
            print(f"    {label:1s}: ({x:10.2f}, {y:10.2f})")
        
        test1_pass = all(param > 0 for param in [result['n1'], result['n2'], result['n4']])
        if test1_pass:
            print("  ✓ All parameters are positive")
        else:
            print("  ✗ Some parameters are non-positive")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        test1_pass = False
    
    # Test 2: n2 given
    print("\n\nTest 2: n2=50 (find n1 and n4)")
    print("-"*70)
    input_data = {
        "n1": None,
        "n2": 50,
        "n4": None,
        "angle_EF": 5
    }
    
    try:
        result = calculate(input_data, config)
        print(f"✓ Success!")
        print(f"  n1:       {result['n1']:.4f}")
        print(f"  n2:       {result['n2']:.4f}")
        print(f"  n4:       {result['n4']:.4f}")
        print(f"  angle_EF: {result['angle_EF']:.4f}°")
        
        test2_pass = all(param > 0 for param in [result['n1'], result['n2'], result['n4']])
        if test2_pass:
            print("  ✓ All parameters are positive")
        else:
            print("  ✗ Some parameters are non-positive")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        test2_pass = False
    
    # Test 3: n4 given
    print("\n\nTest 3: n4=120 (find n1 and n2)")
    print("-"*70)
    input_data = {
        "n1": None,
        "n2": None,
        "n4": 120,
        "angle_EF": 5
    }
    
    try:
        result = calculate(input_data, config)
        print(f"✓ Success!")
        print(f"  n1:       {result['n1']:.4f}")
        print(f"  n2:       {result['n2']:.4f}")
        print(f"  n4:       {result['n4']:.4f}")
        print(f"  angle_EF: {result['angle_EF']:.4f}°")
        
        test3_pass = all(param > 0 for param in [result['n1'], result['n2'], result['n4']])
        if test3_pass:
            print("  ✓ All parameters are positive")
        else:
            print("  ✗ Some parameters are non-positive")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        test3_pass = False
    
    print("\n" + "="*70)
    if test1_pass and test2_pass and test3_pass:
        print("✓ ALL TESTS PASSED")
        print("="*70)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(test_calculate())
