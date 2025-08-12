import os 
from dotenv import load_dotenv


load_dotenv()
DATA_DIR = os.getenv("GRAPH_DIR", "Data")
os.makedirs(DATA_DIR, exist_ok=True)
