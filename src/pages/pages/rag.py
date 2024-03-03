from src.Welcome import get_intent_store
from src.app.embedder import get_embedder
from src.const import DEFAULT_QUERY
from src.store.chunk import ChunkIntent
from sentence_transformers import util

import streamlit as st


def rag_page():
    intent_store, rag, embedder = get_intent_store(), get_rag(), get_embedder()
    st.title("‍🚀️️ kolobot")
    st.subheader("🔮 Query:\n")
    query = st.text_input("Query", value=DEFAULT_QUERY)
    submitted = st.button("🎱 Answer")
    if submitted or query:
        st.subheader("📎 Generated:")
        with st.spinner("Getting answer..."):
            intents, result_intent = [], f"{query}\n\n"
            for classify_result in intent_store.classify(query)[0][:5]:
                intent: ChunkIntent = intent_store.get_intent(str(classify_result))
                if intent:
                    intents.append(intent)
            query_embedding = embedder.embed([f'{query}'])
            chunks = [
                intent.description_chunks[
                    util.cos_sim(
                        query_embedding, intent.description_chunk_embeddings
                    ).detach().to("cpu").numpy().argmax()
                ]
                for intent in intents
            ]
            main_text = rag.generate_main(chunks, query)
            result_intent += main_text
            st.success(result_intent)
