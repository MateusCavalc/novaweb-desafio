FROM python:3

COPY . /server

WORKDIR /server

RUN pip install psycopg2

EXPOSE 9090

CMD ["python", "Server.py"]