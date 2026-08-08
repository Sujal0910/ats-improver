# src/engine/ranker.py

import re
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from src.engine.knowledge_graph import SkillKnowledgeGraph

# Load Models
print("Loading Cross-Encoder model...")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
kg = SkillKnowledgeGraph()

def tokenize(text: str) -> list[str]:
    """Tokenize and normalize text for BM25 keyword matching."""
    return re.findall(r'\w+', text.lower())

def min_max_normalize(scores: list[float]) -> list[float]:
    """Normalize score values to a 0.0 - 1.0 range."""
    min_s, max_s = min(scores), max(scores)
    if max_s == min_s:
        return [1.0 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]

def expand_job_description(jd_text: str) -> str:
    """
    Scans the Job Description for known skills in the Knowledge Graph.
    If found, appends all synonyms and child-skills to the JD context.
    """
    expanded_terms = set()
    jd_lower = jd_text.lower()
    
    # Check if any node in our Knowledge Graph exists in the JD
    for node in kg.graph.nodes:
        # Use word boundaries to avoid partial matches (e.g., 'C' matching inside 'Cloud')
        pattern = r'\b' + re.escape(str(node).lower()) + r'\b'
        if re.search(pattern, jd_lower):
            # Fetch synonyms and related child concepts
            expanded_terms.update(kg.get_expanded_skills(node))
            
    if expanded_terms:
        # Append invisibly to the search query
        enriched_context = "\nExpanded ATS Context: " + ", ".join(expanded_terms)
        return jd_text + enriched_context
    
    return jd_text

def rank_bullets(
    job_description: str, 
    bullet_points: list[dict], 
    bm25_weight: float = 0.3, 
    ce_weight: float = 0.7
) -> list[dict]:
    """
    Ranks master resume bullet points against an EXPANDED Job Description 
    using a Hybrid BM25 + Cross-Encoder architecture.
    """
    bullets_text = [b["text"] for b in bullet_points]
    
    # --- STAGE 0: Knowledge Graph Expansion ---
    enriched_jd = expand_job_description(job_description)
    
    # --- STAGE 1: Lexical Search (BM25) ---
    tokenized_corpus = [tokenize(t) for t in bullets_text]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_jd = tokenize(enriched_jd)
    raw_bm25_scores = bm25.get_scores(tokenized_jd)
    norm_bm25_scores = min_max_normalize(raw_bm25_scores)
    
    # --- STAGE 2: Deep Semantic Re-Ranking (Cross-Encoder) ---
    # We pass the enriched JD to the Cross-Encoder so it understands synonym context
    pairs = [[enriched_jd, b_text] for b_text in bullets_text]
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
    
    ranked_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return ranked_results

if __name__ == "__main__":
    from src.engine.mock_data import MASTER_BULLET_POINTS
    
    # Notice this JD only asks for "Cloud Computing" and "Backend Development"
    # It does NOT explicitly say AWS, Docker, Python, or FastAPI.
    TRICKY_JOB_DESCRIPTION = """
    We are looking for a software engineer with strong Cloud Computing experience.
    You will be responsible for Backend Development and managing our infrastructure.
    """
    
    print("\n--- Running Integrated Graph + Ranker Test ---\n")
    
    # 1. Show the expansion working
    enriched_jd = expand_job_description(TRICKY_JOB_DESCRIPTION)
    print("=== KNOWLEDGE GRAPH EXPANSION ===")
    print("Original JD:", TRICKY_JOB_DESCRIPTION.strip())
    print("\nEnriched JD sent to AI:\n", enriched_jd.strip())
    print("-" * 80)
    
    # 2. Run the ranker
    results = rank_bullets(TRICKY_JOB_DESCRIPTION, MASTER_BULLET_POINTS)
    
    print("\n=== RANKING RESULTS ===")
    print(f"{'Rank':<5} | {'ID':<3} | {'Score':<6} | {'Bullet Point Text'}")
    print("-" * 110)
    for rank, item in enumerate(results[:5], start=1):
        print(f"{rank:<5} | {item['id']:<3} | {item['hybrid_score']:<6.1f} | {item['text'][:85]}...")