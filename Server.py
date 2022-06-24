# Método de inicialização de servidor
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from Postgres import Postgres

DATABASE_INSTANCE = Postgres()

def Check_tables():
    
    contato_table_create = 'CREATE TABLE IF NOT EXISTS contato ' + \
                            '( ' + \
                                'contato_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ), ' + \
                                'nome text COLLATE pg_catalog."default" NOT NULL, ' + \
                                'email text COLLATE pg_catalog."default" NOT NULL, ' + \
                                'CONSTRAINT contato_pkey PRIMARY KEY (contato_id), ' + \
                                'CONSTRAINT contato_nome_key UNIQUE (nome) ' + \
                            ')'
    telefone_table_create = 'CREATE TABLE IF NOT EXISTS telefone ' + \
                            '( ' + \
                                'telefone_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ), ' + \
                                'telefone text COLLATE pg_catalog."default" NOT NULL, ' + \
                                'contato_id integer NOT NULL, ' + \
                                'CONSTRAINT telefone_pkey PRIMARY KEY (telefone_id), ' + \
                                'CONSTRAINT telefone_telefone_key UNIQUE (telefone), ' + \
                                'CONSTRAINT telefone_contato_id_fkey FOREIGN KEY (contato_id) ' + \
                                    'REFERENCES contato (contato_id) MATCH SIMPLE ' + \
                            ')'
    
    conn = DATABASE_INSTANCE.connectToDataBase()
    cur = conn.cursor()
    cur.execute(contato_table_create)
    cur.execute(telefone_table_create)
    conn.commit()
    cur.close()
    conn.close()

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
        html = '<h1>No route \'' + self.path + '\'.<h1>'
        self.wfile.write(html.encode())

    def do_HEAD(self):
        self._set_headers()

    #handle GET method
    def do_GET(self):

        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            
            if self.path == '/contatos':
                query = 'SELECT nome, email, STRING_AGG(telefone, \', \') as telefones ' + \
                        'FROM contato ' + \
                        'INNER JOIN telefone ON contato.contato_id=telefone.contato_id ' + \
                        'GROUP BY nome, email'
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
                    if columns[i][0] == 'telefones':
                        data[columns[i][0]] = row_data.split(',')
                    else:
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

        responsePayload = {}

        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            user_data = request_body['infos']

            # TODO
            if self.path == '/contato':
                query = 'INSERT INTO contato (nome, email) ' + \
                        'VALUES (\'{}\', \'{}\')' \
                        .format(user_data['nome'], user_data['email'])
            elif self.path == '/telefone':
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
    #TODO
    def do_PUT(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length)) 

        responsePayload = {}

        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            
            new_infos = request_body['infos']
            set_stat = ''

            for i, field in enumerate(new_infos.keys()):
                set_stat += field + '=\'' + new_infos[field] + '\''
                if(i < len(new_infos.keys()) - 1):
                    set_stat += ','

            if self.path == '/contato':
                query = 'UPDATE contato ' + \
                        'SET ' + set_stat + ' ' + \
                        'WHERE nome=\'{}\'' \
                        .format(request_body['nome'])
            elif self.path == '/telefone':
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

        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            data = request_body['info']
            
            if self.path == '/contato':
                query = 'DELETE FROM contato ' + \
                        'WHERE nome=\'' + data['nome'] + '\''
            elif self.path == '/telefone':
                query = 'DELETE FROM telefone ' + \
                        'WHERE telefone=\'' + data['telefone'] + '\''
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

def Start_http_server():
    print('http server is starting...')
    Check_tables()
    server_address = ('localhost', 9090)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)  
    print('http server is running...')
    httpd.serve_forever()

def main():
    # SERVIDOR
    Start_http_server()

if __name__ == '__main__':
    main()
