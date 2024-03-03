from functools import lru_cache
from typing import List, Dict

from openai import OpenAI
from pydantic_settings import BaseSettings

from src.app.ner import get_ner
from src.const import HEADER


class DialogSettings(BaseSettings):
    openai_model: str = "gpt-3.5-turbo"
    api_key: str = "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"
    states: List = ['greet', 'ask']
    state_prompt_mapping: Dict = {
        'greet': f"Say hello",
        'ask': f"Ask what if interested and ask for a meeting time\n",
        'bye': f"Say that you saved meeting time and say bye\n",
    }

    class Config:
        env_prefix = 'DIALOG_'


class Dialog:
    def __init__(self):
        self.settings = DialogSettings()
        self.states = self.settings.states
        self.state_prompt_mapping = self.settings.state_prompt_mapping
        self.set_states()
        self.ner = get_ner()
        self.client = OpenAI(api_key=self.settings.api_key)
        self.prompt = None

    def set_states(self):
        self.state_prompt_mapping.update(
            {
                'extracted':    f"Answer short, "
                                f"in 1 sentence, "
                                f"say thanks "
                                f"and say that appointment is scheduled for the time provided: ",
                'fallback': f"{HEADER}",
            }
        )
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
            "content": f"{HEADER}" +
                       f"\nMessage: \n{message}\n" +
                       f"\nContext: \n{self.state_prompt_mapping[current_state]}\n"
        }
        return self


@lru_cache(maxsize=1)
def get_dialog():
    return Dialog()
