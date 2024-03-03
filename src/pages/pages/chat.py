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


def chat_page():
    st.title("👩‍🚀 Chat")
    dialog = get_dialog().render_messages()
    if message := st.chat_input("Message"):
        dialog.response(message)
