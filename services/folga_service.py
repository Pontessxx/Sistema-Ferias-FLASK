from database import get_connection

def obter_folga(funcionario_id, ano):
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


def adicionar_folga(funcionario_id, ano, data_folga):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO folga_assiduidade (funcionario_id, ano, data_folga)
        VALUES (?, ?, ?)
    """, (funcionario_id, ano, data_folga))

    conn.commit()
    conn.close()


def atualizar_folga(folga_id, nova_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE folga_assiduidade
        SET data_folga = ?
        WHERE id = ?
    """, (nova_data, folga_id))

    conn.commit()
    conn.close()


def deletar_folga(folga_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM folga_assiduidade WHERE id = ?;", (folga_id,))
    conn.commit()
    conn.close()
