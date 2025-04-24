# utils/llama_api.py
from utils.rag import retrieve_relevant_passage
import requests

def call_llm_multi(question, filepath):
    context = retrieve_relevant_passage(question, filepath)
    payload = {
        "prompt": f"From this syllabus context:\n{context}\nAnswer the question: {question}",
        "max_tokens": 200
    }
    try:
        res = requests.post("http://csai01:8000/generate", json=payload)
        return res.json().get("response", "No response returned.")
    except Exception as e:
        return f"LLM call failed: {e}"