import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load("en_core_web_sm")

# Expanded Blacklist: Includes job seniority modifiers and generic software terms
# Expanded Blacklist: Includes seniority, general terms, AND technical adjectives/descriptors
JD_BLACKLIST = {
    "responsibilities", "responsibility", "requirements", "requirement",
    "qualifications", "qualification", "experience", "candidate", "role",
    "roles", "description", "opportunity", "company", "team", "work",
    "ability", "years", "job", "duties", "degree", "skills", "knowledge",
    "understanding", "ideal candidate", "minimum", "preferred", "overview",
    "summary", "position", "expectations", "benefits", "environment",
    "developer", "developers", "engineer", "engineers", "programmer", 
    "programmers", "designer", "designers", "manager", "managers", 
    "expert", "experts", "professional", "professionals", "member", "members",
    "client", "clients", "customer", "customers", "user", "users",
    "junior", "senior", "lead", "principal", "applications", "application",
    "system", "systems", "global", "enterprise", "solutions",
    # Added technical adjectives & architecture descriptors:
    "restful", "stack", "scalable", "fast", "secure", "custom", "modern", 
    "distributed", "concurrent", "robust", "dynamic", "static", "high"
}


def preprocess_text_for_keywords(text: str) -> str:
    doc = nlp(text)
    extracted_terms = []

    for chunk in doc.noun_chunks:
        clean_chunk = chunk.text.lower().strip()
        words = clean_chunk.split()
        
        # RULE: Reject the chunk if ANY word inside it is blacklisted
        if any(w in JD_BLACKLIST for w in words):
            continue
            
        if len(words) <= 3 and not chunk.root.is_stop:
            extracted_terms.append(clean_chunk)

    for token in doc:
        clean_token = token.text.lower().strip()
        if (
            token.pos_ in ["NOUN", "PROPN"]
            and not token.is_stop
            and len(clean_token) > 2
            and clean_token not in JD_BLACKLIST
        ):
            extracted_terms.append(clean_token)

    return " ".join(extracted_terms)


def extract_top_jd_keywords(jd_text: str, top_n: int = 15) -> list[tuple[str, float]]:
    processed_jd = preprocess_text_for_keywords(jd_text)

    if not processed_jd.strip():
        return []

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([processed_jd])

    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    keyword_scores = list(zip(feature_names, scores))
    sorted_keywords = sorted(keyword_scores, key=lambda x: x[1], reverse=True)

    unique_keywords = []
    seen = set()

    for term, score in sorted_keywords:
        term_clean = term.strip().lower()
        words = term_clean.split()
        
        # Double check blacklist on final extracted n-grams
        if any(w in JD_BLACKLIST for w in words):
            continue

        if term_clean not in seen and score > 0.0:
            seen.add(term_clean)
            unique_keywords.append((term_clean, round(float(score), 4)))
            if len(unique_keywords) == top_n:
                break

    return unique_keywords