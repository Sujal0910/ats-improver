# src/engine/orchestrator.py

from pathlib import Path
from src.engine.parser import parse_resume_to_structure
from src.engine.ranker import rank_bullets
from src.engine.knapsack import optimize_bullet_selection

def optimize_resume_file(
    file_path: str,
    job_description: str,
    max_character_budget: int = 1400,
    min_bullets: int = 3,
    max_bullets: int = 6
) -> dict:
    """
    Full Optimization Pipeline:
    1. Parses PDF/DOCX resume into structured JSON.
    2. Ranks all master bullets against target JD using Hybrid Cross-Encoder AI.
    3. Optimizes bullet selection to fit strict page character constraints.
    """
    # 1. Parse Document Structure
    parsed_profile = parse_resume_to_structure(file_path)
    extracted_bullets = parsed_profile["master_bullet_points"]

    if not extracted_bullets:
        return {
            "status": "error",
            "message": "No bullet points could be extracted from the provided document."
        }

    # 2. Rank Bullets against Target Job Description
    ranked_bullets = rank_bullets(
        job_description=job_description,
        bullet_points=extracted_bullets
    )

    # 3. Apply Knapsack Optimization for Page-Fit
    optimization_result = optimize_bullet_selection(
        ranked_bullets=ranked_bullets,
        max_characters=max_character_budget,
        min_bullets=min_bullets,
        max_bullets=max_bullets
    )

    # 4. Construct Final Payload
    return {
        "status": "success",
        "file_processed": parsed_profile["file_source"],
        "sections_detected": parsed_profile["sections_found"],
        "total_extracted_bullets": len(extracted_bullets),
        "selected_bullets_count": len(optimization_result["selected_bullets"]),
        "character_budget_used": f"{optimization_result['total_chars']} / {max_character_budget} ({optimization_result['capacity_used_pct']}%)",
        "overall_fit_score": optimization_result["total_score"],
        "optimized_bullets": optimization_result["selected_bullets"],
        "discarded_bullets": [
            b for b in ranked_bullets if b not in optimization_result["selected_bullets"]
        ]
    }

if __name__ == "__main__":
    import docx
    from src.engine.mock_data import TARGET_JOB_DESCRIPTION

    print("\n--- Running Milestone 4: End-to-End Orchestrator Test ---\n")

    # Generate a multi-bullet sample document
    sample_resume_content = """
    ALEX MORGAN
    alex@example.com | San Francisco, CA

    WORK EXPERIENCE
    - Architected and deployed high-throughput REST APIs using Python, FastAPI, and Pydantic, reducing response latency by 35%.
    - Optimized complex PostgreSQL queries and redesigned database schemas, improving query execution time by 50%.
    - Built asynchronous background task processing workflows using Celery, Redis, and Python.
    - Containerized 12+ backend microservices using Docker and orchestrated deployments on AWS EKS.
    - Configured automated CI/CD pipelines via GitHub Actions, decreasing deployment build times from 25 to 6 minutes.
    - Developed responsive, accessible user interfaces using React, TypeScript, and Tailwind CSS.
    - Migrated legacy Redux state management to React Query, improving client-side page load speed by 40%.
    - Trained predictive Machine Learning models using Scikit-Learn to forecast customer churn.

    TECHNICAL SKILLS
    Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS, Redis, React, TypeScript
    """

    test_file = Path("temp_orchestrator_test.docx")
    doc = docx.Document()
    for line in sample_resume_content.split("\n"):
        doc.add_paragraph(line)
    doc.save(test_file)

    try:
        # Run full optimization pipeline with a budget of 600 characters
        result = optimize_resume_file(
            file_path=str(test_file),
            job_description=TARGET_JOB_DESCRIPTION,
            max_character_budget=600,
            min_bullets=2,
            max_bullets=4
        )

        print("=== PIPELINE EXECUTION SUMMARY ===")
        print(f"Status           : {result['status']}")
        print(f"File Source      : {result['file_processed']}")
        print(f"Bullets Extracted: {result['total_extracted_bullets']}")
        print(f"Bullets Selected : {result['selected_bullets_count']}")
        print(f"Budget Capacity  : {result['character_budget_used']}")
        print(f"Overall Match    : {result['overall_fit_score']} pts\n")

        print("=== SELECTED BULLET POINTS (WINNERS) ===")
        for rank, b in enumerate(result['optimized_bullets'], start=1):
            print(f"[{rank}] Score: {b['hybrid_score']:<5} | Chars: {len(b['text']):<3} | {b['text']}")

        print("\n=== DISCARDED BULLET POINTS (IRRELEVANT/OVER BUDGET) ===")
        for b in result['discarded_bullets']:
            print(f"[-] Score: {b['hybrid_score']:<5} | Chars: {len(b['text']):<3} | {b['text']}")

    finally:
        if test_file.exists():
            test_file.unlink()