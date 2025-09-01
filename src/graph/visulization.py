from pyvis.network import Network
from collections import defaultdict

def visualize_graph(graph_documents, max_nodes=None):
    """
    Builds a PyVis knowledge graph from one or more GraphDocument objects with enhanced visualization.
    
    Args:
        graph_documents (list): List of GraphDocument objects.
        max_nodes (int, optional): If set, limits number of nodes for performance.
        
    Returns:
        Network: PyVis Network object.
    """
    net = Network(
        height="900px", width="100%", directed=True,
        bgcolor="#1e1e1e", font_color="white",
        notebook=False, filter_menu=True, cdn_resources="remote"
    )

    if not graph_documents:
        print("No graph documents.")
        return net

    node_color_map = {
        "Person": "#FFB347",
        "Organization": "#87CEEB",
        "Location": "#90EE90",
        "Concept": "#DA70D6",
        "Event": "#FF6F61",
        "Default": "#D3D3D3"
    }

    # --- Merge nodes and edges from all documents ---
    node_dict = {}
    edges = []
    for doc in graph_documents:
        for node in doc.nodes:
            node_dict[node.id] = node  # overwrite duplicates
        for rel in doc.relationships:
            edges.append(rel)

    # Compute node importance (degree)
    degree_count = defaultdict(int)
    for rel in edges:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            degree_count[rel.source.id] += 1
            degree_count[rel.target.id] += 1

    # Optional: limit nodes for very large graphs
    if max_nodes:
        # Keep only top nodes by degree
        top_nodes = set(sorted(degree_count, key=degree_count.get, reverse=True)[:max_nodes])
        edges = [e for e in edges if e.source.id in top_nodes and e.target.id in top_nodes]
        node_dict = {nid: node_dict[nid] for nid in top_nodes}
        degree_count = {nid: degree_count[nid] for nid in top_nodes}

    # --- Add nodes ---
    def truncate_label(label, max_len=30):
        return label if len(label) <= max_len else label[:max_len] + "..."

    for node_id, node in node_dict.items():
        importance = degree_count.get(node_id, 1)
        net.add_node(
            node.id,
            label=truncate_label(node.id),
            title=f"<b>ID:</b> {node.id}<br><b>Type:</b> {node.type}<br><b>Degree:</b> {importance}",
            color=node_color_map.get(node.type, node_color_map["Default"]),
            shape="dot",
            size=15 + min(importance * 2, 40),  # scale size
            font={
                "size": 18,       # slightly bigger
                "color": "#FFFF00",  # bright yellow
                "face": "Arial",
                "strokeWidth": 1,
                "strokeColor": "#000000",
                "bold": True},  # subtle outline for readability},
            group=node.type
        )

    # --- Add edges ---
    for rel in edges:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            # Edge width/color based on type
            edge_color = "#999999"
            width = 2
            if rel.type.lower() in ["parent", "owns", "leads"]:
                edge_color = "#FF6F61"
                width = 4
            elif rel.type.lower() in ["associated", "related"]:
                edge_color = "#87CEEB"
                width = 3
            net.add_edge(
                rel.source.id,
                rel.target.id,
                label=rel.type.title(),
                arrows="to",
                color=edge_color,
                width=width,
                smooth={"enabled": True, "type": "dynamic"},
                font={"color": "#FFFFFF", "size": 12}
            )

    # --- Network options ---
    net.set_options("""
    {
      "layout": {
        "improvedLayout": true
      },
      "nodes": {
        "borderWidth": 1,
        "shadow": true
      },
      "edges": {
        "color": {
          "inherit": false
        },
        "smooth": {
          "enabled": true,
          "type": "dynamic"
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": {"enabled": true},
        "tooltipDelay": 200
      },
      "physics": {
        "enabled": true,
        "solver": "barnesHut",
        "barnesHut": {
          "gravitationalConstant": -2500,
          "centralGravity": 0.2,
          "springLength": 200,
          "springConstant": 0.02,
          "damping": 0.09
        },
        "minVelocity": 0.75,
        "stabilization": {"enabled": true, "iterations": 200}
      }
    }
    """)

    return net
