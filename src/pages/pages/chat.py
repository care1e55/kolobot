import dataclasses
import streamlit as st

from src.app.chat import get_dialog


@dataclasses.dataclass
class Message:
    def __init__(self, role: str, message: str):
        self.role = role
        self.message = message
        self._response = None
        self.state = None


def render_messages():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_message(user, message):
    st.session_state.messages.append(
        {"role": user, "content": message}
    )
    with st.chat_message(user):
        st.markdown(st.session_state.messages[-1]["content"])


def response(dialog, message):
    dialog.state_prompt(message)
    with st.chat_message("assistant"):
        _response = st.write_stream(
            dialog.client.chat.completions.create(
                model=dialog.settings.openai_model,
                messages=[dialog.prompt],
                stream=True,
            )
        )
    st.session_state.messages.append(
        {"role": "assistant", "content": _response}
    )


def chat_page():
    st.title("👩‍🚀 Chat")
    dialog = get_dialog()
    render_messages()
    if message := st.chat_input("Message"):
        render_message("user", message)
        response(dialog, message)
