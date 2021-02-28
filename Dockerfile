FROM python:3.8-slim-buster

WORKDIR /app

RUN apt-get update -y && apt-get -y install libspatialindex-dev

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-m", "e3f2s.webapp"]
