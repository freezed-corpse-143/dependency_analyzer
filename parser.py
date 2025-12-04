import ast
from dataclasses import dataclass
from typing import List


@dataclass
class ImportEntry:
    module: str | None
    names: list[str]


class ImportParser:
    """Parse Python imports using AST."""

    def parse(self, file_path: str) -> List[ImportEntry]:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        results = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                results.append(
                    ImportEntry(None, [alias.name for alias in node.names])
                )

            elif isinstance(node, ast.ImportFrom):
                base = ("." * node.level) + (node.module or "")
                results.append(
                    ImportEntry(base, [alias.name for alias in node.names])
                )

        return results
