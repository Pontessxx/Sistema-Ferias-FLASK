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
        ORDER BY f.funcionario_id, f.data_inicio;
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
            formatar_data(inicio_iso),
            formatar_data(fim_iso),
            formatar_data(folga_atual_iso),
            formatar_data(folga_proximo_iso),
            inicio_iso,
            fim_iso
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
# (sem folga_anterior e folga_ano)
# =======================================
def adicionar_ferias(funcionario_id, agendado_sap, periodo_dias,
                     abono_peculiario, data_inicio, data_fim, cor):

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
            cor
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        funcionario_id,
        agendado_sap,
        periodo_dias,
        abono_peculiario,
        data_inicio,
        data_fim,
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
# (corrigido — sem folga)
# =======================================
def atualizar_ferias(ferias_id, agendado_sap, periodo_dias,
                     abono_peculiario, data_inicio, data_fim, cor):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ferias
        SET agendado_sap = ?,
            periodo_dias = ?,
            abono_peculiario = ?,
            data_inicio = ?,
            data_fim = ?,
            cor = ?
        WHERE id = ?
    """, (
        agendado_sap,
        periodo_dias,
        abono_peculiario,
        data_inicio,
        data_fim,
        cor,
        ferias_id
    ))

    conn.commit()
    conn.close()

def filtrar_ferias_service(funcionario_id, ano, mes, abono, sap):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            f.id, f.funcionario_id, func.nome,
            f.agendado_sap, f.periodo_dias, f.abono_peculiario,
            f.data_inicio, f.data_fim
        FROM ferias f
        JOIN funcionarios func ON func.id = f.funcionario_id
        WHERE 1=1
    """

    params = []

    if funcionario_id:
        query += " AND f.funcionario_id = ?"
        params.append(funcionario_id)

    if ano:
        query += " AND strftime('%Y', f.data_inicio) = ?"
        params.append(str(ano))

    if mes:
        query += " AND strftime('%m', f.data_inicio) = ?"
        params.append(f"{int(mes):02d}")

    if abono:
        query += " AND f.abono_peculiario = ?"
        params.append(abono)

    if sap:
        query += " AND f.agendado_sap = ?"
        params.append(sap)

    query += " ORDER BY f.funcionario_id, f.data_inicio"

    cursor.execute(query, params)
    dados = cursor.fetchall()
    conn.close()

    lista = []
    for r in dados:
        lista.append({
            "id": r[0],
            "funcionario": r[2],
            "sap": r[3],
            "dias": r[4],
            "abono": r[5],
            "inicio": formatar_data(r[6]),
            "fim": formatar_data(r[7])
        })

    return lista

