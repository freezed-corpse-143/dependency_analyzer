import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, DefaultDict
from collections import defaultdict


class G6Visualizer:
    """Generate an interactive dependency graph using AntV G6 with combo support."""

    TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Python Dependency Graph</title>
  <script src="https://unpkg.com/@antv/g6@5/dist/g6.min.js"></script>
  <style>
    html, body, #container {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
    }
  </style>
</head>
<body>
<div id="container"></div>
<script>
const data = __DATA__;

const graph = new G6.Graph({
  container: 'container',
  width: window.innerWidth,
  height: window.innerHeight,
  data,
  // Disable G6 layout since we provide initial positions
  layout: false,
  node: {
    style: {
      labelText: (d) => d.text || d.id,
      size: 30,
      fill: '#79a7d3',
      stroke: '#2a4d7a',
      lineWidth: 2,
    },
  },
  edge: {
    type: 'line',
    style: {
      endArrow: true,
      stroke: '#888',
      lineWidth: 2,
    },
  },
  combo: {
    type: 'rect',
    style: {
      labelText: (d) => d.id,
      fill: '#f0f0f0',
      stroke: '#ccc',
      lineWidth: 1,
      padding: 20,
    },
  },
  behaviors: ['drag-canvas', 'zoom-canvas', 'drag-element', 'collapse-expand-combo'],
});

