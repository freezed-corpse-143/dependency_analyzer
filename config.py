import os

IGNORE_DIRS = {
    "__pycache__", ".git", ".mypy_cache", ".pytest_cache",
    "build", "dist", "venv", ".idea", ".vscode"
}

def should_ignore(path: str) -> bool:
    return any(part in IGNORE_DIRS for part in path.split(os.sep))
