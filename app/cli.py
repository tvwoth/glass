"""
Command-line interface for contour calculator.
Usage: python -m app.cli config.json
"""
import json
import sys
from pathlib import Path
from app.core.calculate import calculate
from app.utils.plot import generate_plot


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <config.json>")
        print("Config JSON format:")
        print(json.dumps({
            "config": {
                "j_x": 0,
                "c_x": 0,
                "cd_len": 0,
                "de_len": 0,
                "fg_len": 0,
                "gh_len": 0,
                "hi_len": 0,
                "jk_len": 0,
                "hcor": 0
            },
            "input_data": {
                "n1": 100,
                "n2": None,
                "n4": None,
                "angle_EF": 5
            }
        }, indent=2))
        sys.exit(1)
    
    config_file = Path(sys.argv[1])
    
    if not config_file.exists():
        print(f"Error: File not found: {config_file}")
        sys.exit(1)
    
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        config = data.get("config", {})
        input_data = data.get("input_data", {})
        
        result = calculate(input_data, config)
        
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ РАСЧЕТА")
        print("="*50)
        print(f"n1:      {result['n1']:.2f}")
        print(f"n2:      {result['n2']:.2f}")
        print(f"n4:      {result['n4']:.2f}")
        print(f"angle_EF: {result['angle_EF']:.2f}°")
        print(f"angle_D:  {result['angle_D']:.2f}°")
        print("\nКоординаты точек:")
        print("-"*50)
        labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        for label, (x, y) in zip(labels, result['points']):
            print(f"{label}: ({x:10.2f}, {y:10.2f})")
        
        # Generate plot if requested
        plot_file = config_file.parent / (config_file.stem + "_plot.png")
        try:
            generate_plot(result['points'], str(plot_file))
            print(f"\nГрафик сохранён: {plot_file}")
        except Exception as e:
            print(f"Warning: Could not generate plot: {e}")
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