graph.render();
// Fit view to show all elements after render
graph.on('afterrender', (e) => {
  // Set positions from style attributes
  const { nodes, combos } = graph.getData();
  nodes.forEach(node => {
    const style = node.style || {};
    if (style.x !== undefined && style.y !== undefined) {
      graph.updateItem(node.id, {
        x: style.x,
        y: style.y
      });
    }
  });
  combos.forEach(combo => {
    const style = combo.style || {};
    if (style.x !== undefined && style.y !== undefined) {
      graph.updateItem(combo.id, {
        x: style.x,
        y: style.y
      });
    }
  });
  graph.fitView([20, 20]);
});
</script>
</body>
</html>"""

    def _extract_dirs(self, path: str) -> List[str]:
        """Extract all parent directories from a file path."""
        dirs = []
        # Handle relative paths starting with ./
        if path.startswith("./"):
            path = path[2:]
        
        path = path.rstrip(os.sep)
        while True:
            path = os.path.dirname(path)
            if not path or path == os.sep or path == ".":
                break
            # Prepend ./ for relative paths
            if not path.startswith("/"):
                path = "./" + path
            dirs.append(path)
            # Remove ./ for next iteration
            if path.startswith("./"):
                path = path[2:]
        return dirs

    def _calculate_positions(self, nodes: List[Dict], combos: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Calculate initial positions for nodes and combos based on directory hierarchy.
        
        Algorithm:
        1. Group nodes by their combo (directory)
        2. Calculate directory depth (number of path segments)
        3. Position directories horizontally by depth, vertically by sibling order
        4. Position nodes within their directory vertically
        5. Center the entire graph in the viewport
        """
        # Group nodes by combo
        nodes_by_combo: DefaultDict[str, List[Dict]] = defaultdict(list)
        for node in nodes:
            combo_id = node.get("combo", ".")
            nodes_by_combo[combo_id].append(node)
        
        # Calculate directory depth and group combos by depth
        combos_by_depth: DefaultDict[int, List[Dict]] = defaultdict(list)
        for combo in combos:
            # Calculate depth based on path segments
            path = combo["id"]
            if path == ".":
                depth = 0
            else:
                # Count path segments, handling ./ prefix
                normalized_path = path[2:] if path.startswith("./") else path
                depth = normalized_path.count(os.sep) + 1
            combo["depth"] = depth
            combos_by_depth[depth].append(combo)
        
        # Constants for layout
        NODE_SPACING = 80
        COMBO_SPACING = 200
        DEPTH_SPACING = 300
        CENTER_X = 800  # Approximate center of browser
        CENTER_Y = 400  # Approximate center of browser
        
        # Calculate positions for combos
        # First pass: assign preliminary positions
        for depth, depth_combos in sorted(combos_by_depth.items()):
            # Sort combos at this depth for consistent ordering
            depth_combos.sort(key=lambda c: c["id"])
            
            for i, combo in enumerate(depth_combos):
                # Horizontal position based on depth
                x = CENTER_X + (depth - 1) * DEPTH_SPACING
                
                # Vertical position based on sibling order
                # Center combos vertically at each depth
                total_at_depth = len(depth_combos)
                start_y = CENTER_Y - (total_at_depth - 1) * COMBO_SPACING / 2
                y = start_y + i * COMBO_SPACING
                
                # Store position in style attribute
                if "style" not in combo:
                    combo["style"] = {}
                combo["style"]["x"] = x
                combo["style"]["y"] = y
        
        # Calculate positions for nodes within their combos
        for combo_id, combo_nodes in nodes_by_combo.items():
            # Find the combo to get its position
            parent_combo = None
            for combo in combos:
                if combo["id"] == combo_id:
                    parent_combo = combo
                    break
            
            if not parent_combo:
                continue
            
            # Sort nodes for consistent ordering
            combo_nodes.sort(key=lambda n: n["id"])
            
            # Calculate node positions relative to combo center
            # Get position from style attribute
            combo_x = parent_combo.get("style", {}).get("x", CENTER_X)
            combo_y = parent_combo.get("style", {}).get("y", CENTER_Y)
            
            total_nodes = len(combo_nodes)
            if total_nodes == 1:
                # Single node at combo center
                node_y_offset = 0
            else:
                # Distribute nodes vertically within combo
                node_y_offset = -(total_nodes - 1) * NODE_SPACING / 2
            
            for i, node in enumerate(combo_nodes):
                node_x = combo_x
                node_y = combo_y + node_y_offset + i * NODE_SPACING
                
                # Store position in style attribute
                if "style" not in node:
                    node["style"] = {}
                node["style"]["x"] = node_x
                node["style"]["y"] = node_y
        
        # Calculate bounding box to center the entire graph
        all_elements = nodes + combos
        if all_elements:
            # Find min and max coordinates from style attributes
            xs = []
            ys = []
            for e in all_elements:
                style = e.get("style", {})
                if "x" in style:
                    xs.append(style["x"])
                if "y" in style:
                    ys.append(style["y"])
            
            if xs and ys:
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                
                # Calculate center of current graph
                graph_center_x = (min_x + max_x) / 2
                graph_center_y = (min_y + max_y) / 2
                
                # Calculate translation to center in viewport
                translate_x = CENTER_X - graph_center_x
                translate_y = CENTER_Y - graph_center_y
                
                # Apply translation to all elements' style attributes
                for element in all_elements:
                    style = element.get("style", {})
                    if "x" in style:
                        style["x"] += translate_x
                    if "y" in style:
                        style["y"] += translate_y
        
        # Remove temporary depth attribute from combos
        for combo in combos:
            if "depth" in combo:
                del combo["depth"]
        
        return nodes, combos
    
    def build_graph(self, graph_dict: Dict[str, List[str]]) -> Dict:
        """Build graph data with nodes, edges, and combos for folder hierarchy."""
        # Collect all unique nodes from both keys and values
        node_set: Set[str] = set()
        edges = []
        
        for src, targets in graph_dict.items():
            node_set.add(src)
            for t in targets:
                node_set.add(t)
                edges.append({
                    "source": src,
                    "target": t,
                    "id": f"{src}->{t}"
                })
        
        # Create nodes with combo assignment
        nodes = []
        for node in sorted(node_set):
            # Get display name (basename)
            display_name = os.path.basename(node)
            if not display_name:
                display_name = node
            
            node_data = {
                "id": node,
                "text": display_name,
            }
            # Assign combo based on parent directory
            parent_dir = os.path.dirname(node)
            if parent_dir == ".":
                # Root directory files belong to root combo
                node_data["combo"] = "."
            elif parent_dir:
                # Ensure parent_dir has ./ prefix if it's a relative path
                if not parent_dir.startswith("/") and not parent_dir.startswith("./"):
                    parent_dir = "./" + parent_dir
                node_data["combo"] = parent_dir
            nodes.append(node_data)
        
        # Create combos for all directories
        dir_set: Set[str] = set()
        # Add root directory
        dir_set.add(".")
        for node in node_set:
            dir_set.update(self._extract_dirs(node))
        
        combos = []
        for dir_path in sorted(dir_set, key=len):
            # Get display name
            display_name = os.path.basename(dir_path)
            if not display_name or display_name == ".":
                display_name = "root"
            
            combo_data = {
                "id": dir_path,
                "text": display_name,
            }
            # Assign parent combo if not root
            parent_dir = os.path.dirname(dir_path)
            if parent_dir and parent_dir != ".":
                # Ensure parent_dir has ./ prefix if it's a relative path
                if not parent_dir.startswith("/") and not parent_dir.startswith("./"):
                    parent_dir = "./" + parent_dir
                if parent_dir in dir_set:
                    combo_data["combo"] = parent_dir
            combos.append(combo_data)
        
        # Calculate initial positions for nodes and combos
        nodes, combos = self._calculate_positions(nodes, combos)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "combos": combos
        }

    def export(self, graph_dict: Dict[str, List[str]], out: str):
        """Export dependency graph to HTML file."""
        data = json.dumps(self.build_graph(graph_dict), indent=2)
        html = self.TEMPLATE.replace("__DATA__", data)
        Path(out).write_text(html, encoding="utf-8")
        print(f"[✔] Exported dependency visualization with combo support → {out}")
        return out