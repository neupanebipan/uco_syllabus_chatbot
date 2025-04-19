
import os
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def extract_text_from_pdf(filepath):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def retrieve_relevant_passage(question, filepath):
    full_text = extract_text_from_pdf(filepath)
    chunks = [full_text[i:i+1000] for i in range(0, len(full_text), 1000)]
    documents = chunks + [question]
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    similarities = cosine_similarity([vectors[-1]], vectors[:-1])[0]
    top_chunk = chunks[np.argmax(similarities)]
    return top_chunk