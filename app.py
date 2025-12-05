from flask import Flask, render_template
from database import create_database
from routes.funcionario_routes import funcionario_bp
from routes.ferias_routes import ferias_bp
from routes.folga_routes import folga_bp
from routes.gantt_routes import gantt_bp

app = Flask(__name__)

create_database()

# Registrar rotas
app.register_blueprint(funcionario_bp)
app.register_blueprint(ferias_bp)
app.register_blueprint(folga_bp)
app.register_blueprint(gantt_bp)

# Rota principal opcional — vamos REDIRECIONAR para o blueprint correto
@app.route("/")
def home():
    from datetime import datetime
    ano_atual = datetime.now().year
    ano_proximo = ano_atual + 1

    return render_template(
        "index.html",
        funcionarios=[],
        ferias=[],
        ano_atual=ano_atual,
        ano_proximo=ano_proximo
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=8000)

