FROM python:3.6.12-buster

RUN apt update && apt install -y graphviz

RUN mkdir /install

WORKDIR /install

COPY ./requirements.txt /requirements.txt

RUN pip install  --requirement /requirements.txt

COPY . .

EXPOSE 80

ENTRYPOINT ["./entrypoint"]
