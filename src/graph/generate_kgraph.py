from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from src.graph.visulization import visualize_graph
import asyncio

# --- Async graph data extraction ---
async def extract_graph_data(text, graph_transformer):
    """
    Asynchronously extracts graph data from input text using a LangChain graph transformer.

    Args:
        text (str): Input text to be processed.

    Returns:
        list: GraphDocument objects with nodes and relationships.
    """
    documents = [Document(page_content=text)]
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    return graph_documents

# --- Main API ---
def generate_knowledge_graph(text: str, selected_model: str):
    """
    Orchestrates LLM-based extraction and visualization of a knowledge graph.

    Args:
        text (str): Input document text.
        selected_model (str): Name of local Ollama model to use.

    Returns:
        Network: PyVis network graph object.
    """
    if not selected_model:
        selected_model = "gemma"  # fallback model
    llm = ChatOllama(temperature=0, model=selected_model)
    graph_transformer = LLMGraphTransformer(llm=llm)
    graph_documents = asyncio.run(extract_graph_data(text, graph_transformer))
    net = visualize_graph(graph_documents)
    return net
