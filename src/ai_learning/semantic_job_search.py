from pathlib import Path
from math import sqrt

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).resolve().parents[2] / ".env")
client = OpenAI()

JOBS = [
    {
        "title": "Frontend Engineer",
        "description": (
            "Build interactive admin dashboards and "
            "reusable components with React and TypeScript."
        ),
        "remote": True,
        "countries": ["JO"],
    },
    {
        "title": "Backend Engineer",
        "description": (
            "Develop APIs, database services and "
            "backend infrastructure with Python."
        ),
        "remote": True,
        "countries": ["JO"],
    },
    {
        "title": "React Developer - Onsite",
        "description": (
            "Build web applications with React "
            "and TypeScript in the office."
        ),
        "remote": False,
        "countries": ["JO"],
    },
]


def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = sqrt(sum(x * x for x in a))
    magnitude_b = sqrt(sum(y * y for y in b))

    return dot_product / (magnitude_a * magnitude_b)


query = "أريد وظيفة تطوير واجهات ولوحات تحكم باستخدام React"

# Step 1: Apply hard filters
eligible_jobs = [
    job for job in JOBS
    if job["remote"] and "JO" in job["countries"]
]

# Step 2: Embed query and eligible job descriptions
texts = [query] + [
    job["description"] for job in eligible_jobs
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts,
)

vectors = [
    item.embedding
    for item in sorted(response.data, key=lambda item: item.index)
]

query_vector = vectors[0]
job_vectors = vectors[1:]

# Step 3: Calculate similarity scores
results = []

for job, vector in zip(eligible_jobs, job_vectors):
    score = cosine_similarity(query_vector, vector)
    results.append((job["title"], score))

# Step 4: Rank by semantic similarity
results.sort(key=lambda item: item[1], reverse=True)

for title, score in results:
    print(f"{title}: {score:.4f}")