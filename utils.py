from pathlib import Path

def scan_py_files(path: str):
    return list(Path(path).rglob("*.py"))
