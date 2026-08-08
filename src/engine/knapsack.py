# src/engine/knapsack.py

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def optimize_bullet_selection(
    ranked_bullets: list[dict],
    max_characters: int = 1400,
    min_bullets: int = 3,
    max_bullets: int = 6
) -> dict:
    """
    Selects the optimal subset of ranked bullet points using 0/1 Integer Linear Programming (Knapsack).
    Maximizes total relevance score while strictly adhering to character and bullet count constraints.
    """
    n = len(ranked_bullets)
    if n == 0:
        return {"selected_bullets": [], "total_chars": 0, "total_score": 0}

    # 1. Extract values (scores) and weights (character length)
    scores = np.array([b["hybrid_score"] for b in ranked_bullets])
    lengths = np.array([len(b["text"]) for b in ranked_bullets])

    # 2. Objective function: scipy.optimize.milp MINIMIZES by default.
    # To MAXIMIZE scores, we multiply the objective vector by -1.
    c = -scores

    # 3. Define Linear Constraints:
    # Constraint A: sum(lengths * x_i) <= max_characters
    # Constraint B: min_bullets <= sum(x_i) <= max_bullets
    
    A = np.vstack([
        lengths,              # Row 1: Character constraint
        np.ones(n)            # Row 2: Bullet count constraint
    ])

    # Lower and upper bounds for constraints
    # Row 1 bounds: [0, max_characters]
    # Row 2 bounds: [min_bullets, min(max_bullets, n)]
    actual_max_bullets = min(max_bullets, n)
    actual_min_bullets = min(min_bullets, n)

    constraints = LinearConstraint(
        A, 
        lb=[0, actual_min_bullets], 
        ub=[max_characters, actual_max_bullets]
    )

    # 4. Variable bounds: x_i must be 0 or 1 (Binary Integer constraint)
    integrality = np.ones(n)  # All variables are integers (binary)
    bounds = Bounds(lb=0, ub=1)

    # 5. Solve the Integer Linear Program
    res = milp(c=c, integrality=integrality, constraints=constraints, bounds=bounds)

    if not res.success:
        print("Warning: Knapsack solver could not find optimal fit. Falling back to top-N selection.")
        # Fallback: take top bullets until max_characters is reached
        selected = []
        curr_chars = 0
        for b in ranked_bullets:
            if curr_chars + len(b["text"]) <= max_characters and len(selected) < max_bullets:
                selected.append(b)
                curr_chars += len(b["text"])
        return {
            "selected_bullets": selected,
            "total_chars": curr_chars,
            "total_score": sum(b["hybrid_score"] for b in selected)
        }

    # 6. Extract selected indices (where solution x_i == 1)
    selected_indices = np.where(np.round(res.x) == 1)[0]
    selected_bullets = [ranked_bullets[i] for i in selected_indices]
    
    # Sort selected bullets by their original rank
    selected_bullets.sort(key=lambda x: x["hybrid_score"], reverse=True)

    total_chars = sum(len(b["text"]) for b in selected_bullets)
    total_score = sum(b["hybrid_score"] for b in selected_bullets)

    return {
        "selected_bullets": selected_bullets,
        "total_chars": total_chars,
        "total_score": round(total_score, 2),
        "capacity_used_pct": round((total_chars / max_characters) * 100, 1)
    }

if __name__ == "__main__":
    from src.engine.mock_data import TARGET_JOB_DESCRIPTION, MASTER_BULLET_POINTS
    from src.engine.ranker import rank_bullets

    print("\n--- Running Milestone 2: Knapsack Optimization Test ---\n")
    
    # Step A: Rank all 15 master bullets
    print("1. Ranking 15 Master Bullet Points...")
    ranked = rank_bullets(TARGET_JOB_DESCRIPTION, MASTER_BULLET_POINTS)

    # Step B: Pass ranked bullets into Knapsack optimizer with a strict 450-character budget
    MAX_CHAR_BUDGET = 450
    print(f"2. Optimizing fit for strict budget of {MAX_CHAR_BUDGET} characters (approx. 4-5 key bullets)...\n")
    
    opt_result = optimize_bullet_selection(
        ranked_bullets=ranked, 
        max_characters=MAX_CHAR_BUDGET, 
        min_bullets=2, 
        max_bullets=5
    )

    print("=== OPTIMIZATION RESULT ===")
    print(f"Bullets Selected : {len(opt_result['selected_bullets'])}")
    print(f"Total Score      : {opt_result['total_score']} pts")
    print(f"Character Budget : {opt_result['total_chars']} / {MAX_CHAR_BUDGET} chars ({opt_result['capacity_used_pct']}% capacity used)")
    print("-" * 80)
    
    for rank, b in enumerate(opt_result['selected_bullets'], start=1):
        print(f"[{rank}] Score: {b['hybrid_score']:<4} | Chars: {len(b['text']):<3} | {b['text']}")