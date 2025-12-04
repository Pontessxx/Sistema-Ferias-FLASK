from flask import Flask, render_template
from database import create_database
from routes.funcionario_routes import funcionario_bp

app = Flask(__name__)

# Criar banco ao iniciar
create_database()

# Registrar rotas
app.register_blueprint(funcionario_bp)

# === ROTA PRINCIPAL ===
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
