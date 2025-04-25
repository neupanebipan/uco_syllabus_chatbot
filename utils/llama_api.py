# utils/llama_api.py
import requests
from utils.rag import retrieve_relevant_passage

def call_llm_multi(question, filepath):
    context = retrieve_relevant_passage(question, filepath)
    prompt = f"""
You are a university syllabus assistant. The following content was extracted from a course syllabus. It may include a schedule, topics, exam dates, or grading breakdowns.

Your job is to answer the student's question clearly and precisely based on the syllabus context.

Syllabus Content:
{context}

Student Question:
{question}

If the syllabus includes dates, weeks, topic titles, or grading components related to the question, include those in your answer. Do not guess if the syllabus does not provide a clear answer.
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