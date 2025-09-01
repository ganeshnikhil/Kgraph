import os
import streamlit as st
import streamlit.components.v1 as components
from src.graph.generate_kgraph import generate_knowledge_graph
from src.utils.file_op import hash_text , list_graph_files ,save_graph_html , file_already_exist 
from src.model.model_info import get_ollama_models
from src.config.folder_con import DATA_DIR

# --- Load environment variables ---
def display_graph_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=1000, width=1500, scrolling=True)


# --- Streamlit UI ---
st.set_page_config(page_title="Knowledge Graph From Text", layout="wide")
st.title("🧠 Knowledge Graph From Text")

# --- Sidebar: Input ---
st.sidebar.title("📄 Input Document")
input_method = st.sidebar.radio("Choose input method:", ["Upload txt", "Input text"])

text = ""
if input_method == "Upload txt":
    uploaded_file = st.sidebar.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")
else:
    text = st.sidebar.text_area("Enter text:", height=300)

# --- Sidebar: Model Selection ---
st.sidebar.title("🤖 Ollama Model")
ollama_models = get_ollama_models()
if not ollama_models:
    st.sidebar.warning("⚠️ No Ollama models found. Use `ollama pull <model>` in your terminal.")
selected_model = st.sidebar.selectbox("Select a model (fallback: gemma)", [""] + ollama_models)


# --- Button to generate graph ---
if text and st.sidebar.button("Generate Knowledge Graph"):
    hash_of_text = hash_text(text)
    if file_already_exist(hash_of_text):
        filepath = os.path.join(DATA_DIR, f"{hash_of_text}.html")
        display_graph_html(filepath)
    else:
        with st.spinner("Generating knowledge graph..."):
            model_to_use = selected_model or "gemma"
            net = generate_knowledge_graph(text, model_to_use)
            filename = hash_of_text + ".html"
            save_path = save_graph_html(net, filename)
            st.success(f"Graph saved as `{filename}`")
            display_graph_html(save_path)

# --- Sidebar: Load stored graphs ---
st.sidebar.title("📁 Load Existing Graph")
graph_files = list_graph_files()

selected_graph = st.sidebar.selectbox("Select a graph to view:", ["-- Select --"] + graph_files)

if selected_graph != "-- Select --":
    st.info(f"Showing saved graph: `{selected_graph}`")
    filepath = os.path.join(DATA_DIR, selected_graph)
    display_graph_html(filepath)

