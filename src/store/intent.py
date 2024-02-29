import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict

import chromadb
import numpy as np
from chromadb.utils import embedding_functions
from chromadb.api.types import QueryResult
from chromadb.config import Settings

from pydantic_settings import BaseSettings


class IntentStoreSettings(BaseSettings):
    data: str
    model: str = 'sentence-transformers/all-mpnet-base-v2'

    class Config:
        env_prefix = 'INTENT_STORE_'


@dataclass
class Intent:
    intent_id: str
    intent_name: str
    texts: List[str]
    index_ids: List[str]
    description: str
    threshold: float

    def __init__(
            self,
            intent_name: str = "",
            texts: List[str] = [],
            description: str = "",
            thresh: float = 1.0
    ):
        self.intent_id = uuid.uuid4().__str__()
        self.intent_name = intent_name
        self.description = description
        self.texts = texts
        self.index_ids = [
            f'0_{uuid.uuid4().__str__()}',
            f'1_{uuid.uuid4().__str__()}',
        ]
        self.index_ids += [
            f'{uuid.uuid4().__str__()}' for _ in texts
        ]
        self.threshold = thresh if thresh < 1.0 else 1.0

    @property
    def dict(self):
        return asdict(self)

    def __str__(self):
        return self.dict.__str__()

    def __len__(self):
        return len(self.index_ids)


class IntentStore:
    def __init__(self):
        self.settings = IntentStoreSettings()
        self.intents: Dict[str: Intent] = {}
        self.intents_names: Dict[str: Intent] = {}
        self._chroma_client = chromadb.HttpClient('chroma', '8000', settings=Settings(allow_reset=True, anonymized_telemetry=False))
        self._chroma_collection = self._chroma_client.get_or_create_collection(
            name='intent_store',
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.settings.model
            ),
            metadata={"hnsw:space": 'cosine'}
        )

    def add_intent(self, intent: Intent):
        self._chroma_collection.add(
            ids=intent.index_ids,
            documents=[intent.intent_name] + [intent.description] + intent.texts,
            metadatas=[
                {
                    "index_id": index_id,
                    "intent_id": intent.intent_id,
                    "intent_name": intent.intent_name
                } for index_id in intent.index_ids]
        )
        self.intents[intent.intent_id] = intent
        self.intents_names[intent.intent_name] = intent
        return self

    def replace_intent(self, intent_intent_id: str, intent: Intent):
        self.intents[intent_intent_id] = intent
        return self

    def get_intent(self, intent: str) -> Intent:
        return self.intents.get(intent) if self.intents.get(intent) else self.intents_names.get(intent)

    def query(self, text: str, k: int = 10) -> QueryResult:
        result: QueryResult = self._chroma_collection.query(
            query_texts=[text],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        return result

    def classify(self, text: str):
        result: QueryResult = self.query(text)
        if result["distances"]:
            distances = np.asarray(result["distances"][0])
            intent_ids = [i["intent_id"] for i in result["metadatas"][0]]
            if distances:
                distances = distances / distances.max()
        return intent_ids, distances

    def describe(self, embeddings=False):
        if not embeddings:
            return self._chroma_collection.get()
        return self._chroma_collection.get(include=["documents", "metadatas", "embeddings"])

    def delete_intent(self, index_name: str):
        del self.intents[index_name]
        return self
