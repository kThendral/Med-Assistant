import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)

doc_texts = []
file_names = []

def index_documents(folder="medical_docs"):
    global file_names
    for fname in os.listdir(folder):
        with open(os.path.join(folder, fname), 'r') as f:
            text = f.read()
            doc_texts.append(text)
            file_names.append(fname)

    embeddings = model.encode(doc_texts)
    index.add(np.array(embeddings))

def get_similar_doc(query):
    q_embed = model.encode([query])
    D, I = index.search(np.array(q_embed), k=1)
    return doc_texts[I[0][0]]
