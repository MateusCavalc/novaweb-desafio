# Método de inicialização de servidor
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from Postgres import *
from CustomExceptions import ContatoNotFound

DATABASE_INSTANCE = Postgres()

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
        conn = None
        cur = None
        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            
            if self.path == '/contatos':
                query = 'SELECT contato.contato_id, nome, email, STRING_AGG(telefone, \',\') as telefones ' + \
                        'FROM contato ' + \
                        'LEFT JOIN telefone ON contato.contato_id=telefone.contato_id ' + \
                        'GROUP BY contato.contato_id, nome, email'
            elif self.path == '/telefones':
                query = 'SELECT telefone.telefone_id, contato.nome, telefone.telefone ' + \
                        'FROM contato ' + \
                        'INNER JOIN telefone ON contato.contato_id=telefone.contato_id'
            else:
                self._no_route()
                return

            cur.execute(query)
            columns = cur.description

            # Monta json de resposta com os dados da query select
            data_array = []
            for row in cur.fetchall():
                data = {}
                for i, row_data in enumerate(row):
                    if columns[i][0] == 'telefones':
                        if row_data:
                            data[columns[i][0]] = row_data.split(',')
                        else:
                            data[columns[i][0]] = []
                    else:
                        data[columns[i][0]] = row_data

                data_array.append(data)

            responsePayload = {'status': 'success'}
            responsePayload['data'] = data_array

        except Exception as e:
            print('> Error:', e)
            responsePayload = {'status': 'failed', 'error': str(e)}
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle POST method
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length))

        responsePayload = {}

        conn = None
        cur = None
        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()

            if self.path == '/contato':
                query = 'INSERT INTO contato (nome, email) ' + \
                        'VALUES (\'{}\', \'{}\') RETURNING contato_id' \
                        .format(request_body['nome'], request_body['email'])

                cur.execute(query)
                
                # Se tem o campo de telefones, insere a lista na tabela 'telefone'
                if request_body['telefones']:
                    new_contatoid = cur.fetchone()[0]
                    Load_telefones(cur, new_contatoid, request_body['telefones'])

            elif self.path == '/telefone':
                contato_id = Get_ContatoID_by_name(cur, request_body['nome']);

                query = 'INSERT INTO telefone (contato_id, telefone) ' + \
                        'VALUES (\'{}\', \'{}\')' \
                        .format(contato_id, request_body['telefone'])

                cur.execute(query)

            else:
                self._no_route()
                return
            
            conn.commit()
            responsePayload = {'status': 'success'}

        except Exception as e:
            print('> Error:', e)
            responsePayload = {'status': 'failed', 'error': str(e)}
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle PUT method
    def do_PUT(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length)) 

        responsePayload = {}

        conn = None
        cur = None
        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            
            new_infos = request_body['infos']
            set_stat = ''

            # Se tem lista de telefones, atualiza os telefones associados com o contato
            if 'telefones' in new_infos.keys():
                contato_nome = request_body['nome']
                new_telefones = new_infos['telefones']
                Update_contato_telefones(cur, contato_nome, new_telefones)
                # Apaga o campo para montar o SET statement da query de UPDATE
                del new_infos['telefones']

            # Se é troca de proprietário de telefone
            if ('telefone' in request_body.keys()) and ('nome' in new_infos.keys()):
                # Adiciona campo 'contato_id' para chave estrangeira
                new_infos['contato_id'] = Get_ContatoID_by_name(cur, new_infos['nome'])
                # Apaga o campo para montar o SET statement da query de UPDATE com o campo contato_id adicionado
                del new_infos['nome']
            
            # Monta string do SET statement da query SQL
            for i, field in enumerate(new_infos.keys()):
                if type(new_infos[field]) is str:
                    set_stat += field + '=\'' + new_infos[field] + '\''
                elif type(new_infos[field]) is int:
                    set_stat += field + '=' + str(new_infos[field])

                if(i < len(new_infos.keys()) - 1):
                    set_stat += ','

            if self.path == '/contato':
                contato_nome = request_body['nome']
                query = 'UPDATE contato ' + \
                        'SET ' + set_stat + ' ' + \
                        'WHERE nome=\'{}\'' \
                        .format(contato_nome)
            elif self.path == '/telefone':
                telefone = request_body['telefone']
                query = 'UPDATE telefone ' + \
                        'SET ' + set_stat + ' ' + \
                        'WHERE telefone=\'{}\'' \
                        .format(telefone)

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
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

    #handle DELETE method
    def do_DELETE(self):
        length = int(self.headers.get('content-length'))
        request_body = json.loads(self.rfile.read(length)) 

        conn = None
        cur = None
        try:
            conn = DATABASE_INSTANCE.connectToDataBase()
            cur = conn.cursor()
            
            if self.path == '/contato':
                contato_nome = request_body['nome']
                tel_list = Get_telefones_by_name(cur, contato_nome) # Pega a lista de telefones do contato
                Del_telefones(cur, tel_list) # Apaga os telefones do contato
                # Apaga o contato
                query = 'DELETE FROM contato ' + \
                        'WHERE nome=\'' + contato_nome + '\''
            elif self.path == '/telefone':
                telefone = request_body['telefone']
                # Apaga o telefone
                query = 'DELETE FROM telefone ' + \
                        'WHERE telefone=\'' + telefone + '\''
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
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

        self._set_headers()
        self.wfile.write(json.dumps(responsePayload).encode())

def Start_http_server():
    print('http server is starting...')

    # Executa queries de criação de tabela
    Check_tables(DATABASE_INSTANCE)

    server_address = ('0.0.0.0', 9090)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)  
    print('http server is running...')
    httpd.serve_forever()

def main():
    # SERVIDOR
    Start_http_server()

if __name__ == '__main__':
    main()
