
## Deploy

As imagens do ambiente Python que roda o servidor REST e do ambiente Postgres foram geradas pelo github actions utilizando os arquivos Dockerfile.server e Dockerfile.postgres, respectivamente. Para fazer o deploy da API, basta clonar o repositório e executar docker-compose para subir os ambientes:

```bash
  docker-compose up
```

Com isso, a API passa a responder  no endereço **localhost** e porta **9090**.