import os
import shutil
import chromadb
from chromadb.utils import embedding_functions

# ---------------------------------------------------------
# ChromaDB initialization
# ---------------------------------------------------------

# Reset ChromaDB store on startup
shutil.rmtree("chroma_store", ignore_errors=True)

client = chromadb.PersistentClient(path="chroma_store")
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="assignment_knowledgebase",
    embedding_function=embedding_fn,
)


# ---------------------------------------------------------
# Load all .txt documents from /data into ChromaDB
# ---------------------------------------------------------

def load_documents():
    folder = "data"
    if not os.path.exists(folder):
        return

    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # Avoid duplicate insertion
        existing = collection.get(ids=[filename])
        if existing["ids"]:
            continue

        collection.add(ids=[filename], documents=[text])


load_documents()


# ---------------------------------------------------------
# Semantic search - supports top_k for reranking
# ---------------------------------------------------------

def semantic_search(query: str, top_k: int = 5):
    """
    Returns a list of candidate documents from ChromaDB.
    Each candidate is a dict: {"id": filename, "text": document_text}
    """
    try:
        results = collection.query(query_texts=[query], n_results=top_k)

        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]

        if not docs:
            return []   # return empty list because rerank() always expects a list

        candidates = []
        # zip() pairs each document ID with its corresponding document text
        for doc_id, text in zip(ids, docs):
            candidates.append({"id": doc_id, "text": text})

        return candidates

    except Exception:
        return []


# ---------------------------------------------------------
# Filename‑based reranker
# ---------------------------------------------------------

# Reranker uses filename hints to override embedding mistakes
def rerank(query: str, candidates: list) -> str:
    """
    Picks the best candidate based on filename hints.
    This avoids wrong matches like 'summary' for 'main characters'.
    """
    if not candidates:
        return (
            "I didn't find anything that matched that question, "
            "but you can try asking in a different way."
        )

    q = query.lower()

    # Priority rules based on filenames in data/
    if "summary" in q:
        for c in candidates:
            if "summary" in c["id"].lower():
                return c["text"]

    if "character" in q:
        for c in candidates:
            if "character" in c["id"].lower():
                return c["text"]

    if "plot" in q:
        for c in candidates:
            if "plot" in c["id"].lower():
                return c["text"]

    # Return the top embedding result
    return candidates[0]["text"]