# Python Dependency Analyzer

A tool to analyze dependencies between Python files in a project and generate interactive visualization.

## New Command-Line Interface

The tool now provides a command-line interface to generate dependency analysis graphs for Python projects.

### Installation

No installation required. Just ensure you have Python 3.7+ installed.

### Usage

#### As a module:
```bash
python -m dependency_analyzer /path/to/project [options]
```

#### Directly:
```bash
python cli.py /path/to/project [options]
```

### Options

- `project_path`: Path to the Python project to analyze (default: current directory)
- `--no-visual`: Disable HTML visualization generation
- `--output`, `-o`: Output path for the dependency graph (default: dependency_graph.html in project directory)
- `--json`, `-j`: Output dependency graph as JSON to stdout
- `--json-file`: Save dependency graph as JSON to specified file

### Examples

1. **Basic analysis with visualization**:
   ```bash
   python -m dependency_analyzer /path/to/project
   ```
   Generates `dependency_graph.html` in the project directory.

2. **JSON output only**:
   ```bash
   python -m dependency_analyzer /path/to/project --json
   ```

3. **Save JSON to file**:
   ```bash
   python -m dependency_analyzer /path/to/project --json-file dependencies.json
   ```

4. **Custom output path**:
   ```bash
   python -m dependency_analyzer /path/to/project --output /tmp/my_graph.html
   ```

5. **Disable visualization**:
   ```bash
   python -m dependency_analyzer /path/to/project --no-visual --json
   ```

### Output Format

The dependency graph is represented as a dictionary where keys are source file paths and values are lists of dependent file paths:

```json
{
  "/path/to/file_a.py": [
    "/path/to/file_b.py",
    "/path/to/file_c.py"
  ],
  "/path/to/file_b.py": [
    "/path/to/file_d.py"
  ]
}
```

### Features

- Parses Python files using AST
- Handles both absolute and relative imports
- Ignores standard library imports
- Excludes common directories (__pycache__, .git, venv, etc.)
- Generates interactive HTML visualization using AntV G6
- Supports JSON output for programmatic use

### Visualization

The HTML visualization provides an interactive graph where you can:
- Drag nodes
- Zoom in/out
- See dependencies as directed edges
- Layout automatically arranges nodes for readability

### Limitations

- Only analyzes .py files
- Does not follow dynamic imports (importlib, __import__, etc.)
- Does not handle conditional imports based on runtime conditions
- Standard library imports are filtered out