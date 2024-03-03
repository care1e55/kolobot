import abc
import enum
import re
from functools import lru_cache
from typing import Mapping, Callable, Optional


class Tag(enum.Enum):
    ALL = ['<NUMBER>', '<NAME>']
    NUMBER = '<NUMBER>'
    EMAIL = '<EMAIL>'
    NAME = '<NAME>'
    PLACE = '<PLACE>'
    TIME = '<TIME>'
    ORG = '<ORG>'
    OTHER = '<OTHER>'
    MISC = '<MISC>'
    IBAN = '<IBAN>'
    NER = '<NER>'
    UNK = '<UNK>'


class NER(abc.ABC):

    def __init__(
            self,
            tag: Tag,
            batch_size: int = 1
    ):
        self.tag = tag
        self.batch_size = batch_size
        self.tag_methods_mapping: Mapping[Tag: Callable] = {}

    def extract(self, text: str) -> Optional[str]:
        return self.tag_methods_mapping[self.tag](text)


class RegexpNER(NER):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from functools import partial
        self.tag_methods_mapping: Mapping[Tag: Callable] = {
            Tag.IBAN: partial(self.extract_by_regexp, Tag.IBAN),
            Tag.NUMBER: partial(self.extract_by_regexp, Tag.NUMBER),
            Tag.NAME: partial(self.extract_by_regexp, Tag.NAME),
            Tag.PLACE: partial(self.extract_by_regexp, Tag.PLACE),
            Tag.EMAIL: partial(self.extract_by_regexp, Tag.EMAIL),
            Tag.TIME: partial(self.extract_by_regexp, Tag.TIME)

        }
        self.pattern: Mapping[Tag: str] = {
            Tag.IBAN: r"\b[A-Z]{2}\d{2} ?(?:[0-9a-zA-Z]{4} ?){2,7}[0-9a-zA-Z]{2,4}\b",
            Tag.NUMBER: r"[0-9]+\s?",
            Tag.NAME: r"[A-Z]{1}[a-z]+\s?",
            Tag.PLACE: r"[A-Z]{1}[a-z]+?",
            Tag.EMAIL: r"[A-z0-9]+@.+\s?",
            Tag.TIME: r"([0-1]?[0-9]|2[0-3]):[0-5][0-9]",
        }

    def extract_by_regexp(self, tag: Tag, text: str) -> Optional[str]:
        result = re.search(self.pattern[tag], text)
        if result:
            return result.group(0)
        return None


@lru_cache(maxsize=1)
def get_ner():
    return RegexpNER(Tag.TIME)
