import requests
from utils.rag import retrieve_relevant_passage

def call_llm_multi(question, filepath):
    context = retrieve_relevant_passage(question, filepath)

    if not context.strip():
        return {"role": "assistant", "content": "No syllabus information available for answering this question."}

    prompt = f"""
You are a university syllabus assistant. You must ONLY answer based on the syllabus content provided below. 
Do NOT guess. If the information is missing from the syllabus, clearly state that it is not available.

--- Syllabus Content ---
{context}
------------------------

Student Question:
{question}

Focus on being syllabus-specific, and prioritize accuracy.
"""

    payload = {
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.2,
        "top_p": 0.9,
        "repetition_penalty": 1.2,
        "top_k": 40
    }

    try:
        response = requests.post("http://csai01:8000/generate", json=payload, timeout=20)
        return response.json()
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"role": "assistant", "content": "Sorry, there was an error generating the answer."}
