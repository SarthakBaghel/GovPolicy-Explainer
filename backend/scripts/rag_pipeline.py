import os
import subprocess
from pathlib import Path
from backend.scripts.retriever import search

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def query_ollama(prompt: str, model: str = "phi3:mini") -> str:
    """
    Send a prompt to Ollama and return the generated response.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print("❌ Ollama error:", e.stderr.decode("utf-8"))
        return ""


def build_prompt(question: str, retrieved_docs: list) -> str:
    """
    Construct a prompt for the LLM using full text from retrieved documents.
    """
    context_blocks = []
    for score, meta in retrieved_docs:
        # Prefer full text if available, else fallback to preview
        text = meta.get("text") or meta.get("preview", "")
        source = meta.get("source", "unknown")
        block = f"[Source: {source}] {text}"
        context_blocks.append(block)

    context = "\n\n".join(context_blocks)

    prompt = f"""
You are an AI assistant answering based on policy documents.

Question:
{question}

Relevant context:
{context}

Answer clearly and concisely, using only the provided context. 
If the context does not contain enough information, say so.
"""
    return prompt.strip()



def rag_answer(question: str,
               index_dir: str = "data/outputs/index",
               k: int = 3,
               embed_model: str = "sentence-transformers/all-MiniLM-L6-v2",
               llm_model: str = "phi3:mini") -> str:
    """
    Retrieve relevant chunks and query Ollama for a final answer.
    """
    # 1. Retrieve documents
    results = search(index_dir, question, k=k, model_name=embed_model)

    if not results:
        return "❌ No relevant documents found."

    # 2. Build prompt
    prompt = build_prompt(question, results)

    # 3. Query Ollama
    answer = query_ollama(prompt, model=llm_model)

    return answer
