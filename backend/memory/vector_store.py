import os
import re
from typing import List, Dict, Any
from backend.config import settings

class SimpleVectorStore:
    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir
        self.documents: List[Dict[str, Any]] = []
        self._load_documents()

    def _load_documents(self):
        self.documents = []
        if not os.path.exists(self.knowledge_dir):
            return

        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(self.knowledge_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Split by sections or double linebreaks
                sections = re.split(r'\n(?=###?\s)', content)
                for idx, sec in enumerate(sections):
                    text = sec.strip()
                    if text:
                        # Extract section header if present
                        lines = text.split('\n')
                        header = lines[0].replace('#', '').strip() if lines[0].startswith('#') else filename
                        self.documents.append({
                            "id": f"{filename}_{idx}",
                            "source": filename,
                            "header": header,
                            "content": text
                        })

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        if not self.documents:
            self._load_documents()

        query_terms = set(re.findall(r'\w+', query.lower()))
        results = []

        for doc in self.documents:
            doc_text = doc["content"].lower()
            doc_terms = set(re.findall(r'\w+', doc_text))
            
            # Simple term overlap scoring
            overlap = query_terms.intersection(doc_terms)
            score = len(overlap) / (len(query_terms) + 1)

            # Boost if query matches header specifically
            header_terms = set(re.findall(r'\w+', doc["header"].lower()))
            if query_terms.intersection(header_terms):
                score += 0.5

            if score > 0:
                results.append((score, doc))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        top_docs = [item[1] for item in results[:top_k]]

        # Fallback if no term match
        if not top_docs and self.documents:
            top_docs = [self.documents[0]]

        return top_docs

# Global vector store instance
vector_store = SimpleVectorStore(settings.KNOWLEDGE_BASE_DIR)

def search_knowledge_base(query: str, top_k: int = 2) -> str:
    """RAG retrieval interface for agents."""
    docs = vector_store.search(query, top_k=top_k)
    snippets = []
    for d in docs:
        snippets.append(f"--- Source: {d['source']} [{d['header']}] ---\n{d['content']}")
    return "\n\n".join(snippets)
