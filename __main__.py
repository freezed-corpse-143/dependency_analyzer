#!/usr/bin/env python3
"""
Entry point for running dependency_analyzer as a module.
Example: python -m dependency_analyzer /path/to/project
"""

from .cli import main

if __name__ == "__main__":
    main()