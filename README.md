
# Desafio Backend Novaweb

Este diretório é referente ao desafio de backend proposto pela Novaweb.
## Solução

Foi implementado uma API REST, utilizando a linguagem Python, que efetua a manutenção de chamadas ao banco de dados PostgreSQL de acordo com as seguintes rotas encontradas em [https://www.getpostman.com/collections/8c6c597a343872987b88](https://www.getpostman.com/collections/da649a75cf5532d3538e) (Postman Collection).

## Deploy

As imagens do ambiente Python que roda o servidor REST e do ambiente Postgres foram geradas pelo github actions utilizando os arquivos Dockerfile.server e Dockerfile.postgres, respectivamente. Para fazer o deploy da API, basta clonar o repositório e executar docker-compose para subir os ambientes:

```bash
  docker-compose up
```

Com isso, a API passa a responder  no endereço **localhost** e porta **9090**.
## Documentação da API

#### Retorna todas as informações sobre os contatos cadastrados

```http
  GET http://localhost:9090/contatos
```

#### Retornar todas as informações sobre os telefones cadastrados

```http
  GET http://localhost:9090/telefones
```

#### Cadastrar novo contato

```http
  POST http://localhost:9090/contato
```

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `nome` | `string` | **Obrigatório**. Nome do contato |
| `email` | `string` | **Obrigatório**. Email do contato|
| `telefones` | `list string` | Lista com os telefones do contato |

+ Request (application/json)

    + Body - Com telefone(s)

            {
                "nome": "Mateus Freitas Cavalcanti",
                "email": "mat.fcavalcanti@gmail.com",
                "telefones": ["(61)90000-0000", "(61)91111-1111"]
            }
    ou
    + Body - Sem telefones

            {
                "nome": "Mateus Freitas Cavalcanti",
                "email": "mat.fcavalcanti@gmail.com",
                "telefones": []
            }

#### Cadastrar novo telefone

```http
  POST http://localhost:9090/telefone
```

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `nome` | `string` | **Obrigatório**. Nome do contato |
| `telefone` | `string` | **Obrigatório**. Telefone para cadastro |

+ Request (application/json)

    + Body

            {
                "nome": "Mateus Freitas Cavalcanti",
                "telefone": "(61)94444-4444"
            }

#### Atualiza informações do contato

```http
  PUT http://localhost:9090/contato
```

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `nome` | `string` | **Obrigatório**. Nome do contato para atualização|
| `infos` | `json` | **Obrigatório**. Json com as informações de atualização|

Dentro do campo `infos` podem ter as seguintes informações:

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `nome` | `string` | Novo nome|
| `email` | `string` | Novo email|
| `telefones` | `list string` | Nova lista de telefones|

É possível alterar **todas** as informações do contato (nome, email e telefones)

+ Request (application/json)

    + Body - Atualizando todas as informações do contato

            {
                "nome": "Mateus Freitas Cavalcanti",
                "infos": {
                    "nome": "Mateus da Silva Cavalcanti",
                    "email": "NOVOEMAIL@email.com",
                    "telefones" : ["novo telefone 1", "novo telefone 2"]
                }
            }
    ou
    + Body - Atualizando somente o email

            {
                "nome": "Mateus Freitas Cavalcanti",
                "infos": {
                    "email": "NOVOEMAIL@email.com",
                }
            }

#### Atualiza informações do telefone

```http
  PUT http://localhost:9090/telefone
```

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `telefone` | `string` | **Obrigatório**. Telefone para atualização|
| `infos` | `json` | **Obrigatório**. Json com as informações de atualização|

Dentro do campo `infos` podem ter as seguintes informações:

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `telefone` | `string` | Novo telefone|
| `nome` | `string` | Novo nome (Busca o ID do contato para chave estrangeira)|

É possível alterar **todas** as informações do telefone (telefone e contato)

+ Request (application/json)

    + Body - Atualizando todas as informações do telefone

            {
                "telefone": "(61)90000-0000",
                "infos": {
                    "telefone": "(61)91111-0000"
                    "nome": "Mateus da Silva Cavalcanti"
                }
            }
    ou
    + Body - Atualizando somente o proprietário do telefone

            {
                "telefone": "(61)90000-0000",
                "infos": {
                    "nome": "NOVO PROPRIETÁRIO"
                }
            }

```http
  DEL http://localhost:9090/contato
```

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `nome` | `string` | **Obrigatório**. Nome do contato a ser removido|

+ Request (application/json)

    + Body - Atualizando todas as informações do telefone

            {
                "nome": "Mateus Freitas Cavalcanti"
            }


```http
  DEL http://localhost:9090/telefone
```

| Parâmetro | Tipo       | Descrição |
|---|---|---|
| `telefone` | `string` | **Obrigatório**. Telefone a ser removido|

+ Request (application/json)

    + Body - Atualizando todas as informações do telefone

            {
                "telefone": "(61)90000-0000"
            }

### Retornos

#### GET

+ Response (application/json)
    + Body - Resposta de requisição de contatos

            {
                "status": "success",
                "data": [{
                    "contato_id": 1,
                    "nome": "Mateus Freitas Cavalcanti",
                    "email": "email@email.com",
                    "telefones": ["telefone 1", "telefone 2"]
                    },
                ...
                ]
            }
    + Body - Resposta de requisição de telefones

            {
                "status": "success",
                "data": [{
                    "telefone_id": 1,
                    "nome": "Mateus Freitas Cavalcanti",
                    "telefone": "telefone 1"
                }, {
                    "telefone_id": 2,
                    "nome": "Mateus Freitas Cavalcanti",
                    "telefone": "telefone 2"
                },
                ...
                ]
            }

    ou
    + Body - **Falha na requisição**

            {
                "status": "failed",
                "error": "Detalhes do erro"
            }

#### POST, PUT e DEL

+ Response (application/json)
    + Body - **Sucesso na operação**

            {
                "status": "success"
            }
ou
+ Body - **Falha na operação**

        {
            "status": "failed",
            "error": "Detalhes do erro"
        }
## Autores

- [@EuMesmo](https://github.com/MateusCavalc)
