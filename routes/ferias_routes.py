from flask import Blueprint, render_template, request, redirect, url_for
from services.funcionario_service import listar_funcionarios
from services.ferias_service import adicionar_ferias, listar_ferias
from datetime import datetime

ferias_bp = Blueprint("ferias", __name__)

@ferias_bp.route("/")
def pagina_inicial():
    funcionarios = listar_funcionarios()
    ferias = listar_ferias()

    ano_atual = datetime.now().year
    ano_proximo = ano_atual + 1    

    return render_template(
        "index.html",
        funcionarios=funcionarios,
        ferias=ferias,
        ano_atual=ano_atual,
        ano_proximo=ano_proximo
    )


@ferias_bp.route("/adicionar-ferias", methods=["POST"])
def route_adicionar_ferias():
    funcionario_id = request.form.get("funcionario_id")
    agendado_sap = request.form.get("agendado_sap")
    periodo_dias = request.form.get("periodo_dias")
    abono_peculiario = request.form.get("abono_peculiario")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")
    folga_ano_anterior = request.form.get("folga_ano_anterior")
    folga_ano = request.form.get("folga_ano")

    adicionar_ferias(
        funcionario_id,
        agendado_sap,
        periodo_dias,
        abono_peculiario,
        inicio,
        fim,
        folga_ano_anterior,
        folga_ano,
        cor="#4CAF50"  # temporário
    )

    return redirect(url_for("ferias.pagina_inicial"))
