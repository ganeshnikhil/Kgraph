import asyncio
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.graph.visulization import visualize_graph
from src.model.model_info import get_context_length
from src.utils.text_clean import clean_text

# #host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# -------------------
# 1️⃣ Async batch processor for large datasets
# -------------------
async def process_batches(documents, graph_transformer, batch_size=5):
    """
    Process documents in batches asynchronously to minimize memory footprint.
    """
    results = []
    batch = []

    for doc in documents:
        batch.append(doc)
        if len(batch) >= batch_size:
            try:
                batch_result = await graph_transformer.aconvert_to_graph_documents(batch)
                results.extend(batch_result)
            except Exception as e:
                print(f"[Batch Error] {e}")
            finally:
                batch.clear()

    if batch:  # process leftover batch
        try:
            batch_result = await graph_transformer.aconvert_to_graph_documents(batch)
            results.extend(batch_result)
        except Exception as e:
            print(f"[Final Batch Processing Error] Skipping final batch due to: {e}")
    return results


# -------------------
# 2️⃣ Chunk size computation
# -------------------
def compute_chunk_size_tokens(context_length: int, safety_factor: float = 0.8, max_chunk: int = 2000) -> int:
    """
    Compute chunk size based on model context length with a safety margin.
    """
    chunk_size = int(context_length * safety_factor)
    return min(chunk_size, max_chunk)


# -------------------
# 3️⃣ Knowledge graph generator
# -------------------
def generate_knowledge_graph(text: str, selected_model: str = None, batch_size: int = 5):
    """
    Generates a knowledge graph from text with cleaning, chunking, and async batch processing.
    """

    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")

    # Clean text
    text = clean_text(text)

    # Select default model if not provided
    selected_model = selected_model or "gemma3:4b"

    # Get model context length safely
    try:
        context_length = get_context_length(selected_model)
        if not context_length:
            print(f"[Warning] Could not determine context length for {selected_model}, using 2048")
            context_length = 2048
    except Exception as e:
        print(f"[Error getting context length] {e}, defaulting to 2048")
        context_length = 2048

    # Defaults for debugging info
    chunk_size = "full text"
    chunk_overlap = 0

    # Decide whether to split text
    if context_length <= len(text):
        chunk_size = compute_chunk_size_tokens(context_length)
        chunk_overlap = min(int(chunk_size * 0.05), 256)  # 5% overlap

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
    llm = ChatOllama(model=selected_model, temperature=0)
    graph_transformer = LLMGraphTransformer(llm=llm)

    # Simpler, cleaner, and standard way to run a coroutine
    graph_documents = asyncio.run(
        process_batches(documents, graph_transformer, batch_size)
    )

    net = visualize_graph(graph_documents)

    # Debug info
    print(f"Context length: {context_length}")
    print(f"Chunk size: {chunk_size}")
    print(f"Chunk overlap: {chunk_overlap}")
    print(f"Total chunks: {len(documents)}")

    return net


# import asyncio
# import threading
# from langchain_experimental.graph_transformers import LLMGraphTransformer
# from langchain_core.documents import Document
# from langchain_ollama import ChatOllama
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from src.graph.visulization import visualize_graph
# from src.model.model_info import get_context_length
# from src.utils.text_clean import clean_text

# # -------------------
# # 1️⃣ Async batch processor
# # -------------------
# async def process_batches(documents, graph_transformer, batch_size=5):
#     results = []
#     batch = []

#     for doc in documents:
#         batch.append(doc)
#         if len(batch) >= batch_size:
#             try:
#                 batch_result = await graph_transformer.aconvert_to_graph_documents(batch)
#                 results.extend(batch_result)
#             except Exception as e:
#                 print(f"[Batch Error] {e}")
#             finally:
#                 batch.clear()

#     if batch:
#         try:
#             batch_result = await graph_transformer.aconvert_to_graph_documents(batch)
#             results.extend(batch_result)
#         except Exception as e:
#             print(f"[Final Batch Error] {e}")

#     return results

# # -------------------
# # 2️⃣ Run async in background thread (Streamlit-safe)
# # -------------------
# def run_async_in_thread(coroutine):
#     """
#     Runs an async coroutine in a background thread and returns the result.
#     """
#     result = []

#     def _runner():
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         result.append(loop.run_until_complete(coroutine))

#     thread = threading.Thread(target=_runner)
#     thread.start()
#     thread.join()
#     return result[0]

# # -------------------
# # 3️⃣ Compute chunk size
# # -------------------
# def compute_chunk_size_tokens(context_length: int, safety_factor: float = 0.8, max_chunk: int = 2000):
#     chunk_size = int(context_length * safety_factor)
#     return min(chunk_size, max_chunk)

# # -------------------
# # 4️⃣ Knowledge graph generator
# # -------------------
# def generate_knowledge_graph(text: str, selected_model: str = None, batch_size: int = 5):
#     if not text or not text.strip():
#         raise ValueError("Input text cannot be empty")

#     text = clean_text(text)
#     selected_model = selected_model or "gemma3:4b"

