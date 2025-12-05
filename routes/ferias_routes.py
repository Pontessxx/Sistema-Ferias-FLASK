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

ferias_bp = Blueprint("ferias", __name__)

# =======================================
# PÁGINA INICIAL
# =======================================
@ferias_bp.route("/")
def pagina_inicial():
    ano_atual = datetime.now().year
    ano_proximo = ano_atual + 1

    funcionarios = listar_funcionarios()
    ferias = listar_ferias(ano_atual, ano_proximo)

    funcionarios_saldo = []
    for f in funcionarios:
        saldo = 30 - total_dias_ferias(f[0])
        funcionarios_saldo.append((f[0], f[1], saldo))

    return render_template(
        "index.html",
        funcionarios=funcionarios_saldo,
        ferias=ferias,
        ano_atual=ano_atual,
        ano_proximo=ano_proximo
    )


# =======================================
# ADICIONAR FÉRIAS
# =======================================
@ferias_bp.route("/adicionar-ferias", methods=["POST"])
def route_adicionar_ferias():
    funcionario_id = request.form.get("funcionario_id")
    agendado_sap = request.form.get("agendado_sap")
    abono = request.form.get("abono_peculiario")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")

    data_i = datetime.strptime(inicio, "%Y-%m-%d")
    data_f = datetime.strptime(fim, "%Y-%m-%d")
    dias_novos = (data_f - data_i).days + 1

    if dias_novos < 1:
        return "Erro: a data final deve ser igual ou posterior à data inicial!"

    dias_ja = total_dias_ferias(funcionario_id)

    if dias_ja + dias_novos > 30:
        return f"Erro: funcionário já tirou {dias_ja} dias. Somando {dias_novos}, ultrapassa 30."

    if existe_sobreposicao(funcionario_id, inicio, fim):
        return "Erro: já existe férias cadastrada que se sobrepõe a este período."

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


# =======================================
# ATUALIZAR FÉRIAS
# =======================================
@ferias_bp.route("/atualizar-ferias/<int:ferias_id>", methods=["POST"])
def route_atualizar_ferias(ferias_id):
    funcionario_id = request.form.get("funcionario_id")
    agendado_sap = request.form.get("agendado_sap")
    abono = request.form.get("abono_peculiario")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")

    if existe_sobreposicao(funcionario_id, inicio, fim, ignorar_ferias_id=ferias_id):
        return "Erro: já existe férias cadastrada que se sobrepõe a este período."

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


# =======================================
# DELETAR FÉRIAS
# =======================================
@ferias_bp.route("/deletar-ferias/<int:ferias_id>")
def route_deletar_ferias(ferias_id):
    deletar_ferias(ferias_id)
    return redirect(url_for("ferias.pagina_inicial"))


@ferias_bp.route("/filtrar-ferias", methods=["POST"])
def filtrar_ferias():
    funcionario_id = request.form.get("funcionario_id")
    ano = request.form.get("ano")
    mes = request.form.get("mes")
    abono = request.form.get("abono")
    sap = request.form.get("sap")

    from services.ferias_service import filtrar_ferias_service
    dados = filtrar_ferias_service(funcionario_id, ano, mes, abono, sap)

    return jsonify(dados)

@ferias_bp.route("/saldo/<int:func_id>")
def pegar_saldo(func_id):
    saldo = 30 - total_dias_ferias(func_id)
    return jsonify({"saldo": saldo})
