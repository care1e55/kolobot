from functools import lru_cache

from openai import OpenAI
import streamlit as st
from pydantic_settings import BaseSettings

from src.app.ner import get_ner
from src.const import HEADER


class DialogSettings(BaseSettings):
    openai_model: str = "gpt-3.5-turbo"
    api_key: str = "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"

    class Config:
        env_prefix = 'DIALOG_'


class Dialog:

    header_prompt = f"{HEADER}\n"

    def __init__(self):
        self.settings = DialogSettings()
        self.ner = get_ner()
        self.client = OpenAI(api_key=self.settings.api_key)
        self.prompt = None
        self.states = None
        self.state_prompt_mapping = None

    def set_states(self):
        self.states = ['greet', 'ask'][::-1]
        self.state_prompt_mapping = {
            'extracted':    f"Answer short, "
                            f"in 1 sentence, "
                            f"say thanks "
                            f"and say that appointment is scheduled for the time provided: ",
            'fallback': f"",
        }
        self.state_prompt_mapping.update(
            {
            'greet': f"Say hello",
            'ask': f"Ask what if interested and ask for a meeting time\n",
            'bye': f"Say that you saved meeting time and say bye\n",
            }
        )
        return self

    def render_messages(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        return self

    def render_message(self, user, message):
        st.session_state.messages.append(
            {"role": user, "content": message}
        )
        with st.chat_message(user):
            st.markdown(st.session_state.messages[-1]["content"])
        return self

    def state_prompt(self, message):
        extracted = self.ner.extract(message)
        if extracted:
            current_state = 'extracted'
            self.state_prompt_mapping[current_state] = self.state_prompt_mapping[current_state] + f"{extracted}\n"
        else:
            try:
                current_state = self.states.pop()
            except IndexError:
                current_state = 'fallback'
        self.prompt = {
            "role": "user",
            "content": f"{self.header_prompt}" +
                       f"\nMessage: \n{message}\n" +
                       f"\nContext: \n{self.state_prompt_mapping[current_state]}\n"
        }
        return self

    def response(self, message):
        self.render_message("user", message)
        self.state_prompt(message)
        with st.chat_message("assistant"):
            _response = st.write_stream(
                self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[self.prompt],
                    stream=True,
                )
            )
        st.session_state.messages.append(
            {"role": "assistant", "content": _response}
        )


@lru_cache(maxsize=1)
def get_dialog():
    return Dialog().set_states()
