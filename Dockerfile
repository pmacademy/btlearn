FROM ubuntu:latest

RUN apt-get update

RUN apt-get install -y \
    python3-dev default-libmysqlclient-dev build-essential \
    python3-pip 

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt 

EXPOSE 5000

ENTRYPOINT ["gunicorn"]

CMD ["main:app", "-b", "0.0.0.0:5000", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1000"]



