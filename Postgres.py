import logging
import urllib.parse as up
import psycopg2
from psycopg2.extras import LoggingConnection

POSTGRES_URL = "postgres://novaweb-desafio-user:novaweb-desafio-password@postgres_server:5432/postgres"
# POSTGRES_URL = "postgres://novaweb-desafio-user:novaweb-desafio-password@0.0.0.0:5432/postgres"

class Postgres:
    def __init__(self):
        up.uses_netloc.append("postgres")
        url = up.urlparse(POSTGRES_URL)
        self.db_settings = {
            "user": url.username,
            "password": url.password,
            "host": url.hostname,
            "port": url.port,
            "database": url.path[1:],
        }

    def connectToDataBase(self):
        return psycopg2.connect(**self.db_settings)