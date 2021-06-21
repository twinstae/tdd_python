FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# RUN apt install gcc libpq (no longer needed bc we use psycopg2-binary)

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

EXPOSE 8080

WORKDIR /src

CMD ["uvicorn", "src.allocation.fastapi_app:app", "--host", "0.0.0.0", "--port", "8080"]
