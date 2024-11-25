FROM python:3.9-slim

WORKDIR /lm_theory

COPY pyproject.toml poetry.lock /lm_theory/
RUN pip install --no-cache-dir poetry && poetry install --no-dev

COPY . /lm_theory

EXPOSE 8800
RUN poetry install
CMD ["poetry", "run", "python", "lm_theory/app.py"]

