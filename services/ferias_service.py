from database import get_connection


# =======================================
# FORMATAR DATA PARA dd-MM-yyyy
# =======================================
def formatar_data(data_str):
    if not data_str:
        return None
    ano, mes, dia = data_str.split("-")
    return f"{dia}/{mes}/{ano}"


# =======================================
# LISTAR FÉRIAS + FOLGAS POR ANO
# =======================================

def listar_ferias(ano_atual, ano_proximo):
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
            (
                SELECT data_folga 
                FROM folga_assiduidade 
                WHERE funcionario_id = f.funcionario_id AND ano = ? 
                LIMIT 1
            ) AS folga_atual,
            (
                SELECT data_folga 
                FROM folga_assiduidade 
                WHERE funcionario_id = f.funcionario_id AND ano = ? 
                LIMIT 1
            ) AS folga_proximo
        FROM ferias f
        JOIN funcionarios func ON func.id = f.funcionario_id
        ORDER BY f.data_inicio;
    """

    cursor.execute(query, (ano_atual, ano_proximo))
    dados = cursor.fetchall()
    conn.close()

    dados_formatados = []

    for row in dados:
        id, func_id, nome, sap, dias, abono, inicio_iso, fim_iso, folga_atual_iso, folga_proximo_iso = row

        dados_formatados.append((
            id,
            func_id,
            nome,
            sap,
            dias,
            abono,

            # formato BR para exibir na tabela
            formatar_data(inicio_iso),
            formatar_data(fim_iso),
            formatar_data(folga_atual_iso),
            formatar_data(folga_proximo_iso),

            # formato ISO para o JS preencher o input
            inicio_iso,
            fim_iso,
            folga_atual_iso or "",
            folga_proximo_iso or ""
        ))

    return dados_formatados


# =======================================
# SOMA DE DIAS
# =======================================
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


# =======================================
# VERIFICAR SOBREPOSIÇÃO
# =======================================
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


# =======================================
# ADICIONAR FÉRIAS
# =======================================
def adicionar_ferias(funcionario_id, agendado_sap, periodo_dias,
                     abono_peculiario, data_inicio, data_fim,
                     folga_ano_anterior, folga_ano, cor):

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


# =======================================
# DELETAR FÉRIAS
# =======================================
def deletar_ferias(ferias_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ferias WHERE id = ?;", (ferias_id,))
    conn.commit()
    conn.close()


# =======================================
# ATUALIZAR FÉRIAS
# =======================================
def atualizar_ferias(ferias_id, agendado_sap, periodo_dias,
                     abono_peculiario, data_inicio, data_fim,
                     folga_ano_anterior, folga_ano, cor):

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
