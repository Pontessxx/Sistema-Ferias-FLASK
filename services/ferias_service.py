from database import get_connection

# ==========================
# LISTAR FÉRIAS
# ==========================
def listar_ferias():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            f.id,
            f.funcionario_id,
            func.nome,
            f.agendado_sap,
            f.periodo_dias,
            f.abono_peculiario,
            f.data_inicio,
            f.data_fim,
            f.folga_assiduidade_ano_anterior,
            f.folga_assiduidade_ano,
            f.cor
        FROM ferias f
        JOIN funcionarios func ON func.id = f.funcionario_id
        ORDER BY f.data_inicio;
    """

    cursor.execute(query)
    dados = cursor.fetchall()

    conn.close()
    return dados


# ==========================
# SOMATÓRIO DE DIAS
# ==========================
def total_dias_ferias(funcionario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(periodo_dias)
        FROM ferias
        WHERE funcionario_id = ?
    """, (funcionario_id,))

    total = cursor.fetchone()[0]
    conn.close()

    return total or 0


# ==========================
# VERIFICAR SOBREPOSIÇÃO
# ==========================
def existe_sobreposicao(funcionario_id, inicio, fim, ignorar_ferias_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT COUNT(*)
        FROM ferias
        WHERE funcionario_id = ?
        AND data_inicio <= ?
        AND data_fim >= ?
    """

    params = [funcionario_id, fim, inicio]

    if ignorar_ferias_id:
        query += " AND id != ?"
        params.append(ignorar_ferias_id)

    cursor.execute(query, params)
    resultado = cursor.fetchone()[0]

    conn.close()

    return resultado > 0


# ==========================
# ADICIONAR FÉRIAS
# ==========================
def adicionar_ferias(funcionario_id, agendado_sap, periodo_dias, abono_peculiario,
                     data_inicio, data_fim, folga_ano_anterior, folga_ano, cor):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ferias (
            funcionario_id,
            agendado_sap,
            periodo_dias,
            abono_peculiario,
            data_inicio,
            data_fim,
            folga_assiduidade_ano_anterior,
            folga_assiduidade_ano,
            cor
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        funcionario_id,
        agendado_sap,
        periodo_dias,
        abono_peculiario,
        data_inicio,
        data_fim,
        folga_ano_anterior,
        folga_ano,
        cor
    ))

    conn.commit()
    conn.close()


# ==========================
# DELETAR
# ==========================
def deletar_ferias(ferias_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ferias WHERE id = ?;", (ferias_id,))
    conn.commit()
    conn.close()


# ==========================
# ATUALIZAR
# ==========================
def atualizar_ferias(ferias_id, agendado_sap, periodo_dias, abono_peculiario,
                     data_inicio, data_fim, folga_ano_anterior, folga_ano, cor):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ferias
        SET agendado_sap = ?,
            periodo_dias = ?,
            abono_peculiario = ?,
            data_inicio = ?,
            data_fim = ?,
            folga_assiduidade_ano_anterior = ?,
            folga_assiduidade_ano = ?,
            cor = ?
        WHERE id = ?
    """, (
        agendado_sap,
        periodo_dias,
        abono_peculiario,
        data_inicio,
        data_fim,
        folga_ano_anterior,
        folga_ano,
        cor,
        ferias_id
    ))

    conn.commit()
    conn.close()
