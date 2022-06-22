# Método de inicialização de servidor
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from Postgres import Postgres

DATABASE_INSTANCE = Postgres()
DEFAULT_SCHEMA = 'novaweb-desafio'

class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    #handle POST command
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length))

        conn = DATABASE_INSTANCE.connectToDataBase()

        cur = conn.cursor()
        cur.execute('SET SEARCH_PATH TO \'' + DEFAULT_SCHEMA + '\'')
        cur.execute(request_body['query'])
        conn.commit()

        print(cur.rowcount, "Record inserted successfully")

        cur.close()
        conn.close()

        responsePayload = {'status': 'POST great'}

        # Envia informações da assinatura para o cliente
        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle GET command
    def do_GET(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length))

        conn = DATABASE_INSTANCE.connectToDataBase()

        cur = conn.cursor()
        cur.execute('SET SEARCH_PATH TO \'' + DEFAULT_SCHEMA + '\'')
        cur.execute(request_body['query'])
        result = cur.fetchall()
        
        for row in result:
            print(row[1] + ' / ' + row[2])

        cur.close()
        conn.close()

        responsePayload = {'status': 'GET great'}

        # Envia informações da assinatura para o cliente
        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle PUT command
    def do_PUT(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length)) 

        responsePayload = {'status': 'PUT great'}

        # Envia informações da assinatura para o cliente
        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle DELETE command
    def do_DELETE(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length)) 

        responsePayload = {'status': 'DELETE great'}

        # Envia informações da assinatura para o cliente
        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

def Start_http_server():
    print('http server is starting...')
    server_address = ('localhost', 9090)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)  
    print('http server is running...')
    httpd.serve_forever()

def main():
    # SERVIDOR
    Start_http_server()

if __name__ == '__main__':
    main()