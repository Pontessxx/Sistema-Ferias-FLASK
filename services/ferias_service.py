from database import get_connection

# ==========================
# LISTAR FÉRIAS
# ==========================
def listar_ferias():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT f.id,
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
# EDITAR / OBTER POR ID
# ==========================
def obter_ferias_por_id(ferias_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, funcionario_id, agendado_sap, periodo_dias, abono_peculiario,
               data_inicio, data_fim, folga_assiduidade_ano_anterior,
               folga_assiduidade_ano, cor
        FROM ferias
        WHERE id = ?
    """, (ferias_id,))

    dados = cursor.fetchone()
    conn.close()
    return dados


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
        agendado_sap, periodo_dias, abono_peculiario,
        data_inicio, data_fim, folga_ano_anterior,
        folga_ano, cor, ferias_id
    ))

    conn.commit()
    conn.close()
