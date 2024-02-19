from pathlib import Path

DEFAULT_TITLE = """
"""

DEFAULT_CONTENT = """
"""

DEFAULT_TEXT = """
"""

MAIN_CONTENT_TEMPLATE = """Write the paragraph related to the QUERY and the TEXT provided

Write no more than 250 words
Use only plain text, no figures or tables
Please be short, coherent, concise
Please write as one paragraph without title
Answer in Russian

QUERY: {query}
TEXT: {docs}

"""

REWRITE_TEMPLATE = """
Please rewrite more coherent dont reduce content length though
Please dont repeat yourself
Please write as one paragraph without title
Please write in Russian

QUERY: {query}
TEXT: {docs}
"""

PRETRAINED_MODEL = 'sentence-transformers/all-mpnet-base-v2'
DOWNLOADS_PATH = Path("/home/care1e55/code/Ilona/resources/ilona/data/лекции/")