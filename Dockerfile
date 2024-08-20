FROM python:3
ENV PYTHONBUFFERED=1

RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client

WORKDIR /code

COPY ./requirements.txt /code/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

COPY . /code/

EXPOSE 8000
RUN chmod +x /code/run.sh
ENTRYPOINT [ "sh", "/code/run.sh" ]