# src/engine/mock_data.py

TARGET_JOB_DESCRIPTION = """
We are seeking a Senior Backend & DevOps Engineer to build scalable microservices using Python, FastAPI, and PostgreSQL. 
Key Responsibilities:
- Design and deploy containerized applications using Docker and Kubernetes on AWS.
- Build robust REST APIs with high throughput and low latency using Python and FastAPI.
- Optimize complex database queries and manage PostgreSQL schemas.
- Set up CI/CD pipelines using GitHub Actions for automated testing and deployment.
- Implement monitoring and logging using Prometheus and Grafana.
"""

MASTER_BULLET_POINTS = [
    # Category: Backend / Python / Databases
    {"id": 1, "text": "Architected and deployed high-throughput REST APIs using Python, FastAPI, and Pydantic, reducing response latency by 35%."},
    {"id": 2, "text": "Optimized complex PostgreSQL queries and redesigned database schemas, improving query execution time by 50% on 10M+ records."},
    {"id": 3, "text": "Built asynchronous background task processing workflows using Celery, Redis, and Python for distributed data processing."},
    
    # Category: DevOps / Cloud / Infrastructure
    {"id": 4, "text": "Containerized 12+ backend microservices using Docker and orchestrated deployments on AWS EKS (Kubernetes)."},
    {"id": 5, "text": "Configured automated CI/CD pipelines via GitHub Actions, decreasing deployment build times from 25 minutes to 6 minutes."},
    {"id": 6, "text": "Implemented real-time monitoring and alerting systems using Prometheus and Grafana, achieving 99.9% service uptime."},
    {"id": 7, "text": "Managed cloud infrastructure using Terraform (Infrastructure as Code) on AWS, reducing cloud spending by 20%."},
    
    # Category: Frontend (Irrelevant to this target JD)
    {"id": 8, "text": "Developed responsive, accessible user interfaces using React, TypeScript, and Tailwind CSS for 50k+ monthly active users."},
    {"id": 9, "text": "Migrated legacy Redux state management to React Query, improving client-side page load speed by 40%."},
    {"id": 10, "text": "Created interactive data visualization dashboards using D3.js and Recharts."},
    
    # Category: Data Science / Machine Learning (Irrelevant to this target JD)
    {"id": 11, "text": "Trained predictive Machine Learning models using Scikit-Learn and PyTorch to forecast customer churn with 88% accuracy."},
    {"id": 12, "text": "Built ETL data pipelines using PySpark and Apache Airflow to process 500GB+ of daily log data into Snowflake."},
    
    # Category: Leadership / Process
    {"id": 13, "text": "Led a cross-functional team of 5 engineers in an Agile/Scrum environment, conducting daily standups and sprint planning."},
    {"id": 14, "text": "Mentored 3 junior developers through weekly code reviews and technical architecture workshops."},
    {"id": 15, "text": "Spearheaded technical documentation and security compliance audits for SOC-2 certification."}
]