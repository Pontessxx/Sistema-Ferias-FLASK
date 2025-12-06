"""
folga_routes.py
----------------
Módulo responsável pelas rotas relacionadas ao cadastro e gerenciamento das
folgas por assiduidade dos funcionários.

Funcionalidades:
- Página principal de visualização e cadastro de folgas.
- Busca de folga por funcionário e ano.
- Inserção de nova folga.
- Atualização de folga já existente.
- Exclusão de folga.

Este módulo utiliza o `folga_service.py` para operações de banco de dados e
`funcionario_service.py` para carregar informações dos colaboradores.
"""

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

# Blueprint para rotas relacionadas às folgas
folga_bp = Blueprint("folga", __name__)


# ============================================================================
# PÁGINA PRINCIPAL (Abono e Folga de Assiduidade)
# ============================================================================
@folga_bp.route("/abono-folga")
def pagina_abono_folga():
    """
    Renderiza a página principal para gerenciamento de folga por assiduidade.

    A página exibe:
    - Lista de funcionários
    - Lista de folgas registradas
    - Ano atual e próximo ano para seleção

    Returns:
        HTML renderizado com dados consolidados.
    """

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


# ============================================================================
# BUSCAR FOLGA POR FUNCIONÁRIO E ANO
# ============================================================================
@folga_bp.route("/buscar-folga", methods=["POST"])
def route_buscar_folga():
    """
    Busca se existe uma folga cadastrada para o funcionário em um determinado ano.

    Parâmetros esperados (via formulário POST):
        - funcionario_id : ID do funcionário
        - ano            : Ano desejado

    Retorna:
        JSON:
        - {"id": <id da folga>, "data": <data da folga>}
        - {"id": None} quando não existe folga registrada
    """

    funcionario_id = request.form.get("funcionario_id")
    ano = request.form.get("ano")

    folga = obter_folga(funcionario_id, ano)

    if folga:
        return jsonify({
            "id": folga[0],   # ID do registro
            "data": folga[1]  # Data da folga
        })

    return jsonify({"id": None})


# ============================================================================
# ADICIONAR NOVA FOLGA
# ============================================================================
@folga_bp.route("/adicionar-folga", methods=["POST"])
def route_adicionar_folga():
    """
    Cadastra uma nova folga por assiduidade.

    Parâmetros esperados (via formulário):
        - funcionario_folga_id : ID do funcionário
        - ano                  : Ano da concessão da folga
        - data_folga           : Data da folga

    Após inserir, redireciona o usuário para a página principal.
    """

    funcionario_id = request.form.get("funcionario_folga_id")
    ano = request.form.get("ano")
    data = request.form.get("data_folga")

    adicionar_folga(funcionario_id, ano, data)

    return redirect(url_for("folga.pagina_abono_folga"))


# ============================================================================
# ATUALIZAR UMA FOLGA EXISTENTE
# ============================================================================
@folga_bp.route("/atualizar-folga/<int:folga_id>", methods=["POST"])
def route_atualizar_folga(folga_id):
    """
    Atualiza a data de uma folga existente.

    Parâmetros:
        folga_id (int): ID da folga a ser atualizada.
        nova_data     : nova data informada no formulário.

    Após atualizar, redireciona o usuário para a página principal.
    """

    nova_data = request.form.get("data_folga")
    atualizar_folga(folga_id, nova_data)

    return redirect(url_for("folga.pagina_abono_folga"))


# ============================================================================
# DELETAR FOLGA
# ============================================================================
@folga_bp.route("/deletar-folga/<int:folga_id>")
def route_deletar_folga(folga_id):
    """
    Remove um registro de folga do banco de dados.

    Parâmetro:
        folga_id (int): identificação do registro a ser apagado.

    Redireciona novamente para a tela principal.
    """

    deletar_folga(folga_id)
    return redirect(url_for("folga.pagina_abono_folga"))
