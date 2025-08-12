from pyvis.network import Network

def visualize_graph(graph_documents):
    """
    Builds and styles a PyVis knowledge graph from extracted nodes and relationships.

    Args:
        graph_documents (list): GraphDocument objects.

    Returns:
        Network: A PyVis Network object.
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

    doc = graph_documents[0]
    node_dict = {node.id: node for node in doc.nodes}

    valid_edges = []
    valid_node_ids = set()

    for rel in doc.relationships:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            valid_edges.append(rel)
            valid_node_ids.update([rel.source.id, rel.target.id])

    def truncate_label(label, max_len=30):
        return label if len(label) <= max_len else label[:max_len] + "..."

    for node_id in valid_node_ids:
        node = node_dict[node_id]
        label = truncate_label(node.id)
        net.add_node(
            node.id,
            label=label,
            title=f"<b>ID:</b> {node.id}<br><b>Type:</b> {node.type}",
            color=node_color_map.get(node.type, node_color_map["Default"]),
            shape="dot",
            size=35,
            font={"size": 20, "color": "white"},
            group=node.type
        )

    for rel in valid_edges:
        net.add_edge(
            rel.source.id,
            rel.target.id,
            label=rel.type.title(),
            font={"color": "#ffffff", "size": 14, "face": "arial"},
            arrows="to",
            color="#999999",
            smooth={"enabled": True, "type": "dynamic"}
        )

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
        "keyboard": {
          "enabled": true
        },
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
        "stabilization": {
          "enabled": true,
          "iterations": 200
        }
      }
    }
    """)

    return net
