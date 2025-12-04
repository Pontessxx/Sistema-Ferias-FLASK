from database import get_connection

# ======================
# LISTAR
# ======================
def listar_funcionarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM funcionarios ORDER BY nome;")
    dados = cursor.fetchall()

    conn.close()
    return dados


# ======================
# ADICIONAR
# ======================
def adicionar_funcionario(nome):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO funcionarios (nome) VALUES (?);", (nome,))
    conn.commit()
    conn.close()


# ======================
# OBTÉM POR ID
# ======================
def obter_funcionario_por_id(func_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM funcionarios WHERE id = ?;", (func_id,))
    dado = cursor.fetchone()

    conn.close()
    return dado


# ======================
# ATUALIZAR
# ======================
def atualizar_funcionario(func_id, novo_nome):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE funcionarios SET nome = ? WHERE id = ?;", (novo_nome, func_id))
    conn.commit()
    conn.close()


# ======================
# DELETAR
# ======================
def deletar_funcionario(func_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM funcionarios WHERE id = ?;", (func_id,))
    conn.commit()
    conn.close()
