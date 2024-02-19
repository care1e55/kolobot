from dataclasses import dataclass
from functools import lru_cache
from typing import List

import numpy as np

from langchain.text_splitter import CharacterTextSplitter
from src.app.embedder import get_embedder
from src.store.intent import Intent


@lru_cache(maxsize=1)
def get_splitter():
    return CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=100)


@dataclass
class ChunkIntent(Intent):
    description_chunks: List[str]
    description_chunk_embeddings: np.ndarray

    splitter = get_splitter()
    embedder = get_embedder()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description_chunks = self.splitter.split_text(self.description)
        self.description_chunk_embeddings = self.embedder.embed(self.description_chunks)
