# API de Produtos

Projeto da atividade avaliativa com FastAPI, SQLAlchemy, PostgreSQL via Docker e testes automatizados com Pytest.

## Produtos usados nos testes

```json
{
  "nome": "Placa de Vídeo Triple-Fan",
  "preco": 3500.0,
  "estoque": 1,
  "ativo": true
}
```

```json
{
  "nome": "Livro de Regras Fabula Ultima",
  "preco": 150.0,
  "estoque": 5
}
```

## Subir banco de teste

```bash
docker-compose up -d db_test
```

O banco de teste fica disponível em `localhost:5433` e usa a base `produtos_test_db`.

## Instalar dependências

```bash
pip install -r requirements.txt
```

## Executar testes

```bash
pytest --cov=main -v
```

Também é possível rodar o comando final sugerido no enunciado:

```bash
docker-compose up -d db_test && pytest --cov=main -v
```

## Saída esperada do pytest

A saida deve ser semelhante a esta:

```text
tests/test_produtos.py::test_listar_produtos_com_banco_vazio PASSED
tests/test_produtos.py::test_criar_produto_verifica_persistencia_no_banco PASSED
tests/test_produtos.py::test_criar_produto_aparece_na_listagem PASSED
tests/test_produtos.py::test_buscar_produto_por_id_com_sucesso PASSED
tests/test_produtos.py::test_buscar_produto_com_id_inexistente_retorna_404 PASSED
tests/test_produtos.py::test_deletar_produto_retorna_204 PASSED
tests/test_produtos.py::test_deletar_produto_confirma_remocao_com_get PASSED
tests/test_produtos.py::test_deletar_produto_inexistente_retorna_404 PASSED
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload0] PASSED
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload1] PASSED
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload2] PASSED
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload3] PASSED
tests/test_produtos.py::test_banco_fica_isolado_entre_testes PASSED
tests/test_produtos.py::test_criar_produto_sem_ativo_usa_padrao_true PASSED

---------- coverage: platform win32, python 3.x.x-final-0 -----------
Name      Stmts   Miss  Cover
-----------------------------
main.py      ...    ...   acima de 85%
-----------------------------
TOTAL        ...    ...   acima de 85%

14 passed
```

## Como o isolamento entre testes funciona

A fixture `client`, em `conftest.py`, cria as tabelas no banco de teste antes de cada teste com `Base.metadata.create_all`. Ela substitui a dependência `get_db` da aplicação usando `app.dependency_overrides`, fazendo os endpoints usarem uma sessão conectada ao PostgreSQL de teste.

Depois do `yield`, a mesma fixture limpa o override e executa `Base.metadata.drop_all`, removendo as tabelas e os dados. Por isso, cada teste começa com o banco vazio e não depende do estado deixado por outros testes.

## Executar API localmente

Suba o banco de desenvolvimento:

```bash
docker-compose up -d db
```

Inicie a API:

```bash
uvicorn main:app --reload
```

A documentação interativa fica em `http://localhost:8000/docs`.
