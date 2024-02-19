import streamlit as st

from src.pages.pages.rag import get_intent_store
from src.store.intent import Intent


def intent_form():
    intent_store = get_intent_store()
    intent = st.session_state.get("intent", Intent())

    with st.form("Intent Form"):
        st.markdown(f"**Intent:** {intent.intent_id or ''}")
        intent_name = st.text_input('Name', intent.intent_name)
        text_examples = st.text_area('Examples', "\n".join(intent.texts))
        desc = st.text_area('Text', intent.description, height=256)
        col_1, col_2 = st.columns(2)
        with col_1:
            submitted = st.form_submit_button("Submit")
        if submitted:
            intent = Intent(
                intent_name,
                texts=[text for text in text_examples.split("\n")],
                description=desc
            )
            intent_store.add_intent(intent)
            st.session_state["intent"] = intent
            st.success(f'✅ Submitted intent [{intent.intent_name}]\n\nNew ID: {intent.intent_id}')


def dispatcher_page():
    intent_store = get_intent_store()
    st.subheader("🔮 Intent index")
    intent_names = set([metadata["intent_name"] for metadata in intent_store.describe()["metadatas"]])

    query = st.selectbox(
        'Select from intents',
        intent_names,
    )
    if query:
        intent = intent_store.get_intent(query)
        if not intent:
            intent = Intent()
        st.session_state["intent"] = intent
        intent_form()
