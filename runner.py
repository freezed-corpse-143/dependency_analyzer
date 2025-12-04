from pathlib import Path

try:
    # When running as module: python -m dependency_analyzer
    from .parser import ImportParser
    from .resolver import ModuleResolver
    from .graph_builder import DependencyGraph
    from .visualizer import G6Visualizer
    from .utils import scan_py_files
except ImportError:
    # When running directly: python runner.py
    from parser import ImportParser
    from resolver import ModuleResolver
    from graph_builder import DependencyGraph
    from visualizer import G6Visualizer
    from utils import scan_py_files


class Analyzer:
    def __init__(self, root: str, enable_visual=True):
        self.root = Path(root)
        self.parser = ImportParser()
        self.resolver = ModuleResolver()
        self.graph = DependencyGraph()
        self.enable_visual = enable_visual

    def run(self):
        py_files = scan_py_files(self.root)

        for file in py_files:
            imports = self.parser.parse(file)
            for entry in imports:
                # For 'import module_b', entry.module is None, entry.names = ['module_b']
                # For 'from module_c import function_c', entry.module = 'module_c', entry.names = ['function_c']
                if entry.module is None:
                    # Simple import: import module_b
                    for name in entry.names:
                        resolved = self.resolver.resolve(name, self.root.as_posix())
                        if resolved:
                            # Convert to relative path
                            src_rel = "." + file.as_posix()[len(self.root.as_posix()):]
                            dst_rel = "." + resolved[len(self.root.as_posix()):]
                            self.graph.add(src_rel, dst_rel)
                else:
                    # From import: from module_c import ...
                    # Handle relative imports (e.g., .base, ..utils)
                    module_to_resolve = entry.module
                    if module_to_resolve.startswith('.'):
                        # Convert relative import to absolute based on file location
                        # Remove leading dots and build path relative to file's directory
                        rel_level = len(module_to_resolve) - len(module_to_resolve.lstrip('.'))
                        base_module = module_to_resolve.lstrip('.')
                        file_dir = file.parent
                        # Go up rel_level-1 directories
                        for _ in range(rel_level - 1):
                            file_dir = file_dir.parent
                        # Search from file_dir instead of project root
                        resolved = self.resolver.resolve(base_module, file_dir.as_posix())
                    else:
                        resolved = self.resolver.resolve(module_to_resolve, self.root.as_posix())
                    
                    if resolved:
                        # Convert to relative path
                        src_rel = "." + file.as_posix()[len(self.root.as_posix()):]
                        dst_rel = "." + resolved[len(self.root.as_posix()):]
                        self.graph.add(src_rel, dst_rel)

        result = self.graph.to_dict()

        if self.enable_visual:
            out = self.root / "dependency_graph.html"
            G6Visualizer().export(result, out.as_posix())

        return result