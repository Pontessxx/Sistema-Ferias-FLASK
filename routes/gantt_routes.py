from flask import Blueprint, render_template
from services.ferias_service import listar_periodos_para_gantt
from services.folga_service import listar_folgas
import plotly.figure_factory as ff
import datetime as dt
import holidays

gantt_bp = Blueprint("gantt", __name__)


# ============================================================
#   FUNÇÃO PARA OBTER FERIADOS DO ANO ATUAL E PRÓXIMO
# ============================================================
def obter_feriados():
    ano_atual = dt.datetime.now().year
    ano_proximo = ano_atual + 1

    feriados = holidays.Brazil(
        years=[ano_atual, ano_proximo],
        state="SP",
        language="pt_BR"
    )

    feriados_osasco = {
        f"{ano_atual}-02-19": "Aniversário de Osasco",
        f"{ano_proximo}-02-19": "Aniversário de Osasco"
    }

    all_feriados = {str(data): nome for data, nome in feriados.items()}
    all_feriados.update(feriados_osasco)

    return all_feriados



# ============================================================
#   ROTA DO GANTT
# ============================================================
@gantt_bp.route("/gantt")
def pagina_gantt():
    dados = listar_periodos_para_gantt()
    folgas = listar_folgas()
    feriados = obter_feriados()

    tasks = []

    # ============================================================
    #   FÉRIAS  (AZUL)
    # ============================================================
    for nome, inicio, fim in dados:
        tasks.append(dict(
            Task=nome,
            Start=inicio,
            Finish=fim,
            Resource="Férias"
        ))

    # ============================================================
    #   FOLGAS (1 DIA – LARANJA)
    # ============================================================
    for f in folgas:
        nome = f["nome"]
        data = f["data_folga"]

        inicio = data
        fim = (dt.datetime.strptime(data, "%Y-%m-%d") + dt.timedelta(days=1)).strftime("%Y-%m-%d")

        tasks.append(dict(
            Task=nome,
            Start=inicio,
            Finish=fim,
            Resource="Folga"
        ))

    # ============================================================
    #   CRIAR O GANTT COM CORES FIXAS
    # ============================================================
    fig = ff.create_gantt(
        tasks,
        index_col="Resource",
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        height=650,
          colors={
            "Férias": "rgb(0, 102, 204)",   # azul forte
            "Folga": "rgb(255, 140, 0)"     # laranja
        }
    )

    # ============================================================
    #   INSERIR LINHAS DOS FERIADOS
    # ============================================================
    shapes = list(fig['layout'].shapes or [])

    for data, descricao in feriados.items():
        d = dt.datetime.strptime(data, "%Y-%m-%d")

        shapes.append({
            "type": "line",
            "x0": d,
            "y0": -1,
            "x1": d,
            "y1": len(tasks),
            "line": {"color": "red", "width": 2, "dash": "dot"}
        })

    fig['layout'].shapes = tuple(shapes)

    # ============================================================
    #   REMOVER TÍTULO AUTOMÁTICO
    # ============================================================
    fig.update_layout(
        title=None,
        margin=dict(t=20)
    )

    # ============================================================
    #   LEGENDA DOS FERIADOS (TRACE INVISÍVEL)
    # ============================================================
    fig.add_trace({
        "x": [None],
        "y": [None],
        "mode": "lines",
        "line": {"color": "red", "width": 2, "dash": "dot"},
        "name": "Feriados"
    })

    grafico_html = fig.to_html(full_html=False)

    # ============================================================
    #   FERIADOS PARA TABELA (sem duplicar anos)
    # ============================================================
    feriados_sem_duplicados = {}
    for data, nome in feriados.items():
        chave_dm = data[5:10]  # MM-DD
        feriados_sem_duplicados[chave_dm] = nome

    feriados_ordenados = dict(
        sorted(
            feriados_sem_duplicados.items(),
            key=lambda x: (int(x[0][0:2]), int(x[0][3:5]))
        )
    )

    return render_template(
        "gantt.html",
        grafico_html=grafico_html,
        feriados=feriados_ordenados
    )
