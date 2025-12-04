import os
from typing import Optional

try:
    # When running as module: python -m dependency_analyzer
    from .config import should_ignore
except ImportError:
    # When running directly
    from config import should_ignore


class ModuleResolver:
    """Resolve Python import paths to real file paths."""

    def resolve(self, module: str, search_dir: str) -> Optional[str]:
        if not module:
            return None

        module_path = module.replace(".", "/")

        candidates = [f"{module_path}.py", f"{module_path}/__init__.py"]

        for root, _, _ in os.walk(search_dir):
            if should_ignore(root):
                continue

            for c in candidates:
                full = os.path.join(root, c)
                if os.path.exists(full):
                    return os.path.abspath(full)

        return None