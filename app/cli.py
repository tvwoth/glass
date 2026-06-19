"""
Command-line interface for contour calculator.

Usage:
    contour calculate <config.json>
    contour render <config.json> [output.png]
    contour export-pdf <config.json> [output.pdf]
    contour config-list
    contour config-edit <name> [param=value ...]

All commands use the same core calculation engine.
No mathematical logic exists in the CLI layer.
"""
import json
import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Any

from app.core.calculate import calculate as core_calculate
from app.rendering.matplotlib_renderer import render
from app.storage.export_json import export_json
from app.storage.export_csv import export_csv
from app.storage.export_pdf import export_pdf
from app.configs.manager import ConfigManager


# Default H-parameters (empty config)
DEFAULT_CONFIG = {
    "j_x": 0, "c_x": 0, "cd_len": 0, "de_len": 0,
    "fg_len": 0, "gh_len": 0, "hi_len": 0, "jk_len": 0, "hcor": 0,
    "rev": False,
}


def load_config_from_file(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not config_path.exists():
        print(f"Error: File not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Support both old format (with config/input_data) and new format
        if "config" in data:
            config = data.get("config", {})
            input_data = data.get("input_data", {})
        else:
            config = data
            input_data = {}
        
        return {"config": config, "input_data": input_data}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_path}: {e}", file=sys.stderr)
        sys.exit(1)


def print_result(result: Dict[str, Any]) -> None:
    """Print calculation results to console."""
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ РАСЧЕТА")
    print("=" * 50)
    print(f"n1:       {result['n1']:.2f}")
    print(f"n2:       {result['n2']:.2f}")
    print(f"n3:       {result['n3']:.2f}")
    print(f"n4:       {result['n4']:.2f}")
    print(f"angle_EF: {result['angle_EF']:.2f}°")
    print(f"angle_D:  {result['angle_D']:.2f}°")
    print()
    print("Координаты точек:")
    print("-" * 50)
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    for label, (x, y) in zip(labels, result['points']):
        print(f"  {label}: ({x:10.2f}, {y:10.2f})")


def cmd_calculate(args):
    """Contour calculate: run calculation and display results."""
    loaded = load_config_from_file(Path(args.config))
    config = loaded["config"]
    input_data = loaded["input_data"]

    # Apply default config values for missing keys
    for key, val in DEFAULT_CONFIG.items():
        config.setdefault(key, val)

    result = core_calculate(input_data, config)
    print_result(result)

    # Auto-save JSON result with metadata
    output_path = Path(args.config).with_suffix('.result.json')
    metadata = {
        "config_name": Path(args.config).stem,
        "config": config,
        "input": input_data,
    }
    export_json(result, str(output_path), metadata=metadata)
    print(f"\nРезультат сохранён: {output_path}")


def cmd_render(args):
    """Contour render: calculate and generate plot image."""
    loaded = load_config_from_file(Path(args.config))
    config = loaded["config"]
    input_data = loaded["input_data"]

    for key, val in DEFAULT_CONFIG.items():
        config.setdefault(key, val)

    result = core_calculate(input_data, config)

    output = args.output or Path(args.config).with_suffix('.png')
    render(result['points'], str(output))
    print(f"График сохранён: {output}")


def cmd_export_pdf(args):
    """Contour export-pdf: calculate and generate PDF report."""
    loaded = load_config_from_file(Path(args.config))
    config = loaded["config"]
    input_data = loaded["input_data"]

    for key, val in DEFAULT_CONFIG.items():
        config.setdefault(key, val)

    result = core_calculate(input_data, config)

    output = args.output or Path(args.config).with_suffix('.pdf')
    config_name = Path(args.config).stem
    export_pdf(result, str(output), config_name=config_name)
    print(f"PDF отчёт сохранён: {output}")


def cmd_config_list(args):
    """Contour config-list: list available configurations."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    mgr = ConfigManager(app_dir)

    print("Системные конфигурации:")
    for name in mgr.list_system():
        print(f"  - {name}")
    
    print()
    print("Пользовательские конфигурации:")
    user_configs = mgr.list_user()
    if user_configs:
        for name in user_configs:
            print(f"  - {name}")
    else:
        print("  (нет)")


def cmd_config_edit(args):
    """Contour config-edit: create/edit a user configuration."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    mgr = ConfigManager(os.path.abspath(app_dir))

    name = args.name
    existing = mgr.load(name) or DEFAULT_CONFIG.copy()

    if args.params:
        for param in args.params:
            if '=' not in param:
                print(f"Error: Invalid parameter format: {param} (use key=value)", file=sys.stderr)
                sys.exit(1)
            key, value = param.split('=', 1)
            existing[key] = float(value)

    saved_name = mgr.save(name, existing)
    print(f"Конфигурация «{saved_name}» сохранена.")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Contour Calculator - расчёт геометрии контура стеклянного козырька"
    )
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # contour calculate <config.json>
    p_calc = subparsers.add_parser("calculate", help="Выполнить расчёт")
    p_calc.add_argument("config", help="Путь к JSON-файлу конфигурации")

    # contour render <config.json> [output.png]
    p_render = subparsers.add_parser("render", help="Построить график контура")
    p_render.add_argument("config", help="Путь к JSON-файлу конфигурации")
    p_render.add_argument("output", nargs="?", help="Путь для сохранения PNG")

    # contour export-pdf <config.json> [output.pdf]
    p_pdf = subparsers.add_parser("export-pdf", help="Экспортировать результаты в PDF")
    p_pdf.add_argument("config", help="Путь к JSON-файлу конфигурации")
    p_pdf.add_argument("output", nargs="?", help="Путь для сохранения PDF")

    # contour config-list
    subparsers.add_parser("config-list", help="Список доступных конфигураций")

    # contour config-edit <name> [param=value ...]
    p_edit = subparsers.add_parser("config-edit", help="Создать или изменить конфигурацию")
    p_edit.add_argument("name", help="Имя конфигурации")
    p_edit.add_argument("params", nargs="*", help="Параметры в формате key=value")

    args = parser.parse_args()

    if args.command == "calculate":
        cmd_calculate(args)
    elif args.command == "render":
        cmd_render(args)
    elif args.command == "export-pdf":
        cmd_export_pdf(args)
    elif args.command == "config-list":
        cmd_config_list(args)
    elif args.command == "config-edit":
        cmd_config_edit(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()