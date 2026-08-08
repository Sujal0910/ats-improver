import spacy
from sentence_transformers import SentenceTransformer, util

# Load spaCy for phrase extraction and SentenceTransformer for semantic matching
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def get_resume_phrases(resume_text: str) -> list[str]:
    """Extracts nouns and noun phrases from the resume for comparison."""
    doc = nlp(resume_text)
    phrases = set()
    
    # Extract noun chunks
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3 and not chunk.root.is_stop:
            phrases.add(chunk.text.lower().strip())
            
    # Extract standalone nouns
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2:
            phrases.add(token.text.lower().strip())
            
    return list(phrases)


def get_missing_keywords(
    jd_keywords: list[tuple[str, float]], 
    resume_text: str, 
    similarity_threshold: float = 0.65
) -> list[str]:
    """
    Identifies missing keywords, ensures no semantic duplication, 
    and filters out terms already present.
    """
    resume_text_lower = resume_text.lower()
    raw_missing = []
    
    resume_phrases = get_resume_phrases(resume_text)
    
    if resume_phrases:
        resume_embeddings = embedder.encode(resume_phrases, convert_to_tensor=True)
    else:
        resume_embeddings = None

    for term, _ in jd_keywords:
        # 1. Fast Pass: Exact String Match
        if term in resume_text_lower:
            continue
            
        # 2. Deep Pass: Semantic Similarity
        is_semantically_present = False
        
        if resume_embeddings is not None:
            term_embedding = embedder.encode(term, convert_to_tensor=True)
            cosine_scores = util.cos_sim(term_embedding, resume_embeddings)[0]
            best_score = cosine_scores.max().item()
            
            if best_score >= similarity_threshold:
                is_semantically_present = True
                
        if not is_semantically_present:
            raw_missing.append(term)
            
    # 3. Clean & Deduplicate: Remove words that are completely contained within longer phrases
    # (e.g., if "restful apis" is missing, drop standalone "apis" if "apis" is already being injected or present)
    deduplicated = []
    for term in sorted(raw_missing, key=len, reverse=True): # Process longer phrases first
        # Check if this term is a subset of an already accepted missing keyword
        is_redundant = any(term in existing and term != existing for existing in deduplicated)
        if not is_redundant and term not in deduplicated:
            deduplicated.append(term)
            
    return deduplicated