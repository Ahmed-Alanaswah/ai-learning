from collections.abc import Iterator
from dotenv import load_dotenv
from openai import OpenAI


def stream_answer(
    client: OpenAI,
    question: str
) -> Iterator[str]:

    stream = client.responses.create(
        model="gpt-4.1-mini",
        input=question,
        stream=True,
    )

    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta

        elif event.type == "response.failed":
            raise RuntimeError(
                "Model response failed"
            )

        elif event.type == "error":
            raise RuntimeError(
                "Streaming connection failed"
            )


def main() -> None:
    load_dotenv()
    client = OpenAI()

    try:
        for text in stream_answer(
            client,
            "Explain React useEffect briefly."
        ):
            print(text, end="", flush=True)

    except Exception as error:
        print("\nError:", error)


if __name__ == "__main__":
    main()