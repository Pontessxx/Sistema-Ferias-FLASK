"""
ferias_routes.py
----------------
Blueprint responsável por todas as rotas relacionadas ao gerenciamento de férias.

Funcionalidades implementadas:
- Carregamento da página inicial com dados de funcionários e períodos de férias.
- Cadastro de novos períodos de férias com validações.
- Atualização de registros existentes.
- Exclusão de férias.
- Filtros dinâmicos via AJAX.
- Consulta de saldo restante de dias por funcionário.

Este arquivo conversa diretamente com `ferias_service.py` e `funcionario_service.py`,
que executam a lógica de banco de dados.
"""

from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from services.funcionario_service import listar_funcionarios
from services.ferias_service import (
    adicionar_ferias,
    listar_ferias,
    atualizar_ferias,
    deletar_ferias,
    total_dias_ferias,
    existe_sobreposicao
)
from datetime import datetime

# Blueprint principal das rotas de férias
ferias_bp = Blueprint("ferias", __name__)


# ============================================================================
# PÁGINA INICIAL DO SISTEMA (Dashboard)
# ============================================================================
@ferias_bp.route("/")
def pagina_inicial():
    """
    Renderiza a página inicial do sistema, preenchendo:

    - Ano atual e próximo ano (para filtros e validação)
    - Lista de funcionários com saldo restante de férias
    - Todos os períodos de férias cadastrados

    O saldo é calculado como:
        saldo = 30 - total_dias_ferias(funcionario_id)
    """

    ano_atual = datetime.now().year
    ano_proximo = ano_atual + 1

    # Lista todos os funcionários e calcula saldo individual
    funcionarios = listar_funcionarios()
    ferias = listar_ferias(ano_atual, ano_proximo)

    funcionarios_saldo = []
    for f in funcionarios:
        saldo = 30 - total_dias_ferias(f[0])
        funcionarios_saldo.append((f[0], f[1], saldo))

    # Renderiza o index.html com dados consolidados
    return render_template(
        "index.html",
        funcionarios=funcionarios_saldo,
        ferias=ferias,
        ano_atual=ano_atual,
        ano_proximo=ano_proximo
    )


# ============================================================================
# ADICIONAR NOVO PERÍODO DE FÉRIAS
# ============================================================================
@ferias_bp.route("/adicionar-ferias", methods=["POST"])
def route_adicionar_ferias():
    """
    Processa o envio do formulário para cadastrar um novo período de férias.

    Validações aplicadas:
    - Data final >= data inicial
    - Funcionário não pode ultrapassar 30 dias no ano
    - Não pode haver sobreposição de períodos já cadastrados

    Após validação, insere o registro no banco chamando `adicionar_ferias()`.
    """

    funcionario_id = request.form.get("funcionario_id")
    agendado_sap = request.form.get("agendado_sap")
    abono = request.form.get("abono_peculiario")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")

    # Converte datas e calcula quantidade de dias
    data_i = datetime.strptime(inicio, "%Y-%m-%d")
    data_f = datetime.strptime(fim, "%Y-%m-%d")
    dias_novos = (data_f - data_i).days + 1

    if dias_novos < 1:
        return "Erro: a data final deve ser igual ou posterior à data inicial!"

    dias_ja = total_dias_ferias(funcionario_id)

    # Impede ultrapassar 30 dias no ano
    if dias_ja + dias_novos > 30:
        return f"Erro: funcionário já tirou {dias_ja} dias. Somando {dias_novos}, ultrapassa 30."

    # Impede sobreposição de datas
    if existe_sobreposicao(funcionario_id, inicio, fim):
        return "Erro: já existe férias cadastrada que se sobrepõe a este período."

    # Inserção no banco
    adicionar_ferias(
        funcionario_id,
        agendado_sap,
        dias_novos,
        abono,
        inicio,
        fim,
        cor="#4CAF50"
    )

    return redirect(url_for("ferias.pagina_inicial"))


# ============================================================================
# ATUALIZAR FÉRIAS EXISTENTES
# ============================================================================
@ferias_bp.route("/atualizar-ferias/<int:ferias_id>", methods=["POST"])
def route_atualizar_ferias(ferias_id):
    """
    Atualiza um registro de férias existente.

    Validações aplicadas:
    - Impede sobreposição com outros períodos do mesmo funcionário
    - Recalcula quantidade de dias
    - Atualiza valores de SAP, abono, datas e cor

    Obs.:
    `existe_sobreposicao()` recebe o parâmetro `ignorar_ferias_id` para permitir
    atualização sem comparar o registro consigo mesmo.
    """

    funcionario_id = request.form.get("funcionario_id")
    agendado_sap = request.form.get("agendado_sap")
    abono = request.form.get("abono_peculiario")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")

    # Validação de sobreposição ignorando o próprio registro atualizado
    if existe_sobreposicao(funcionario_id, inicio, fim, ignorar_ferias_id=ferias_id):
        return "Erro: já existe férias cadastrada que se sobrepõe a este período."

    # Converte datas e recalcula dias
    data_i = datetime.strptime(inicio, "%Y-%m-%d")
    data_f = datetime.strptime(fim, "%Y-%m-%d")
    dias_novos = (data_f - data_i).days + 1

    atualizar_ferias(
        ferias_id,
        agendado_sap,
        dias_novos,
        abono,
        inicio,
        fim,
        cor="#4CAF50"
    )

    return redirect(url_for("ferias.pagina_inicial"))


# ============================================================================
# DELETAR FÉRIAS
# ============================================================================
@ferias_bp.route("/deletar-ferias/<int:ferias_id>")
def route_deletar_ferias(ferias_id):
    """
    Remove um registro de férias da base de dados.

    Parâmetro:
        ferias_id (int): id do registro a ser removido.
    """
    deletar_ferias(ferias_id)
    return redirect(url_for("ferias.pagina_inicial"))


# ============================================================================
# FILTRO AVANÇADO DE FÉRIAS (AJAX)
# ============================================================================
@ferias_bp.route("/filtrar-ferias", methods=["POST"])
def filtrar_ferias():
    """
    Executa filtro dinâmico de férias com base nos parâmetros enviados via formulário.

    Parâmetros esperados:
        funcionario_id : id do funcionário
        ano            : ano desejado
        mes            : mês desejado
        abono          : filtro opcional por abono pecuniário
        sap            : filtro por agendado no SAP

    Retorna JSON contendo os registros filtrados.
    """
    funcionario_id = request.form.get("funcionario_id")
    ano = request.form.get("ano")
    mes = request.form.get("mes")
    abono = request.form.get("abono")
    sap = request.form.get("sap")

    from services.ferias_service import filtrar_ferias_service
    dados = filtrar_ferias_service(funcionario_id, ano, mes, abono, sap)

    return jsonify(dados)


# ============================================================================
# CONSULTAR SALDO DE DIAS RESTANTES
# ============================================================================
@ferias_bp.route("/saldo/<int:func_id>")
def pegar_saldo(func_id):
    """
    Retorna o saldo de férias restantes do funcionário.

    Cálculo:
        saldo = 30 - total_dias_ferias(func_id)

    Retorna:
        {"saldo": <valor>}
    """
    saldo = 30 - total_dias_ferias(func_id)
    return jsonify({"saldo": saldo})
