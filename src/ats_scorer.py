import re
from sentence_transformers import util

# FIX 1: Do NOT load the model again! Import the one already running in memory.
from src.matcher import embedder 

def calculate_impact_score(resume_text: str) -> float:
    """Scores the resume based on quantifiable metrics and structural sections."""
    score = 0.0
    text_lower = resume_text.lower()
    
    # 1. Section Completeness
    core_sections = ["experience", "education", "skills", "projects"]
    for section in core_sections:
        if section in text_lower:
            score += 2.5
            
    # 2. Measurable Impact 
    # Looks for digits, percentages, and dollar signs (e.g., "40%", "1M+", "$500k", "3x")
    metrics_found = len(re.findall(r'(\d+%|\$\d+|\d+x|\d+[km])', text_lower))
    score += min(10.0, metrics_found * 2.5) 
    
    return score

def calculate_local_ats_score(
    resume_text: str, 
    jd_text: str, 
    missing_keywords: list[str], 
    total_jd_keywords: int
) -> dict:
    """
    Calculates a highly accurate, entirely local ATS match score (0-100).
    Safely handles tensor limits and empty arrays.
    """
    try:
        if total_jd_keywords == 0:
            return {"score": 0, "feedback": "No technical keywords found in Job Description."}

        # --- 1. Keyword Score (45% of total) ---
        matched_keywords_count = max(0, total_jd_keywords - len(missing_keywords))
        keyword_score = (matched_keywords_count / total_jd_keywords) * 45.0

        # --- 2. Semantic Similarity Score (35% of total) ---
        # FIX 2: Slicing [:4000] prevents the AI model from crashing if a massive document is uploaded
        safe_resume_text = resume_text[:4000] if resume_text else "empty"
        safe_jd_text = jd_text[:4000] if jd_text else "empty"

        resume_emb = embedder.encode(safe_resume_text, convert_to_tensor=True)
        jd_emb = embedder.encode(safe_jd_text, convert_to_tensor=True)
        
        cosine_sim = util.cos_sim(resume_emb, jd_emb)[0][0].item()
        
        normalized_sim = max(0.0, min(1.0, (cosine_sim - 0.2) / 0.6))
        semantic_score = normalized_sim * 35.0

        # --- 3. Impact & Formatting Score (20% of total) ---
        impact_score = calculate_impact_score(resume_text)

        # --- Final Calculation ---
        final_score = int(round(keyword_score + semantic_score + impact_score))
        final_score = max(0, min(100, final_score)) # Clamp between 0 and 100
        
        # Generate dynamic feedback
        if final_score >= 80:
            feedback = "Excellent match! Your resume is highly optimized for this role."
        elif final_score >= 60:
            feedback = f"Good potential, but missing key technical requirements: {', '.join(missing_keywords[:3])}."
        else:
            feedback = "Low match. Your resume requires significant keyword and metric optimization."

        return {
            "score": final_score,
            "feedback": feedback
        }
        
    except Exception as e:
        print(f"ATS Scoring Engine Error: {e}")
        # Fail gracefully without breaking the rest of the application
        return {"score": 0, "feedback": "System was unable to calculate score."}