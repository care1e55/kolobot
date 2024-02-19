import logging
from abc import ABC, abstractmethod
from functools import lru_cache

import numpy as np
import torch
from pydantic_settings import BaseSettings
from sentence_transformers import SentenceTransformer
from src.const import PRETRAINED_MODEL


logger = logging.getLogger(__name__)


class SentenceTransformerSettings(BaseSettings):
    embedding_dim: int = 768
    epochs: int = 5
    steps_per_epoch: int = 100
    warmup_steps: int = 10
    device: str = "cpu"

    class Config:
        env_prefix = "SENTENCE_TRANSFORMER_"


@lru_cache(maxsize=1)
def get_settings():
    return SentenceTransformerSettings()


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str):
        pass


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, pretrained_model):
        self.settings = get_settings()
        self.model = SentenceTransformer(pretrained_model, device=self.settings.device)

    def embed(self, texts: list[str]) -> np.ndarray:
        with torch.no_grad():
            return self.model.encode([str(text) for text in texts])


@lru_cache(maxsize=1)
def get_embedder():
    return SentenceTransformerEmbedder(PRETRAINED_MODEL)
