# Método de inicialização de servidor
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from Postgres import Postgres

DATABASE_INSTANCE = Postgres()

def Get_ContatoID_by_name(cur, nome):
    try:
        query = 'SELECT contato_id ' + \
                'FROM contato ' + \
                'WHERE nome=\'' + nome + '\''

        cur.execute(query)
        data_row = cur.fetchone()
        return data_row[0]
    except Exception as e:
        raise e

class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _no_route(self):
        self.send_response(404)
        self.end_headers()
        html = '<h1>Não existe rota \'' + self.path + '\' no momento.<h1>'
        self.wfile.write(html.encode())

    def do_HEAD(self):
        self._set_headers()

    #handle GET method
    def do_GET(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length))

        curr_schema = request_body['schema']

        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            cur.execute('SET SEARCH_PATH TO \'' + curr_schema + '\'')
            
            if self.path == '/contatos':
                query = 'SELECT * ' + \
                        'FROM contato'
            elif self.path == '/telefones':
                query = 'SELECT telefone.telefone_id, contato.nome, telefone.telefone ' + \
                        'FROM contato ' + \
                        'INNER JOIN telefone ON contato.contato_id=telefone.contato_id'
            else:
                self._no_route()
                return

            cur.execute(query)
            columns = cur.description

            data_array = []
            for row in cur.fetchall():
                data = {}
                for i, row_data in enumerate(row):
                    data[columns[i][0]] = row_data

                data_array.append(data)

            responsePayload = {'status': 'success'}
            responsePayload['data'] = data_array

        except Exception as e:
            print('> Error:', e)
            responsePayload = {'status': 'failed', 'error': str(e)}
        finally:
            cur.close()
            conn.close()

        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle POST method
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length))

        curr_schema = request_body['schema']
        responsePayload = {}

        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            cur.execute('SET SEARCH_PATH TO \'' + curr_schema + '\'')

            if self.path == '/contato':
                user_data = request_body['infos']
                query = 'INSERT INTO contato (nome, email) ' + \
                        'VALUES (\'{}\', \'{}\')' \
                        .format(user_data['nome'], user_data['email'])
            elif self.path == '/telefone':
                user_data = request_body['infos']

                contato_id = Get_ContatoID_by_name(cur, user_data['nome']);

                query = 'INSERT INTO telefone (contato_id, telefone) ' + \
                        'VALUES (\'{}\', \'{}\')' \
                        .format(contato_id, user_data['telefone'])

            else:
                self._no_route()
                return
            
            cur.execute(query)
            conn.commit()
            responsePayload = {'status': 'success'}

        except Exception as e:
            print('> Error:', e)
            responsePayload = {'status': 'failed', 'error': str(e)}
        finally:
            cur.close()
            conn.close()

        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle PUT method
    def do_PUT(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length)) 

        responsePayload = {}

        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            
            fields = request_body['fields']
            cols = '('
            for i, field in enumerate(fields):
                cols += field
                if(i < len(fields) - 1):
                    cols += ','

            cols += ')'

            if self.path == '/contato':
                user_data = request_body['infos']
                query = 'INSERT INTO contato (nome, email) ' + \
                        'VALUES (\'{}\', \'{}\')' \
                        .format(user_data['nome'], user_data['email'])
            elif self.path == '/telefone':
                user_data = request_body['infos']

                contato_id = Get_ContatoID_by_name(cur, user_data['nome']);

                query = 'INSERT INTO telefone (contato_id, telefone) ' + \
                        'VALUES (\'{}\', \'{}\')' \
                        .format(contato_id, user_data['telefone'])

            else:
                self._no_route()
                return
            
            cur.execute(query)
            conn.commit()
            responsePayload = {'status': 'success'}

        except Exception as e:
            print('> Error:', e)
            responsePayload = {'status': 'failed', 'error': str(e)}
        finally:
            cur.close()
            conn.close()

        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle DELETE method
    def do_DELETE(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length)) 

        

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
