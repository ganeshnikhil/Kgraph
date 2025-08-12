import os 
import hashlib
from src.config.folder_con import DATA_DIR


def file_already_exist(hash_of_text):
    hash_files = [file_hash.replace(".html","") for file_hash in os.listdir(DATA_DIR) if file_hash.endswith('.html')]
    return  hash_of_text in hash_files


def hash_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def list_graph_files():
    return [f for f in os.listdir(DATA_DIR) if f.endswith('.html')]


def save_graph_html(net, filename):
    path = os.path.join(DATA_DIR, filename)
    net.save_graph(path)
    return path