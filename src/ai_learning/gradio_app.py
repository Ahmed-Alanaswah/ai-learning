import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI()


def to_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict)
            and part.get("type") == "text"
        )

    return ""


def chat(message, history):
    messages = []

    for item in history:
        role = item.get("role")

        if role not in ("user", "assistant"):
            continue

        content = to_text(item.get("content"))

        if content:
            messages.append({
                "role": role,
                "content": content
            })

    messages.append({
        "role": "user",
        "content": message
    })

    stream = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are a helpful AI programming tutor. "
            "Explain concepts clearly with examples."
        ),
        input=messages,
        stream=True,
    )

    answer = ""

    for event in stream:
        if event.type == "response.output_text.delta":
            answer += event.delta
            yield answer

        elif event.type == "response.failed":
            raise RuntimeError("Model response failed")

        elif event.type == "error":
            raise RuntimeError("Streaming failed")


demo = gr.ChatInterface(
    fn=chat,
    title="AI Programming Tutor",
    description="OpenAI + Gradio + Streaming",
    examples=[
        "Explain React rendering.",
        "What is a Python generator?",
    ],
)


if __name__ == "__main__":
    demo.launch(share=False)