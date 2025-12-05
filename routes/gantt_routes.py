from flask import Blueprint, render_template
from services.ferias_service import listar_periodos_para_gantt
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

    # Feriados nacionais + estaduais SP
    feriados = holidays.Brazil(
        years=[ano_atual, ano_proximo],
        state="SP",
        language="pt_BR"
    )

    # Feriado municipal (Osasco)
    feriados_osasco = {
        f"{ano_atual}-02-19": "Aniversário de Osasco",
        f"{ano_proximo}-02-19": "Aniversário de Osasco"
    }

    all_feriados = {}

    # Converte todas as datas para string YYYY-MM-DD
    for data, nome in feriados.items():
        all_feriados[str(data)] = nome

    # Adiciona Osasco
    all_feriados.update(feriados_osasco)

    return all_feriados



# ============================================================
#   ROTA DO GANTT
# ============================================================
@gantt_bp.route("/gantt")
def pagina_gantt():
    dados = listar_periodos_para_gantt()
    feriados = obter_feriados()

    # ------------------------------
    # Construir tasks para o Gantt
    # ------------------------------
    tasks = []
    for nome, inicio, fim in dados:
        tasks.append(dict(
            Task=nome,
            Start=inicio,
            Finish=fim,
            Resource="Férias"
        ))

    # Criar gráfico Gantt
    fig = ff.create_gantt(
        tasks,
        index_col="Resource",
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        height=600,
    )

    # ------------------------------
    # Inserir linhas dos feriados
    # ------------------------------
    shapes = list(fig['layout'].shapes or [])

    for data, descricao in feriados.items():
        d = dt.datetime.strptime(data, "%Y-%m-%d")

        shapes.append({
            "type": "line",
            "x0": d,
            "y0": -1,
            "x1": d,
            "y1": len(tasks),
            "line": {
                "color": "red",
                "width": 2,
                "dash": "dot"
            }
        })

    fig['layout'].shapes = tuple(shapes)

    # Exportar o HTML do gráfico
    grafico_html = fig.to_html(full_html=False)

    # ============================================================
    #   REMOVER DUPLICADOS (mesmo dia/mês) E ORDENAR
    # ============================================================

    # Ex.: "2025-01-01" → chave somente "01-01"
    feriados_sem_duplicados = {}
    for data, nome in feriados.items():
        chave_dm = data[5:10]  # MM-DD
        feriados_sem_duplicados[chave_dm] = nome  # sobrescreve duplicados

    # Ordenar por mês e dia
    feriados_ordenados = dict(
        sorted(
            feriados_sem_duplicados.items(),
            key=lambda x: (int(x[0][0:2]), int(x[0][3:5]))  # MM-DD → (MM, DD)
        )
    )

    # ============================================================

    return render_template(
        "gantt.html",
        grafico_html=grafico_html,
        feriados=feriados_ordenados
    )
