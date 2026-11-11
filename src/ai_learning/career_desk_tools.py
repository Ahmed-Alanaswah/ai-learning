from openai import (
    OpenAI,
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    APIStatusError,
)
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv(Path(__file__).resolve().parents[2] / ".env")
client = OpenAI(
    timeout=15.0,
    max_retries=1,
)


def call_ai(**kwargs):
    try:
        return client.responses.create(**kwargs)

    except APITimeoutError:
        print("AI request timed out.")

    except APIConnectionError:
        print("Cannot connect to AI provider.")

    except RateLimitError:
        print("Rate limit reached. Try again later.")

    except APIStatusError as error:
        print(f"AI API error: {error.status_code}")

    raise SystemExit(1)


# Mock database
JOBS = [
    {
        "id": 1,
        "title": "React Developer",
        "skills": ["React", "TypeScript"],
        "remote": True,
        "countries": ["JO", "AE"],
    },
    {
        "id": 2,
        "title": "Frontend Engineer",
        "skills": ["React", "JavaScript"],
        "remote": False,
        "countries": ["JO"],
    },
]
COUNTRY_ALIASES = {
    "الأردن": "JO",
    "الاردن": "JO",
    "jordan": "JO",
    "jo": "JO",
    "الإمارات": "AE",
    "الامارات": "AE",
    "uae": "AE",
    "united arab emirates": "AE",
    "ae": "AE",
}


def normalize_country(value: str) -> str:
    normalized = value.strip().casefold()
    country_code = COUNTRY_ALIASES.get(normalized)

    if country_code is None:
        raise ValueError(f"Unsupported country: {value}")

    return country_code

class SearchArgs(BaseModel):
    skills: list[str]
    remote_only: bool
    eligible_from_country: str


def search_jobs(args: SearchArgs):
    country_code = normalize_country(
        args.eligible_from_country
    )

    return [
        job for job in JOBS
        if all(
            skill.casefold() in [
                s.casefold() for s in job["skills"]
            ]
            for skill in args.skills
        )
        and (not args.remote_only or job["remote"])
        and country_code in job["countries"]
    ]

tools = [
    {
        "type": "function",
        "name": "search_jobs",
        "description": "Search stored mock job listings.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "remote_only": {"type": "boolean"},
                "eligible_from_country": {"type": "string"},
            },
            "required": [
                "skills",
                "remote_only",
                "eligible_from_country",
            ],
            "additionalProperties": False,
        },
    }
]


model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

messages = [
    {
        "role": "user",
        "content": (
            "ابحث عن وظائف React ريموت "
            "تقبل المتقدمين من الأردن."
        ),
    }
]

response = call_ai(
    model=model,
    instructions=(
        "Use search_jobs for job searches. "
        "The tool contains mock data, not live jobs."
    ),
    input=messages,
    tools=tools,
    tool_choice="required",
    parallel_tool_calls=False,
)

messages.extend(response.output)

for item in response.output:
    if item.type != "function_call":
        continue

    if item.name != "search_jobs":
        raise ValueError("Unknown tool")

    args = SearchArgs.model_validate_json(item.arguments)
    result = search_jobs(args)

    print("Tool arguments:", args.model_dump())
    print("Tool result:", result)

    messages.append({
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result),
    })


final_response = call_ai(
    model=model,
    instructions=(
        "Answer in Arabic using only the tool results. "
        "Clarify that these are mock jobs."
    ),
    input=messages,
    tool_choice="none",
)

print("\nAI answer:")
print(final_response.output_text)