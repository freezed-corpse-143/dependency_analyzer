from collections import defaultdict


class DependencyGraph:
    def __init__(self):
        self.edges = defaultdict(set)

    def add(self, src, dst):
        self.edges[src].add(dst)

    def to_dict(self):
        return {k: sorted(list(v)) for k, v in self.edges.items()}
