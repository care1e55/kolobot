from pathlib import Path

DEFAULT_QUERY = """
"""

DEFAULT_CONTENT = """
"""

DEFAULT_TEXT = """
"""

HEADER = """Write the paragraph related to the QUERY and the TEXT provided

Write no more than 250 words
Use only plain text, no figures or tables
Please be short, coherent, concise
Please write as one paragraph without title
"""


MAIN_CONTENT_TEMPLATE = HEADER + """

QUERY: {query}
TEXT: {docs}

"""

REWRITE_TEMPLATE = """
Please rewrite more coherent dont reduce content length though
Please dont repeat yourself
Please write as one paragraph without title

QUERY: {query}
TEXT: {docs}
"""

PRETRAINED_MODEL = 'sentence-transformers/all-mpnet-base-v2'
DOWNLOADS_PATH = Path("")
