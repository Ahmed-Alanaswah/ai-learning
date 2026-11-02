from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    load_dotenv()

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="You are a senior software engineer.",
        input="Explain React state in two sentences."
    )

    print(response.output_text)


if __name__ == "__main__":
    main()