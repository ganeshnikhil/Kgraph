import os
import asyncio
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from ollama import Client 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.graph.visulization import visualize_graph
from src.model.model_info import get_context_length
from src.utils.text_clean import clean_text

host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
client = Client(host=host)

class OllamaLLMWrapper:
    def __init__(self, client, model="llama2", temperature=0):
        self.client = client
        self.model = model
        self.temperature = temperature

    def __call__(self, prompt):
        response = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response["message"]["content"]
 
# -------------------
# 1️⃣ Async batch processor for large datasets
# -------------------
async def process_batches(documents, graph_transformer, batch_size=5):
    """
    Process documents in batches asynchronously to minimize memory footprint.
    """
    results = []
    batch = []
    for doc in documents:  # normal generator loop
        batch.append(doc)
        if len(batch) >= batch_size:
            batch_result = await graph_transformer.aconvert_to_graph_documents(batch)
            results.extend(batch_result)
            batch.clear()  # reset batch
    if batch:  # leftover batch
        batch_result = await graph_transformer.aconvert_to_graph_documents(batch)
        results.extend(batch_result)
    return results

# -------------------
# 2️⃣ Chunk size computation
# -------------------
def compute_chunk_size_tokens(context_length: int, safety_factor: float = 0.8, max_chunk: int = 5000):
    chunk_size = int(context_length * safety_factor)
    return min(chunk_size, max_chunk)

# -------------------
# 3️⃣ Knowledge graph generator
# -------------------
def generate_knowledge_graph(text: str, selected_model: str = None, batch_size: int = 5):
    """
    Generates a knowledge graph from text with cleaning, chunking, and async batch processing.
    """
    # Clean text
    if text:
        text = clean_text(text)

    # Select default model if not provided
    if not selected_model:
        selected_model = "gemma3:4b"

    # Get model context length
    context_length = get_context_length(selected_model) or 2048

    # Decide whether to split text
    if context_length <= len(text):
        chunk_size = compute_chunk_size_tokens(context_length)
        chunk_overlap = min(int(chunk_size * 0.05), 256)  # 5% overlap for efficiency

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "]
        )
        text_chunks = splitter.split_text(text)
        documents = [Document(page_content=chunk) for chunk in text_chunks]
    else:
        documents = [Document(page_content=text)]

    # Initialize LLM and Graph Transformer
    llm = OllamaLLMWrapper(client, model=selected_model, temperature=0)
    graph_transformer = LLMGraphTransformer(llm=llm)

    # Extract graph asynchronously in batches
    graph_documents = asyncio.run(process_batches(documents, graph_transformer, batch_size=batch_size))

    # Visualize knowledge graph
    net = visualize_graph(graph_documents)

    # Debug info
    print(f"Context length: {context_length}")
    print(f"Chunk size: {chunk_size if context_length <= len(text) else 'full text'}")
    print(f"Chunk overlap: {chunk_overlap if context_length <= len(text) else 0}")
    print(f"Total chunks: {len(documents)}")

    return net

