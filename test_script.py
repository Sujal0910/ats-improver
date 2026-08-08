import docx
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

print("1. Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

print("2. Loading Sentence Transformer model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

print("\n✅ All core libraries initialized successfully! You are ready for Step 1.")