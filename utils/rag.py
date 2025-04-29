import pdfplumber
import os
import re

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        return ""

    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def split_into_sentences(text):
    # Lightweight custom sentence splitter based on punctuation
    text = text.replace('\n', ' ')
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences

def retrieve_relevant_passage(question, filepath):
    full_text = extract_text_from_pdf(filepath)
    if not full_text.strip():
        return ""

    sentences = split_into_sentences(full_text)
    keywords = [kw.strip().lower() for kw in question.lower().split() if len(kw) > 3]

    relevant_sentences = []
    for sent in sentences:
        sent_lower = sent.lower()
        if any(kw in sent_lower for kw in keywords):
            relevant_sentences.append(sent)

    return " ".join(relevant_sentences) if relevant_sentences else full_text
