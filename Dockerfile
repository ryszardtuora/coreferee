# syntax=docker/dockerfile:1
FROM python:3.9

RUN apt-get update
RUN python3 -m pip install --upgrade pip setuptools wheel build && \
    python3 -m pip install --index-url https://pypi.clarin-pl.eu/simple plwn_api && \
    python3 -m pip install spacy==3.1.2  coreferee && \
    python3 -m spacy download pl_core_news_lg

RUN wget https://minio.clarin-pl.eu/public/models/plwn_api_dumps/plwn_dump_27-03-2018.sqlite -O plwn.sqlite

RUN git clone https://github.com/ryszardtuora/coreferencer.git --branch coreferencer --depth 1 && \
  python3 -m build coreferencer && \
  python3 -m pip install coreferencer/dist/coreferencer-1.1.2-py3-none-any.whl && \
  python3 -m coreferencer install pl

