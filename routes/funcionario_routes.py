"""
funcionario_routes.py
---------------------
Módulo responsável pelo CRUD de funcionários no sistema.

Funcionalidades implementadas:
- Exibir lista de funcionários
- Adicionar novo funcionário
- Buscar funcionário por ID (útil para popups e edições dinâmicas)
- Atualizar informações de um funcionário
- Excluir funcionário

Este módulo utiliza o serviço `funcionario_service.py` para executar
operações diretamente no banco de dados.
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from services.funcionario_service import (
    listar_funcionarios,
    adicionar_funcionario,
    obter_funcionario_por_id,
    atualizar_funcionario,
    deletar_funcionario
)

# Blueprint dedicado às rotas de funcionários
funcionario_bp = Blueprint("funcionario", __name__)


# ============================================================================
# PÁGINA PRINCIPAL DO CRUD DE FUNCIONÁRIOS
# ============================================================================
@funcionario_bp.route("/funcionarios")
def pagina_funcionarios():
    """
    Exibe a página principal com a lista de funcionários cadastrados.

    Lê os dados via `listar_funcionarios()` e envia para o template
    `funcionarios.html`.

    Returns:
        HTML renderizado com a tabela de funcionários.
    """
    funcionarios = listar_funcionarios()
    return render_template("funcionarios.html", funcionarios=funcionarios)


# ============================================================================
# ADICIONAR FUNCIONÁRIO
# ============================================================================
@funcionario_bp.route("/adicionar-funcionario", methods=["POST"])
def route_adicionar_funcionario():
    """
    Recebe o nome do funcionário via formulário e adiciona no banco.

    Parâmetro esperado (POST):
        nome: nome do funcionário

    Caso o nome esteja preenchido, chama `adicionar_funcionario()`.
    Em seguida, redireciona para a página principal do CRUD.
    """

    nome = request.form.get("nome")

    if nome:
        adicionar_funcionario(nome)

    return redirect(url_for("funcionario.pagina_funcionarios"))


# ============================================================================
# BUSCAR FUNCIONÁRIO (para popup/edição dinâmica)
# ============================================================================
@funcionario_bp.route("/buscar-funcionario/<int:func_id>")
def route_buscar_funcionario(func_id):
    """
    Retorna os dados de um funcionário específico em formato JSON.

    Usado para:
        - Popups de edição
        - Formulários dinâmicos via AJAX

    Parâmetro:
        func_id (int): ID do funcionário desejado.

    Retorna:
        JSON com {id, nome} ou erro 404 caso não exista.
    """

    func = obter_funcionario_por_id(func_id)

    if func is None:
        return jsonify({"erro": "Funcionário não encontrado"}), 404

    return jsonify({"id": func[0], "nome": func[1]})


# ============================================================================
# ATUALIZAR FUNCIONÁRIO
# ============================================================================
@funcionario_bp.route("/atualizar-funcionario/<int:func_id>", methods=["POST"])
def route_atualizar_funcionario(func_id):
    """
    Atualiza o nome de um funcionário existente.

    Parâmetros esperados (POST):
        nome — novo nome a ser atribuído

    Caso exista novo nome, chama `atualizar_funcionario()`.

    Após isso, redireciona o usuário para a página principal do CRUD.
    """

    novo_nome = request.form.get("nome")

    if novo_nome:
        atualizar_funcionario(func_id, novo_nome)

    return redirect(url_for("funcionario.pagina_funcionarios"))


# ============================================================================
# DELETAR FUNCIONÁRIO
# ============================================================================
@funcionario_bp.route("/deletar-funcionario/<int:func_id>")
def route_deletar_funcionario(func_id):
    """
    Remove um funcionário do banco de dados.

    Parâmetro:
        func_id (int): ID do funcionário a ser excluído.

    Após exclusão, redireciona novamente para a página de listagem.
    """

    deletar_funcionario(func_id)
    return redirect(url_for("funcionario.pagina_funcionarios"))
