from flask import Blueprint, request, jsonify, redirect, url_for
from services.folga_service import (
    obter_folga,
    adicionar_folga,
    atualizar_folga,
    deletar_folga
)

folga_bp = Blueprint("folga", __name__)

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


@folga_bp.route("/adicionar-folga", methods=["POST"])
def route_adicionar_folga():
    funcionario_id = request.form.get("funcionario_folga_id")
    ano = request.form.get("ano")
    data = request.form.get("data_folga")
    adicionar_folga(funcionario_id, ano, data)
    return redirect(url_for("ferias.pagina_inicial"))


@folga_bp.route("/atualizar-folga/<int:folga_id>", methods=["POST"])
def route_atualizar_folga(folga_id):
    nova_data = request.form.get("data_folga")
    atualizar_folga(folga_id, nova_data)
    return redirect(url_for("ferias.pagina_inicial"))


@folga_bp.route("/deletar-folga/<int:folga_id>")
def route_deletar_folga(folga_id):
    deletar_folga(folga_id)
    return redirect(url_for("ferias.pagina_inicial"))
