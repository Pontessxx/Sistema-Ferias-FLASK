from flask import Blueprint, render_template
from services.ferias_service import listar_periodos_para_gantt
from services.folga_service import listar_folgas
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import holidays

gantt_bp = Blueprint("gantt", __name__)

def obter_feriados():

    ano_atual = dt.datetime.now().year
    ano_prox = ano_atual + 1

    # feriados nacionais + estaduais SP
    feriados = holidays.Brazil(
        years=[ano_atual, ano_prox],
        state="SP",
        language="pt_BR"
    )

    resultado = {}

    # ======== ADICIONAR FERIADOS MUNICIPAIS DE OSASCO ========
    resultado[f"{ano_atual}-02-19"] = "Aniversário de Osasco"
    resultado[f"{ano_prox}-02-19"] = "Aniversário de Osasco"

    # ======== ADICIONAR FERIADOS MÓVEIS QUE A LIBRARY NÃO TRAZ ========
    for ano in [ano_atual, ano_prox]:
        # === Carnaval (terça-feira) ===
        for nome_variacao in ["Carnaval", "Carnaval (ponto facultativo)"]:
            try:
                datas = holidays.Brazil(years=[ano]).get_named(nome_variacao)
                if datas:
                    resultado[datas[0].strftime("%Y-%m-%d")] = "Carnaval"
                    break
            except:
                pass

        # === Corpus Christi ===
        for nome_variacao in ["Corpus Christi", "Corpus-Christi"]:
            try:
                datas = holidays.Brazil(years=[ano]).get_named(nome_variacao)
                if datas:
                    resultado[datas[0].strftime("%Y-%m-%d")] = "Corpus Christi"
                    break
            except:
                pass


        # Santo Antônio (municipal)
        resultado[f"{ano}-06-13"] = "Santo Antônio"

    # ======== ADICIONAR OS FERIADOS DA LIBRARIES =========
    for data, nome in feriados.items():
        if isinstance(data, dt.date):
            resultado[data.strftime("%Y-%m-%d")] = nome

    return resultado



@gantt_bp.route("/gantt")
def pagina_gantt():
    dados = listar_periodos_para_gantt()
    folgas = listar_folgas()
    feriados = obter_feriados()

    tasks = []

    # Férias
    for nome, inicio, fim in dados:
        tasks.append({
            "Funcionário": nome,
            "Inicio": inicio,
            "Fim": fim,
            "Tipo": "Férias"
        })

    # Folgas
    for f in folgas:
        nome = f["nome"]
        data = f["data_folga"]
        dt_inicio = dt.datetime.strptime(data, "%Y-%m-%d")
        dt_fim = dt_inicio + dt.timedelta(days=1)

        tasks.append({
            "Funcionário": nome,
            "Inicio": dt_inicio.strftime("%Y-%m-%d"),
            "Fim": dt_fim.strftime("%Y-%m-%d"),
            "Tipo": "Folga"
        })

    if not tasks:
        return render_template("gantt.html",
                               grafico_html="<h3>Sem dados</h3>",
                               feriados={})

    # Criar o Gantt
    fig = px.timeline(
        tasks,
        x_start="Inicio",
        x_end="Fim",
        color="Tipo",
        color_discrete_map={
            "Férias": "rgb(0,102,204)",
            "Folga": "rgb(255,140,0)"
        },
        y="Funcionário",
    )

    fig.update_yaxes(autorange="reversed", tickfont=dict(size=18))
    # fig.update_yaxes(title=None)

    # SHAPES dos feriados
    shapes = []

    for data, nome in feriados.items():
        dt_data = dt.datetime.strptime(data, "%Y-%m-%d")

        shapes.append({
            "type": "line",
            "x0": dt_data,
            "x1": dt_data,
            "y0": -0.5,
            "y1": len(tasks) - 0.5,
            "line": {"color": "red", "width": 2, "dash": "dot"},
            "xref": "x",
            "yref": "y"
        })

    # finais de semana
    ano = dt.datetime.now().year
    inicio = dt.datetime(ano, 1, 1)
    fim = dt.datetime(ano + 1, 12, 31)

    for i in range((fim - inicio).days):
        dia = inicio + dt.timedelta(days=i)

        if dia.weekday() in (5, 6):
            shapes.append({
                "type": "rect",
                "x0": dia,
                "x1": dia + dt.timedelta(days=1),
                "y0": -0.5,
                "y1": len(tasks) - 0.5,
                "fillcolor": "rgba(200,200,200,0.5)",
                "line": {"width": 0},
                "layer": "below", # colocar atrás das barras
            })
    fig.update_layout(
        shapes=shapes,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    # === LEGENDA: FERIADOS ===
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="lines",
        line=dict(color="red", width=2, dash="dot"),
        name="Feriados"
    ))

    # === LEGENDA: SÁBADOS E DOMINGOS ===
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(size=15, color="rgba(200,200,200,0.6)"),
        name="Sábados e Domingos"
    ))


    grafico_html = fig.to_html(full_html=False)

    ano_atual = dt.datetime.now().year
    ano_prox = ano_atual + 1
    # Filtra somente feriados do ano atual
    feriados_filtrados = {
        data: nome
        for data, nome in feriados.items()
        if data.startswith(str(ano_prox))
    }

    # Ordena por mês e dia
    feriados_ordenados = dict(
        sorted(
            feriados_filtrados.items(),
            key=lambda x: (int(x[0][5:7]), int(x[0][8:10]))
        )
    )



    return render_template("gantt.html",
                           grafico_html=grafico_html,
                           feriados=feriados_ordenados)
