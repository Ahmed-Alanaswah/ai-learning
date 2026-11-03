import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI()


INSTRUCTIONS = {
    "معلّم برمجة": (
        "You are a programming teacher. "
        "Explain concepts step by step with examples. "
        "Prefer Arabic explanations."
    ),
    "مدرّب مقابلات": (
        "You are a technical interviewer. "
        "Ask focused interview questions. "
        "Give feedback on the user's answers."
    ),
}


def add_user_message(message, history):
    message = message.strip()

    if not message:
        return "", history

    updated_history = history + [
        {"role": "user", "content": message}
    ]

    return "", updated_history
def extract_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = [
            extract_text(item)
            for item in content
        ]
        return "\n".join(
            part for part in parts if part
        )

    if isinstance(content, dict):
        text = content.get("text", "")
        return text if isinstance(text, str) else ""

    return ""

def generate_response(history, mode):
    history = history or []
    messages = []

    for item in history:
        role = item.get("role")

        if role not in ("user", "assistant"):
            continue

        content = extract_text(item.get("content"))

        if content.strip():
            messages.append({
                "role": role,
                "content": content
            })

    # Debug: see what we are sending to OpenAI
    print("Prepared messages:", repr(messages))

    if not messages or messages[-1]["role"] != "user":
        raise gr.Error(
            "No valid user message found."
        )

    stream = client.responses.create(
        model="gpt-4.1-mini",
        instructions=INSTRUCTIONS[mode],
        input=messages,
        stream=True,
    )

    answer = ""

    for event in stream:
        if event.type == "response.output_text.delta":
            answer += event.delta

            yield history + [
                {
                    "role": "assistant",
                    "content": answer
                }
            ]

        elif event.type == "response.failed":
            raise gr.Error("Model response failed.")

        elif event.type == "error":
            raise gr.Error("Streaming failed.")

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## AI Programming Assistant")

    mode = gr.Dropdown(
        choices=list(INSTRUCTIONS.keys()),
        value="معلّم برمجة",
        label="وضع المساعد",
    )

    chatbot = gr.Chatbot(
        label="المحادثة",
        height=400,
        rtl=True,
    )

    message_input = gr.Textbox(
        label="رسالتك",
        placeholder="اكتب سؤالك هنا...",
    )

    clear = gr.ClearButton(
        [message_input, chatbot],
        value="مسح المحادثة",
    )

    submit_event = message_input.submit(
        fn=add_user_message,
        inputs=[message_input, chatbot],
        outputs=[message_input, chatbot],
        queue=False,
    )

    submit_event.then(
        fn=generate_response,
        inputs=[chatbot, mode],
        outputs=chatbot,
    )


if __name__ == "__main__":
    demo.launch(share=False, show_error=True)