#     try:
#         context_length = get_context_length(selected_model) or 2048
#     except Exception as e:
#         print(f"[Error getting context length] {e}, defaulting to 2048")
#         context_length = 2048

#     chunk_size = "full text"
#     chunk_overlap = 0

#     # Split text into bigger chunks to reduce LLM calls
#     if context_length <= len(text):
#         chunk_size = compute_chunk_size_tokens(context_length, safety_factor=0.95, max_chunk=8000)
#         chunk_overlap = min(int(chunk_size * 0.05), 256)

#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             separators=["\n\n", "\n", ".", " "]
#         )
#         text_chunks = splitter.split_text(text)
#         documents = [Document(page_content=chunk) for chunk in text_chunks]
#     else:
#         documents = [Document(page_content=text)]

#     # Initialize model and transformer
#     llm = ChatOllama(model=selected_model, temperature=0)
#     graph_transformer = LLMGraphTransformer(llm=llm)

#     # Async processing in background thread for Streamlit
#     graph_documents = run_async_in_thread(process_batches(documents, graph_transformer, batch_size))

#     # Visualize
#     net = visualize_graph(graph_documents)

#     # Debug info
#     print(f"Context length: {context_length}")
#     print(f"Chunk size: {chunk_size}")
#     print(f"Chunk overlap: {chunk_overlap}")
#     print(f"Total chunks: {len(documents)}")

#     return net


# import asyncio
# from langchain_experimental.graph_transformers import LLMGraphTransformer
# from langchain_core.documents import Document
# from langchain_ollama import ChatOllama
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from src.graph.visulization import visualize_graph
# from src.model.model_info import get_context_length
# from src.utils.text_clean import clean_text

# # -------------------
# # 1️⃣ Parallel async batch processor
# # -------------------
# async def process_batches_parallel(documents, graph_transformer, batch_size=5, max_concurrent_batches=3):
#     results = []
#     batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]

#     semaphore = asyncio.Semaphore(max_concurrent_batches)

#     async def process_single_batch(batch):
#         try:
#             return await graph_transformer.aconvert_to_graph_documents(batch)
#         except Exception as e:
#             print(f"[Batch Error] {e}")
#             return []

#     async def sem_task(batch):
#         async with semaphore:
#             return await process_single_batch(batch)

#     tasks = [sem_task(batch) for batch in batches]
#     batch_results = await asyncio.gather(*tasks)
#     for res in batch_results:
#         results.extend(res)
#     return results

# # -------------------
# # 2️⃣ Streamlit-safe async runner
# # -------------------
# def run_async(coroutine):
#     """
#     Run async coroutine safely in Streamlit or normal script.
#     """
#     try:
#         return asyncio.run(coroutine)
#     except RuntimeError:
#         # Already running loop (e.g., Streamlit), create task
#         loop = asyncio.get_event_loop()
#         return loop.run_until_complete(coroutine)

# # -------------------
# # 3️⃣ Compute chunk size
# # -------------------
# def compute_chunk_size_tokens(context_length: int, safety_factor: float = 0.8, max_chunk: int = 2000):
#     chunk_size = int(context_length * safety_factor)
#     return min(chunk_size, max_chunk)

# # -------------------
# # 4️⃣ Optimized knowledge graph generator
# # -------------------
# def generate_knowledge_graph(text: str, selected_model: str = None, batch_size: int = 5):
#     if not text or not text.strip():
#         raise ValueError("Input text cannot be empty")

#     text = clean_text(text)
#     selected_model = selected_model or "gemma3:4b"

#     try:
#         context_length = get_context_length(selected_model) or 2048
#     except Exception as e:
#         print(f"[Error getting context length] {e}, defaulting to 2048")
#         context_length = 2048

#     # Adaptive chunking
#     if len(text) > context_length:
#         chunk_size = compute_chunk_size_tokens(context_length, safety_factor=0.95, max_chunk=8000)
#         chunk_overlap = min(int(chunk_size * 0.05), 256)
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             separators=["\n\n", "\n", ".", " "]
#         )
#         text_chunks = splitter.split_text(text)
#         documents = [Document(page_content=chunk) for chunk in text_chunks]
#     else:
#         documents = [Document(page_content=text)]
#         chunk_size = "full text"
#         chunk_overlap = 0

#     # -------------------
#     # Initialize LLM and graph transformer (reuse for speed)
#     # -------------------
#     llm = ChatOllama(model=selected_model, temperature=0)
#     graph_transformer = LLMGraphTransformer(llm=llm)

#     # -------------------
#     # Process batches asynchronously
#     # -------------------
#     graph_documents = run_async(process_batches_parallel(documents, graph_transformer, batch_size))

#     # -------------------
#     # Visualize
#     # -------------------
#     net = visualize_graph(graph_documents)

#     # -------------------
#     # Debug info
#     # -------------------
#     print(f"Context length: {context_length}")
#     print(f"Chunk size: {chunk_size}")
#     print(f"Chunk overlap: {chunk_overlap}")
#     print(f"Total chunks: {len(documents)}")

#     return net
