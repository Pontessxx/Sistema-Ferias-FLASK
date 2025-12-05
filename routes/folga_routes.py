from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from services.folga_service import (
    obter_folga,
    adicionar_folga,
    atualizar_folga,
    deletar_folga,
    listar_folgas
)
from services.funcionario_service import listar_funcionarios
from datetime import datetime

folga_bp = Blueprint("folga", __name__)


# Página nova
@folga_bp.route("/abono-folga")
def pagina_abono_folga():
    funcionarios = listar_funcionarios()
    folgas = listar_folgas()

    ano_atual = datetime.now().year
    ano_proximo = ano_atual + 1

    return render_template(
        "abono-folga.html",
        funcionarios=funcionarios,
        folgas=folgas,
        ano_atual=ano_atual,
        ano_proximo=ano_proximo
    )


# Buscar folga
@folga_bp.route("/buscar-folga", methods=["POST"])
def route_buscar_folga():
    funcionario_id = request.form.get("funcionario_id")
    ano = request.form.get("ano")

    folga = obter_folga(funcionario_id, ano)

    if folga:
        return jsonify({
            "id": folga[0],
            "data": folga[1]
        })

    return jsonify({"id": None})


# Adicionar folga
@folga_bp.route("/adicionar-folga", methods=["POST"])
def route_adicionar_folga():
    funcionario_id = request.form.get("funcionario_folga_id")
    ano = request.form.get("ano")
    data = request.form.get("data_folga")

    adicionar_folga(funcionario_id, ano, data)

    return redirect(url_for("folga.pagina_abono_folga"))


# Atualizar folga
@folga_bp.route("/atualizar-folga/<int:folga_id>", methods=["POST"])
def route_atualizar_folga(folga_id):
    nova_data = request.form.get("data_folga")
    atualizar_folga(folga_id, nova_data)

    return redirect(url_for("folga.pagina_abono_folga"))


# Deletar folga
@folga_bp.route("/deletar-folga/<int:folga_id>")
def route_deletar_folga(folga_id):
    deletar_folga(folga_id)
    return redirect(url_for("folga.pagina_abono_folga"))
