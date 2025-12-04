#!/usr/bin/env python3
"""
Command-line interface for Python dependency analyzer.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    # When running as module: python -m dependency_analyzer
    from .runner import Analyzer
except ImportError:
    # When running directly: python cli.py
    from runner import Analyzer


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Python file dependencies in a project and generate dependency graph."
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path to the Python project to analyze (default: current directory)"
    )
    parser.add_argument(
        "--no-visual",
        action="store_true",
        help="Disable HTML visualization generation"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output path for the dependency graph (default: dependency_graph.html in project directory)"
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output dependency graph as JSON to stdout"
    )
    parser.add_argument(
        "--json-file",
        help="Save dependency graph as JSON to specified file"
    )
    
    args = parser.parse_args()
    
    # Validate project path
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"Error: Project path '{project_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not project_path.is_dir():
        print(f"Error: '{project_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Run analysis
        analyzer = Analyzer(str(project_path), enable_visual=not args.no_visual)
        result = analyzer.run()
        
        # Output JSON if requested
        if args.json:
            print(json.dumps(result, indent=2))
        
        if args.json_file:
            json_path = Path(args.json_file)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"[✔] JSON saved to {json_path}")
        
        if not args.no_visual and args.output:
            # If custom output path is specified, move the generated file
            default_output = project_path / "dependency_graph.html"
            custom_output = Path(args.output)
            if default_output.exists() and default_output != custom_output:
                default_output.rename(custom_output)
                print(f"[✔] Visualization moved to {custom_output}")
        
        print(f"[✔] Analysis completed. Found {len(result)} Python files with dependencies.")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()