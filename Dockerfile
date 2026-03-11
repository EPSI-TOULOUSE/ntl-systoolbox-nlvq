FROM python:3.14.3-alpine3.23

RUN adduser -S ntl
RUN mkdir /app && chown -R ntl /app

USER ntl
WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY src/ ./src/

ENTRYPOINT ["python", "-m", "src.main"]
