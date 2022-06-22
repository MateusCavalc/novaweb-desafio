import urllib.parse as up
import psycopg2

POSTGRES_URL = "postgres://fywwmpwc:tch3IBBOrFOQFdUs6QPd_UosRQjqPByT@kesavan.db.elephantsql.com/fywwmpwc"

class Postgres:
    def __init__(self):
        up.uses_netloc.append("postgres")
        self.url = up.urlparse(POSTGRES_URL)

    def connectToDataBase(self):
        return psycopg2.connect(database=self.url.path[1:],
            user=self.url.username,
            password=self.url.password,
            host=self.url.hostname,
            port=self.url.port
        )