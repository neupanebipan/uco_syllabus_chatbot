# utils/llama_api.py
import requests
from utils.rag import retrieve_relevant_passage

def call_llm_multi(question, filepath):
    context = retrieve_relevant_passage(question, filepath)
    prompt = f"""
You are a helpful academic assistant that answers questions based on university syllabi.

Syllabus content:
{context}

Question:
{question}

Provide a clear, concise answer using any relevant dates or policies found in the syllabus.
"""
    payload = {
        "prompt": prompt,
        "max_tokens": 400,
        "temperature": 0.4,
        "top_p": 0.9,
        "repetition_penalty": 1.2,
        "top_k": 40
    }
    try:
        response = requests.post("http://csai01:8000/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "[No meaningful answer returned]")
    except requests.exceptions.RequestException as e:
        return f"LLM call failed: {str(e)}"