FROM python:3.9-buster
COPY requirements /app/requirements.txt
WORKDIR /app
RUN python3.9 -m pip install -U pip setuptools wheel
RUN python3.9 -m pip install -r requirements.txt
COPY . /app
CMD ./run.sh

