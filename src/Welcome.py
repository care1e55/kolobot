from pathlib import Path

import streamlit as st

from src.const import DOWNLOADS_PATH
from src.store.chunk import ChunkIntent
from src.store.intent import IntentStore


_logo, _name = "🕹", "Admin Tools for Automation"


INFO = f"""
*ATA* is a admin panel and tools for automation


- 🚀️️ *Kolbot** is your copilot assistant \n
- 🔮 **Index** is an intent manager admin \n
"""


@st.cache_resource
def get_intent_store():
    store = IntentStore()
    for lectures_path in DOWNLOADS_PATH.glob("*"):
        with open(lectures_path) as lecture_file:
            lecture_txt = lecture_file.read()
            _intent = ChunkIntent(
                intent_name=lectures_path.name,
                texts=[lectures_path.name],
                description=lecture_txt
            )
            store.add_intent(_intent)
    return store


if __name__ == '__main__':
    st.set_page_config(
        page_title=_name,
        page_icon=_logo,
    )
    st.title(f"{_logo} {_name}")
    st.markdown(INFO)
    with st.spinner("Booting tools..."):
        intent_store = get_intent_store()
    st.success("Select tool from the left menu")
