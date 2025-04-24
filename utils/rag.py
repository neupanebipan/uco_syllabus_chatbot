# utils/rag.py
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def extract_text_from_pdf(filepath):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

def retrieve_relevant_passage(question, filepath):
    full_text = extract_text_from_pdf(filepath)
    chunk_size = 1500
    overlap = 200
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size - overlap)]

    # Keyword boosting: prioritize chunks with exam-related keywords
    keywords = ["midterm", "exam", "test", "quiz", "schedule", "date"]
    scored_chunks = []
    for chunk in chunks:
        score = sum(1 for word in keywords if re.search(rf"\b{word}\b", chunk, re.IGNORECASE))
        scored_chunks.append((chunk, score))

    # Sort so chunks with higher keyword match are earlier
    sorted_chunks = [chunk for chunk, _ in sorted(scored_chunks, key=lambda x: -x[1])]
    documents = sorted_chunks + [question]

    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    similarities = cosine_similarity([vectors[-1]], vectors[:-1])[0]
    top_chunk = sorted_chunks[np.argmax(similarities)]
    return top_chunk