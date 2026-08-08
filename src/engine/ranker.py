# src/engine/ranker.py

import re
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

# Load a lightweight Cross-Encoder model (runs fast locally on CPU)
print("Loading Cross-Encoder model...")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def tokenize(text: str) -> list[str]:
    """Tokenize and normalize text for BM25 keyword matching."""
    return re.findall(r'\w+', text.lower())

def min_max_normalize(scores: list[float]) -> list[float]:
    """Normalize score values to a 0.0 - 1.0 range."""
    min_s, max_s = min(scores), max(scores)
    if max_s == min_s:
        return [1.0 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]

def rank_bullets(
    job_description: str, 
    bullet_points: list[dict], 
    bm25_weight: float = 0.3, 
    ce_weight: float = 0.7
) -> list[dict]:
    """
    Ranks master resume bullet points against a Job Description 
    using a Hybrid BM25 + Cross-Encoder architecture.
    """
    bullets_text = [b["text"] for b in bullet_points]
    
    # --- STAGE 1: Lexical Search (BM25) ---
    tokenized_corpus = [tokenize(t) for t in bullets_text]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_jd = tokenize(job_description)
    raw_bm25_scores = bm25.get_scores(tokenized_jd)
    norm_bm25_scores = min_max_normalize(raw_bm25_scores)
    
    # --- STAGE 2: Deep Semantic Re-Ranking (Cross-Encoder) ---
    # Create input pairs: [Job Description, Bullet Point]
    pairs = [[job_description, b_text] for b_text in bullets_text]
    raw_ce_scores = cross_encoder.predict(pairs)
    norm_ce_scores = min_max_normalize(raw_ce_scores.tolist())
    
    # --- STAGE 3: Hybrid Score Fusion ---
    ranked_results = []
    for i, bullet in enumerate(bullet_points):
        final_score = (bm25_weight * norm_bm25_scores[i]) + (ce_weight * norm_ce_scores[i])
        ranked_results.append({
            "id": bullet["id"],
            "text": bullet["text"],
            "hybrid_score": round(final_score * 100, 2),
            "bm25_score": round(norm_bm25_scores[i] * 100, 2),
            "cross_encoder_score": round(norm_ce_scores[i] * 100, 2)
        })
    
    # Sort descending by hybrid score
    ranked_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return ranked_results

if __name__ == "__main__":
    from src.engine.mock_data import TARGET_JOB_DESCRIPTION, MASTER_BULLET_POINTS
    
    print("\n--- Running Hybrid Ranking Engine Test ---\n")
    results = rank_bullets(TARGET_JOB_DESCRIPTION, MASTER_BULLET_POINTS)
    
    print(f"{'Rank':<5} | {'ID':<3} | {'Score':<6} | {'Bullet Point Text'}")
    print("-" * 110)
    for rank, item in enumerate(results, start=1):
        print(f"{rank:<5} | {item['id']:<3} | {item['hybrid_score']:<6.1f} | {item['text'][:85]}...")