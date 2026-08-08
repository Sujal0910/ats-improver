from src.matcher import get_missing_keywords

# Simulated JD keywords (what the employer wants)
jd_keywords = [
    ("machine learning", 0.35),
    ("aws", 0.25),
    ("docker", 0.20),
    ("rest apis", 0.15)
]

# Candidate has "deep learning" (semantic match to ML), 
# "amazon web services" (exact/semantic match to AWS), 
# but NO docker or APIs.
sample_resume_text = """
Experienced software engineer specializing in deep learning and neural networks.
Deployed multiple cloud architectures using Amazon Web Services.
"""

print("--- Running Semantic ATS Matcher ---")
missing = get_missing_keywords(jd_keywords, sample_resume_text)

print(f"Job Description required: {[k[0] for k in jd_keywords]}")
print(f"Keywords identified as strictly missing: {missing}")