from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from services.funcionario_service import (
    listar_funcionarios,
    adicionar_funcionario,
    obter_funcionario_por_id,
    atualizar_funcionario,
    deletar_funcionario
)

funcionario_bp = Blueprint("funcionario", __name__)


# ========================================
# PÁGINA PRINCIPAL DO CRUD DE FUNCIONÁRIOS
# ========================================
@funcionario_bp.route("/funcionarios")
def pagina_funcionarios():
    funcionarios = listar_funcionarios()
    return render_template("funcionarios.html", funcionarios=funcionarios)


# ========================================
# ADICIONAR FUNCIONÁRIO
# ========================================
@funcionario_bp.route("/adicionar-funcionario", methods=["POST"])
def route_adicionar_funcionario():
    nome = request.form.get("nome")

    if nome:
        adicionar_funcionario(nome)

    return redirect(url_for("funcionario.pagina_funcionarios"))


# ========================================
# BUSCAR FUNCIONÁRIO (para popup)
# ========================================
@funcionario_bp.route("/buscar-funcionario/<int:func_id>")
def route_buscar_funcionario(func_id):
    func = obter_funcionario_por_id(func_id)

    if func is None:
        return jsonify({"erro": "Funcionário não encontrado"}), 404

    return jsonify({"id": func[0], "nome": func[1]})


# ========================================
# ATUALIZAR FUNCIONÁRIO
# ========================================
@funcionario_bp.route("/atualizar-funcionario/<int:func_id>", methods=["POST"])
def route_atualizar_funcionario(func_id):
    novo_nome = request.form.get("nome")

    if novo_nome:
        atualizar_funcionario(func_id, novo_nome)

    return redirect(url_for("funcionario.pagina_funcionarios"))


# ========================================
# DELETAR FUNCIONÁRIO
# ========================================
@funcionario_bp.route("/deletar-funcionario/<int:func_id>")
def route_deletar_funcionario(func_id):
    deletar_funcionario(func_id)
    return redirect(url_for("funcionario.pagina_funcionarios"))
