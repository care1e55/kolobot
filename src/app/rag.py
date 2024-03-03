import enum
from functools import lru_cache

from pydantic_settings import BaseSettings

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from src.const import MAIN_CONTENT_TEMPLATE, REWRITE_TEMPLATE


class RAGSettings(BaseSettings):
    prompt_model_name: str = "gpt-3.5-turbo-instruct"
    embedding_model_name: str = "text-embedding-ada-002"

    class Config:
        env_prefix = 'RAG_'


class RAG:
    class Params(enum.Enum):
        query: str = "query"
        docs: str = "docs"

    def __init__(self, settings: RAGSettings, template: str):
        self.settings, self.template = settings, template
        self.llm = OpenAI(model_name=self.settings.prompt_model_name, max_tokens=1024)

    def retemplate(self, template):
        self.template = template
        return self

    def get_answer(self, query, context: str) -> str:
        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=[
                    self.Params.query.value,
                    self.Params.docs.value
                ],
                template=self.template
            )
        ).run(query=query, docs=context)


@lru_cache(maxsize=1)
def get_rag():
    return RAG(RAGSettings(), MAIN_CONTENT_TEMPLATE)




class ChunkRAG(RAG):

    def generate_main(self, chunks: List[str], query: str):
        answers = [self.get_answer(query, chunk[:5000]) for chunk in chunks]
        main_text = self.retemplate(REWRITE_TEMPLATE).get_answer(str("\n".join(answers))[:5000], "")
        return f"""\n\n{main_text}"""


@lru_cache(maxsize=1)
def get_chunk_rag():
    return ChunkRAG(RAGSettings(), MAIN_CONTENT_TEMPLATE)
