
import requests

def call_llm(question, syllabus_filename):
    payload = {
        "prompt": f"Given the syllabus in file {syllabus_filename}, answer this: {question}",
        "max_tokens": 200
    }
    try:
        response = requests.post("http://csai01:8000/generate", json=payload)
        return response.json().get("response", "No answer returned.")
    except Exception as e:
        return f"Error calling LLM API: {str(e)}"
