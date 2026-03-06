FROM python:3.12.3-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /bot

RUN pip install --upgrade pip wheel "poetry==1.8.2"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY rag_bot .

CMD ["poetry", "run bot"]