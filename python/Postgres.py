import os
import urllib.parse as up
import psycopg2
import time

POSTGRES_URL = 'postgres://' + os.getenv('DB_USER') + ':' + os.getenv('DB_PASSWORD') + '@' + os.getenv('DB_ADDRESS') + ':' + os.getenv('DB_PORT') + '/' + os.getenv('DB_NAME')


# Classe de conexão com o banco Postgres
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
        try:
            return psycopg2.connect(**self.db_settings)
        except Exception as e:
            raise e

def Check_tables(db_instance):
    
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

    retry_connection = True
    conn = None
    cur = None
    time.sleep(5)
    while retry_connection:
        try:
            conn = db_instance.connectToDataBase()
            cur = conn.cursor()
            cur.execute(contato_table_create)
            cur.execute(telefone_table_create)
            conn.commit()
            retry_connection = False
            
        except Exception as e:
            print(str(e), flush=True)
            if e != "FATAL:  the database system is starting up":
                retry_connection = False
            else:
                print("Waiting for database to come online...", flush=True)
                time.sleep(5)
                print("Retrying connection...", flush=True)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

# Retorna o id do contato a partir do nome
def Get_ContatoID_by_name(cur, nome):
    try:
        query = 'SELECT contato_id ' + \
                'FROM contato ' + \
                'WHERE nome=\'' + nome + '\''

        cur.execute(query)
        data_row = cur.fetchone()
        if data_row is not None:
            return data_row[0]
        else:
            raise ContatoNotFound(nome)
    except Exception as e:
        raise e

# Importa na tabela 'telefone' a lista de telefones 'telefone_list'
def Load_telefones(cur, contato_id, telefone_list):
    try:
        for telefone in telefone_list:
            query = 'INSERT INTO telefone (contato_id, telefone) ' + \
                    'VALUES (\'{}\', \'{}\')' \
                    .format(contato_id, telefone)

            cur.execute(query)

    except Exception as e:
        raise e

# Retorna a lista de telefones associada ao contato 'contato_nome'
def Get_telefones_by_name(cur, contato_nome):
    try:
        contato_id = Get_ContatoID_by_name(cur, contato_nome);
        query = 'SELECT telefone ' + \
                'FROM telefone ' + \
                'WHERE contato_id={}' \
                .format(contato_id)

        cur.execute(query)
        telefones = []
        for row in cur.fetchall():
            telefones.append(row[0])

        return telefones

    except Exception as e:
        raise e

# Remove os telefones presentes na lista 'telefone_list'
def Del_telefones(cur, telefone_list):
    try:
        query = 'DELETE FROM telefone ' + \
                'WHERE telefone ' + \
                'IN {}' \
                .format(tuple(telefone_list))

        cur.execute(query)

    except Exception as e:
        raise e

# Atualiza os telefones associados ao contato 'contato_nome' de acordo com a lista 'new_telefones' recebida
def Update_contato_telefones(cur, contato_nome, new_telefones):  
    try:
        old_telefones = Get_telefones_by_name(cur, contato_nome)
        to_remove = []

        for old_telefone in old_telefones:
            if old_telefone not in new_telefones:
                to_remove.append(old_telefone)
        
        query = 'DELETE FROM telefone ' + \
                'WHERE telefone ' + \
                'IN {}' \
                .format(tuple(to_remove))

        cur.execute(query)

        contato_id = Get_ContatoID_by_name(cur, contato_nome);

        for new_telefone in new_telefones:
            if new_telefone not in old_telefones:
                query = 'INSERT INTO telefone (contato_id, telefone) ' + \
                        'VALUES (\'{}\', \'{}\')' \
                        .format(contato_id, new_telefone)

                cur.execute(query)

    except Exception as e:
        raise e