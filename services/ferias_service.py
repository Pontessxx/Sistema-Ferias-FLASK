"""
ferias_service.py
-----------------
Camada de serviço responsável por toda a lógica de acesso e manipulação
dos dados de férias.

Este módulo fornece:

- Conversão e formatação de datas
- Consulta completa de férias com folgas relacionadas
- Cálculo de total de dias de férias de um funcionário
- Verificação de sobreposição entre períodos
- Cadastro, atualização e remoção de férias
- Filtros avançados para exibição
- Retorno de dados especializados para o gráfico Gantt

Todas as funções aqui acessam o banco de dados usando `get_connection()`.
"""

from database import get_connection


# ============================================================================
# FORMATAÇÃO DE DATA (ISO → dd/MM/yyyy)
# ============================================================================
def formatar_data(data_str):
    """
    Converte datas do formato ISO (yyyy-mm-dd) para dd/mm/yyyy.

    Parâmetros:
        data_str (str): data vinda do banco no formato ISO.

    Retorna:
        str: data formatada para exibição.
        None: caso data seja nula.
    """
    if not data_str:
        return None
    ano, mes, dia = data_str.split("-")
    return f"{dia}/{mes}/{ano}"


# ============================================================================
# LISTAR TODAS AS FÉRIAS (+ FOLGAS) POR ANO
# ============================================================================
def listar_ferias(ano_atual, ano_proximo):
    """
    Retorna lista de férias com informações completas,
    incluindo folga de assiduidade do ano atual e do ano seguinte.

    O retorno já vem formatado para exibição no HTML.

    Parâmetros:
        ano_atual (int)
        ano_proximo (int)

    Retorna:
        list[tuple]: contendo:
            (id, func_id, nome, sap, dias, abono,
             inicio_formatado, fim_formatado,
             folga_atual_formatada, folga_proximo_formatada,
             inicio_iso, fim_iso)
    """

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
        (
            id, func_id, nome, sap, dias, abono,
            inicio_iso, fim_iso,
            folga_atual_iso, folga_proximo_iso
        ) = row

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


# ============================================================================
# SOMA DE DIAS DE FÉRIAS DO FUNCIONÁRIO
# ============================================================================
def total_dias_ferias(funcionario_id):
    """
    Soma todos os dias de férias já tirados pelo funcionário.

    Serve para impedir que ultrapasse o limite de 30 dias.

    Retorna:
        int: total de dias já registrados.
    """

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


# ============================================================================
# VERIFICAR SOBREPOSIÇÃO DE FÉRIAS
# ============================================================================
def existe_sobreposicao(funcionario_id, inicio, fim, ignorar_ferias_id=None):
    """
    Verifica se um período de férias se sobrepõe a outro já cadastrado.

    Lógica:
        Sobrepõe quando:
            data_inicio <= fim_novo  AND
            data_fim >= inicio_novo

    Parâmetros:
        funcionario_id (int)
        inicio (str)  → formato ISO (yyyy-mm-dd)
        fim (str)
        ignorar_ferias_id (int) → usado em atualizações

    Retorna:
        bool: True se houver conflito, False caso contrário.
    """

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


# ============================================================================
# ADICIONAR NOVO PERÍODO DE FÉRIAS
# ============================================================================
def adicionar_ferias(funcionario_id, agendado_sap, periodo_dias,
                     abono_peculiario, data_inicio, data_fim, cor):
    """
    Insere um novo período de férias no banco.

    Parâmetros:
        funcionario_id (int)
        agendado_sap (str: 'sim' ou 'não')
        periodo_dias (int)
        abono_peculiario (str)
        data_inicio (str ISO)
        data_fim (str ISO)
        cor (str): cor usada no gráfico Gantt
    """

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


# ============================================================================
# REMOVER PERÍODO DE FÉRIAS
# ============================================================================
def deletar_ferias(ferias_id):
    """
    Deleta um registro de férias do banco.

    Parâmetros:
        ferias_id (int)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ferias WHERE id = ?;", (ferias_id,))
    conn.commit()
    conn.close()


# ============================================================================
# ATUALIZAR PERÍODO DE FÉRIAS EXISTENTE
# ============================================================================
def atualizar_ferias(ferias_id, agendado_sap, periodo_dias,
                     abono_peculiario, data_inicio, data_fim, cor):
    """
    Atualiza os dados de um período de férias.

    Parâmetros:
        ferias_id (int)
        agendado_sap (str)
        periodo_dias (int)
        abono_peculiario (str)
        data_inicio (str)
        data_fim (str)
        cor (str)
    """

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


# ============================================================================
# FILTRO AVANÇADO (USADO NA TELA PRINCIPAL / AJAX)
# ============================================================================
def filtrar_ferias_service(funcionario_id, ano, mes, abono, sap):
    """
    Aplica filtros dinâmicos nas férias para exibição no frontend.

    Filtros suportados:
        funcionário
        ano
        mês
        abono pecuniário
        agendado no SAP

    Retorna:
        lista de objetos JSON serializáveis.
    """

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


# ============================================================================
# LISTAR PERÍODOS PARA GANTT
# ============================================================================
def listar_periodos_para_gantt():
    """
    Retorna apenas os dados necessários para montar o gráfico Gantt:
        - Nome do funcionário
        - Data de início
        - Data de fim

    O gráfico não precisa de detalhes como SAP, abono, cor etc.

    Retorna:
        list[tuple]: [(nome, inicio_iso, fim_iso), ...]
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT func.nome, f.data_inicio, f.data_fim
        FROM ferias f
        JOIN funcionarios func ON func.id = f.funcionario_id
        ORDER BY func.nome, f.data_inicio
    """)

    dados = cursor.fetchall()
    conn.close()

    lista = []
    for nome, inicio, fim in dados:
        lista.append((nome, inicio, fim))

    return lista
