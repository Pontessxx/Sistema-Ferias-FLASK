"""
folga_service.py
----------------
Camada de serviço responsável por manipular os dados da tabela
`folga_assiduidade`, que armazena as folgas concedidas por assiduidade
aos funcionários.

Este módulo fornece funções para:

- Consultar folga existente para um funcionário e ano
- Inserir nova folga
- Atualizar folga existente
- Deletar folga
- Listar todas as folgas registradas junto com o nome do funcionário

Cada função acessa o banco utilizando `get_connection()`.
"""

from database import get_connection


# ============================================================================
# OBTER FOLGA POR FUNCIONÁRIO E ANO
# ============================================================================
def obter_folga(funcionario_id, ano):
    """
    Retorna a folga de um funcionário em determinado ano, caso exista.

    Parâmetros:
        funcionario_id (int)
        ano (int)

    Retorna:
        tuple (id, data_folga)
        ou
        None → se não houver registro para o ano informado.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, data_folga
        FROM folga_assiduidade
        WHERE funcionario_id = ? AND ano = ?
        LIMIT 1;
    """, (funcionario_id, ano))

    dado = cursor.fetchone()
    conn.close()
    return dado  # (id, data_folga) ou None


# ============================================================================
# ADICIONAR NOVA FOLGA
# ============================================================================
def adicionar_folga(funcionario_id, ano, data_folga):
    """
    Insere uma nova folga de assiduidade na tabela.

    Parâmetros:
        funcionario_id (int)
        ano (int)
        data_folga (str → formato ISO yyyy-mm-dd)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO folga_assiduidade (funcionario_id, ano, data_folga)
        VALUES (?, ?, ?)
    """, (funcionario_id, ano, data_folga))

    conn.commit()
    conn.close()


# ============================================================================
# ATUALIZAR DATA DE UMA FOLGA EXISTENTE
# ============================================================================
def atualizar_folga(folga_id, nova_data):
    """
    Atualiza a data de uma folga já cadastrada.

    Parâmetros:
        folga_id (int): ID do registro a ser atualizado
        nova_data (str ISO)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE folga_assiduidade
        SET data_folga = ?
        WHERE id = ?
    """, (nova_data, folga_id))

    conn.commit()
    conn.close()


# ============================================================================
# DELETAR FOLGA
# ============================================================================
def deletar_folga(folga_id):
    """
    Remove uma folga da tabela com base em seu ID.

    Parâmetros:
        folga_id (int)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM folga_assiduidade WHERE id = ?;", (folga_id,))
    conn.commit()
    conn.close()


# ============================================================================
# LISTAR TODAS AS FOLGAS
# ============================================================================
def listar_folgas():
    """
    Lista todas as folgas registradas, incluindo:

        - ID da folga
        - Nome do funcionário
        - Ano da folga
        - Data da folga

    A consulta faz JOIN com a tabela `funcionarios` para retornar o nome.

    Retorna:
        list[dict]:
            [
                {
                    "id": <id>,
                    "nome": <nome funcionário>,
                    "ano": <ano>,
                    "data_folga": <data>
                },
                ...
            ]
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.id, func.nome, f.ano, f.data_folga
        FROM folga_assiduidade f
        JOIN funcionarios func ON func.id = f.funcionario_id
        ORDER BY func.nome, f.ano;
    """)

    dados = cursor.fetchall()
    conn.close()

    # Converte linhas em objetos (dicionários)
    return [
        {
            "id": row[0],
            "nome": row[1],
            "ano": row[2],
            "data_folga": row[3]
        }
        for row in dados
    ]
