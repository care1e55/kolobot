FROM python:3.11.6
COPY . /app
WORKDIR /app

RUN pip install "poetry==1.7.0" && \
    poetry config virtualenvs.create false && \
    poetry config cache-dir /cache/poetry && \
    poetry install --no-dev --no-interaction --no-ansi

ENV PYTHONPATH="/app"
ENV OPENAI_API_KEY="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"
