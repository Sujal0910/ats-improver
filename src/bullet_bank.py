BULLET_BANK = [
    {
        "keywords": ["docker", "kubernetes", "uptime"],
        "text": "Architected and deployed containerized microservices using Docker and Kubernetes, reducing deployment time by 45% and ensuring 99.9% system uptime."
    },
    {
        "keywords": ["ci/cd", "github actions", "pipelines"],
        "text": "Automated build and release cycles by implementing robust CI/CD pipelines via GitHub Actions, cutting release failure rates by 30%."
    },
    {
        "keywords": ["aws", "terraform", "infrastructure"],
        "text": "Spearheaded cloud infrastructure migration to AWS using Terraform for Infrastructure as Code, decreasing monthly hosting costs by 25%."
    },
    {
        "keywords": ["aws lambda", "dynamodb", "serverless"],
        "text": "Optimized scalable serverless architectures using AWS Lambda and DynamoDB, boosting data processing throughput twofold."
    },
    {
        "keywords": ["react", "typescript", "redux"],
        "text": "Engineered high-performance frontend web applications utilizing React, TypeScript, and Redux, improving page load speeds by 40%."
    },
    {
        "keywords": ["ui", "components", "legacy"],
        "text": "Refactored legacy monolithic UI codebases into modular component libraries, enhancing developer velocity and cutting bug reports by 35%."
    },
    {
        "keywords": ["node.js", "graphql", "backend"],
        "text": "Developed scalable backend microservices with Node.js and GraphQL, reducing API response latency by 50% for 1M+ active users."
    },
    {
        "keywords": ["postgresql", "database", "sql"],
        "text": "Designed complex relational database schemas and optimized indexing in PostgreSQL, accelerating query execution times by 3x."
    },
    {
        "keywords": ["python", "airflow", "data"],
        "text": "Built automated data ingestion pipelines using Python and Apache Airflow, processing over 50GB of streaming data daily with zero downtime."
    },
    {
        "keywords": ["machine learning", "ml", "models"],
        "text": "Integrated machine learning prediction models into production applications, increasing user conversion rates by 18%."
    },
    {
        "keywords": ["rest apis", "microservices", "api"],
        "text": "Designed and implemented fault-tolerant REST APIs and distributed microservices architecture, scaling user request capacity to 10k RPS."
    },
    {
        "keywords": ["redis", "caching", "latency"],
        "text": "Integrated Redis caching layers to alleviate database strain, reducing average server response latency by 60%."
    },
    {
        "keywords": ["agile", "scrum", "saas"],
        "text": "Led cross-functional Agile/Scrum engineering teams to deliver mission-critical SaaS features 2 weeks ahead of scheduled deadlines."
    },
    {
        "keywords": ["jest", "cypress", "testing", "coverage"],
        "text": "Established comprehensive automated testing suites using Jest and Cypress, elevating overall code coverage from 65% to 92%."
    },
    {
        "keywords": ["oauth", "jwt", "authentication", "security"],
        "text": "Implemented secure authentication and authorization protocols using OAuth 2.0 and JWT, eliminating security vulnerabilities across endpoints."
    },
    {
        "keywords": ["encryption", "compliance", "security standards"],
        "text": "Enforced end-to-end data encryption standards for sensitive user records, achieving full compliance with industry security frameworks."
    },
    {
        "keywords": ["prometheus", "grafana", "monitoring"],
        "text": "Deployed real-time application performance monitoring systems using Prometheus and Grafana, lowering mean time to resolution (MTTR) by 50%."
    },
    {
        "keywords": ["alerting", "outage"],
        "text": "Configured proactive alerting thresholds that reduced critical system outage notifications by 40%."
    },
    {
        "keywords": ["kafka", "event-driven", "messaging"],
        "text": "Architected a high-throughput event-driven messaging system using Apache Kafka, handling 5 million daily asynchronous transactions seamlessly."
    },
    {
        "keywords": ["pub/sub", "architecture", "scalability"],
        "text": "Decoupled tightly bound legacy backend services into a robust pub/sub architecture, increasing system scalability and fault tolerance."
    }
]

def get_matching_bullets(missing_keywords: list[str], max_bullets: int = 2) -> list[str]:
    """
    Finds and returns the best matching professional achievement bullets 
    based on overlap with the extracted missing keywords.
    """
    scored_bullets = []
    missing_set = {kw.lower() for kw in missing_keywords}

    for item in BULLET_BANK:
        score = 0
        for kw in item["keywords"]:
            if any(kw in m or m in kw for m in missing_set):
                score += 2
        for m in missing_set:
            if m in item["text"].lower():
                score += 1

        if score > 0:
            scored_bullets.append((score, item["text"]))

    scored_bullets.sort(key=lambda x: x[0], reverse=True)
    selected = [b[1] for b in scored_bullets[:max_bullets]]
    
    # Fallback if no specific keyword match is found
    if not selected and BULLET_BANK:
        selected = [BULLET_BANK[0]["text"]]

    return selected