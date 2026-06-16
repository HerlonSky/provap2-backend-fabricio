import pytest


PRODUTO_PLACA_VIDEO = {
    "nome": "Placa de Vídeo Triple-Fan",
    "preco": 3500.00,
    "estoque": 1,
    "ativo": True,
}

PRODUTO_LIVRO = {
    "nome": "Livro de Regras Fabula Ultima",
    "preco": 150.00,
    "estoque": 5,
}


def test_listar_produtos_com_banco_vazio(client):
    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json() == []


def test_criar_produto_verifica_persistencia_no_banco(client):
    response = client.post("/produtos", json=PRODUTO_PLACA_VIDEO)

    assert response.status_code == 201
    produto_id = response.json()["id"]

    get_response = client.get(f"/produtos/{produto_id}")
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == PRODUTO_PLACA_VIDEO["nome"]


def test_criar_produto_aparece_na_listagem(client):
    response = client.post("/produtos", json=PRODUTO_LIVRO)

    assert response.status_code == 201

    list_response = client.get("/produtos")
    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "id": response.json()["id"],
            "nome": PRODUTO_LIVRO["nome"],
            "preco": PRODUTO_LIVRO["preco"],
            "estoque": PRODUTO_LIVRO["estoque"],
            "ativo": True,
        }
    ]


def test_buscar_produto_por_id_com_sucesso(client, produto_existente):
    response = client.get(f"/produtos/{produto_existente['id']}")

    assert response.status_code == 200
    assert response.json() == produto_existente


def test_buscar_produto_com_id_inexistente_retorna_404(client):
    response = client.get("/produtos/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Produto nao encontrado"


def test_deletar_produto_retorna_204(client, produto_existente):
    response = client.delete(f"/produtos/{produto_existente['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_deletar_produto_confirma_remocao_com_get(client, produto_existente):
    delete_response = client.delete(f"/produtos/{produto_existente['id']}")
    get_response = client.get(f"/produtos/{produto_existente['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_deletar_produto_inexistente_retorna_404(client):
    response = client.delete("/produtos/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Produto nao encontrado"


@pytest.mark.parametrize(
    "payload",
    [
        {"nome": "", "preco": 10.0, "estoque": 1},
        {"nome": "Produto sem preco positivo", "preco": 0.0, "estoque": 1},
        {"nome": "Produto com estoque negativo", "preco": 10.0, "estoque": -1},
        {"preco": 10.0, "estoque": 1},
    ],
)
def test_criar_produto_com_payload_invalido_retorna_422(client, payload):
    response = client.post("/produtos", json=payload)

    assert response.status_code == 422


def test_banco_fica_isolado_entre_testes(client):
    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json() == []


def test_criar_produto_sem_ativo_usa_padrao_true(client):
    response = client.post("/produtos", json=PRODUTO_LIVRO)

    assert response.status_code == 201
    assert response.json()["ativo"] is True
