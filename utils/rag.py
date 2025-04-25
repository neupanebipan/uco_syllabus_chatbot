# utils/rag.py
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

            # Optional: extract tables as text
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    row_text = ' | '.join(cell for cell in row if cell)
                    text += row_text + "\n"
    return text

def split_into_sentences(text):
    # Enhanced splitter that includes table-style lines
    lines = text.split('\n')
    sentences = []
    for line in lines:
        if re.search(r'\w+', line) and len(line.strip()) > 10:
            sentences.append(line.strip())
    return sentences

def retrieve_relevant_passage(question, filepath):
    full_text = extract_text_from_pdf(filepath)

    # Use enhanced line-aware sentence splitter
    sentences = split_into_sentences(full_text)
    documents = sentences + [question]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(documents)
    vectors = vectorizer.toarray()

    similarities = cosine_similarity([vectors[-1]], vectors[:-1])[0]
    top_indices = np.argsort(similarities)[-5:][::-1]  # Top 5 most relevant sentences

    # Include a context window around each top sentence (before/after)
    top_matches = []
    for i in top_indices:
        if similarities[i] > 0.05:
            context_block = sentences[max(0, i-1):min(len(sentences), i+2)]
            top_matches.extend(context_block)

    return "\n\n".join(dict.fromkeys(top_matches))  # remove duplicates while preserving order
