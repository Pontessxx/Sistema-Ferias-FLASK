"""
funcionario_service.py
----------------------
Camada de serviço responsável por manipular os dados da tabela `funcionarios`.

Este módulo fornece funções CRUD para:
- Listar funcionários
- Inserir novo funcionário
- Consultar funcionário por ID
- Atualizar nome de funcionário
- Remover funcionário

Todas as operações utilizam `get_connection()` para acessar o banco SQLite.
"""

from database import get_connection


# ============================================================================
# LISTAR FUNCIONÁRIOS
# ============================================================================
def listar_funcionarios():
    """
    Retorna todos os funcionários cadastrados no banco.

    A consulta é ordenada alfabeticamente.

    Retorno:
        list[tuple]: [(id, nome), ...]
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM funcionarios ORDER BY nome;")
    dados = cursor.fetchall()

    conn.close()
    return dados


# ============================================================================
# ADICIONAR NOVO FUNCIONÁRIO
# ============================================================================
def adicionar_funcionario(nome):
    """
    Insere um novo funcionário na tabela.

    Parâmetro:
        nome (str): nome do funcionário

    Não retorna valor, apenas grava no banco.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO funcionarios (nome) VALUES (?);", (nome,))
    conn.commit()
    conn.close()


# ============================================================================
# CONSULTAR FUNCIONÁRIO POR ID
# ============================================================================
def obter_funcionario_por_id(func_id):
    """
    Busca um funcionário pelo seu ID.

    Parâmetro:
        func_id (int): ID do funcionário

    Retorna:
        tuple (id, nome) ou None caso não exista.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM funcionarios WHERE id = ?;", (func_id,))
    dado = cursor.fetchone()

    conn.close()
    return dado


# ============================================================================
# ATUALIZAR FUNCIONÁRIO
# ============================================================================
def atualizar_funcionario(func_id, novo_nome):
    """
    Atualiza o nome de um funcionário existente.

    Parâmetros:
        func_id (int): ID do funcionário
        novo_nome (str): novo nome para atualizar
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE funcionarios SET nome = ? WHERE id = ?;",
        (novo_nome, func_id)
    )

    conn.commit()
    conn.close()


# ============================================================================
# DELETAR FUNCIONÁRIO
# ============================================================================
def deletar_funcionario(func_id):
    """
    Remove um funcionário do banco de dados.

    Parâmetro:
        func_id (int): ID do funcionário a ser apagado
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM funcionarios WHERE id = ?;", (func_id,))
    conn.commit()
    conn.close()
