from backend.scripts.rag_pipeline import rag_answer
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


print("Policy Q&A Chatbot (Ollama + FAISS)\nType 'exit' to quit.\n")

while True:
    q = input("Ask: ")
    if q.lower() in ["exit", "quit"]:
        break
    ans = rag_answer(q)
    print(f"\nAnswer: {ans}\n")
