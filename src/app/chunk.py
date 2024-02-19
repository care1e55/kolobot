from functools import lru_cache
from typing import List

from src.app.rag import RAG, RAGSettings
from src.const import MAIN_CONTENT_TEMPLATE, REWRITE_TEMPLATE


class ChunkRAG(RAG):

    def generate_main(self, chunks: List[str], query: str):
        answers = [self.get_answer(query, chunk[:5000]) for chunk in chunks]
        main_text = self.retemplate(REWRITE_TEMPLATE).get_answer(str("\n".join(answers))[:5000], "")
        return f"""\n\n{main_text}"""


@lru_cache(maxsize=1)
def get_rag():
    return ChunkRAG(RAGSettings(), MAIN_CONTENT_TEMPLATE)
