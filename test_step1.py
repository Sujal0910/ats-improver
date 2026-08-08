from src.extractor import extract_top_jd_keywords
from src.parser import parse_document

sample_jd = """
We are looking for a Senior Software Engineer with strong experience in Python,
FastAPI, and PostgreSQL. The ideal candidate will build scalable REST APIs, 
deploy applications using Docker and Kubernetes, and implement machine learning 
pipelines on AWS. Experience with git version control and CI/CD pipelines is required.
"""

print("--- Extracting Top Keywords from Sample Job Description ---")
keywords = extract_top_jd_keywords(sample_jd, top_n=10)

for rank, (term, score) in enumerate(keywords, 1):
    print(f"{rank}. {term:<25} (TF-IDF Score: {score})")