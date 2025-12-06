"""
app.py
------
Arquivo principal da aplicação Flask responsável por:

- Inicializar a aplicação
- Criar o banco de dados caso não exista
- Registrar todos os Blueprints (funcionários, férias, folga, gráfico Gantt)
- Renderizar a página inicial
- Executar o servidor web

Este módulo é o ponto de entrada do sistema.
"""

from flask import Flask, render_template
from database import create_database
import logging

# Importação das rotas (Blueprints)
from routes.funcionario_routes import funcionario_bp
from routes.ferias_routes import ferias_bp
from routes.folga_routes import folga_bp
from routes.gantt_routes import gantt_bp

# ===============================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ===============================================================
app = Flask(__name__)

# Cria estrutura do banco de dados na primeira execução
create_database()

# ===============================================================
# REGISTRO DOS BLUEPRINTS
# Cada módulo de rotas é isolado e modularizado
# ===============================================================
app.register_blueprint(funcionario_bp)
app.register_blueprint(ferias_bp)
app.register_blueprint(folga_bp)
app.register_blueprint(gantt_bp)

# ===============================================================
# ROTA PRINCIPAL
# - Exibe a página inicial
# - Passa valores padrão (listas vazias) para evitar erros
# - Poderia futuramente redirecionar para /ferias ou outro dashboard
# ===============================================================
@app.route("/")
def home():
    """
    Renderiza a página inicial do sistema.

    A página de férias utiliza valores fornecidos via backend.
    Como esta rota é apenas uma tela inicial e não uma listagem real,
    os dados são enviados vazios para evitar carga desnecessária.
    """
    from datetime import datetime

    ano_atual = datetime.now().year
    ano_proximo = ano_atual + 1

    return render_template(
        "index.html",
        funcionarios=[],   # lista vazia (não carrega dados reais aqui)
        ferias=[],         # tabela vazia
        ano_atual=ano_atual,
        ano_proximo=ano_proximo
    )

# ===============================================================
# EXECUÇÃO DO SERVIDOR DE DESENVOLVIMENTO
# - debug=True: facilita rastrear erros
# - use_reloader=False: evita duplicação de processos no Windows
# - host 0.0.0.0: permite acesso na rede local
# - porta 8000: porta personalizada do sistema
# ===============================================================
# Desliga o logger padrão do werkzeug (essas linhas de GET/POST)
logging.getLogger("werkzeug").disabled = True
if __name__ == "__main__":



    print("\n========================================")
    print("  🚀 Sistema de Escala de Férias")
    print("  ▶ Servidor rodando em: http://127.0.0.1:8000")
    print("  ▶ Acesse /gantt para ver o gráfico")
    print("  ▶ Pressione CTRL+C para encerrar")
    print("========================================\n")
    app.run(debug=False, host="0.0.0.0", port=8000)
