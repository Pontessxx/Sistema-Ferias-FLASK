"""
gantt_routes.py
----------------
Módulo responsável pela geração da visualização do gráfico Gantt contendo:

- Períodos de férias
- Folgas por assiduidade
- Feriados nacionais, estaduais e municipais
- Realce de finais de semana
- Suporte a tema claro e escuro
- Sistema de filtros por funcionário, mês e ano
"""

from flask import Blueprint, render_template, request
from services.ferias_service import listar_periodos_para_gantt
from services.folga_service import listar_folgas
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import holidays

gantt_bp = Blueprint("gantt", __name__)


# ============================================================================#
# FUNÇÃO PARA OBTER LISTA COMPLETA DE FERIADOS (ANO ATUAL + PRÓXIMO)
# ============================================================================#
def obter_feriados():
    """
    Retorna um dicionário contendo todos os feriados relevantes para o gráfico.

    Inclui:
    - Feriados nacionais e estaduais usando a biblioteca `holidays`.
    - Feriados municipais fixos (ex.: Aniversário de Osasco).
    - Feriados móveis: Carnaval, Corpus Christi, e outros suportados pela lib.

    Formato do retorno:
        {
            "YYYY-MM-DD": "Nome do feriado",
            ...
        }
    """
    ano_atual = dt.datetime.now().year
    ano_prox = ano_atual + 1

    feriados = holidays.Brazil(
        years=[ano_atual, ano_prox],
        state="SP",
        language="pt_BR"
    )

    resultado = {}

    # Feriado municipal
    resultado[f"{ano_atual}-02-19"] = "Aniversário de Osasco"
    resultado[f"{ano_prox}-02-19"] = "Aniversário de Osasco"

    # Feriados móveis + Santo Antônio
    for ano in [ano_atual, ano_prox]:
        try:
            datas = holidays.Brazil(years=[ano]).get_named("Carnaval")
            if datas:
                resultado[datas[0].strftime("%Y-%m-%d")] = "Carnaval"
        except:
            pass

        try:
            datas = holidays.Brazil(years=[ano]).get_named("Corpus Christi")
            if datas:
                resultado[datas[0].strftime("%Y-%m-%d")] = "Corpus Christi"
        except:
            pass

        resultado[f"{ano}-06-13"] = "Santo Antônio"

    # Feriados padrão
    for data, nome in feriados.items():
        if isinstance(data, dt.date):
            resultado[data.strftime("%Y-%m-%d")] = nome

    return resultado


# ============================================================================#
# ROTA DO GRÁFICO GANTT
# ============================================================================#
@gantt_bp.route("/gantt")
def pagina_gantt():
    """
    Gera e exibe o gráfico de Gantt com todos os períodos de férias, folgas,
    feriados e finais de semana.
    """

    # ---------------- TEMA (LIGHT / DARK) ----------------
    theme = request.cookies.get("theme", "light")

    if theme == "dark":
        paper_bg = "#121212"
        plot_bg = "#1a1a1a"
        text_color = "#e0e0e0"
        grid_color = "#333"
        weekend_color = "rgba(255,255,255,0.05)"
        legend_bg = "rgba(0,0,0,0)"
    else:
        paper_bg = "white"
        plot_bg = "white"
        text_color = "#222"
        grid_color = "#ccc"
        weekend_color = "rgba(0,0,0,0.05)"
        legend_bg = "white"

    # ---------------- FILTROS (GET) ----------------
    funcionario_filtro = request.args.get("funcionario") or ""
    mes_filtro = request.args.get("mes") or ""
    ano_filtro = request.args.get("ano") or ""

    # ---------------- DADOS DO BANCO ----------------
    dados_todos = listar_periodos_para_gantt()   # férias
    folgas_todas = listar_folgas()               # folgas
    feriados_dict = obter_feriados()             # feriados (ano atual + próximo)

    # Lista única de funcionários (para possíveis filtros futuros)
    funcionarios_unicos = sorted({d[0] for d in dados_todos})

    # Lista de anos existentes em férias + folgas
    anos_set = set()
    for nome, inicio, fim in dados_todos:
        try:
            anos_set.add(int(inicio[:4]))
            anos_set.add(int(fim[:4]))
        except Exception:
            pass
    for f in folgas_todas:
        try:
            anos_set.add(int(f["data_folga"][:4]))
        except Exception:
            pass
    anos_unicos = sorted(anos_set)

    # Copias que serão filtradas
    dados = list(dados_todos)
    folgas = list(folgas_todas)

    # ---------------- Função auxiliar de filtro ----------------
    def dentro_do_filtro(inicio, fim):
        dt_inicio = dt.datetime.strptime(inicio, "%Y-%m-%d")
        dt_fim = dt.datetime.strptime(fim, "%Y-%m-%d")

        # Filtro por ano (se selecionado)
        if ano_filtro:
            ano_int = int(ano_filtro)
            if dt_inicio.year != ano_int and dt_fim.year != ano_int:
                return False

        # Filtro por mês (se selecionado)
        if mes_filtro:
            mes_int = int(mes_filtro)
            if dt_inicio.month != mes_int and dt_fim.month != mes_int:
                return False

        return True

    # ---------------- FILTRAR POR FUNCIONÁRIO ----------------
    if funcionario_filtro:
        dados = [d for d in dados if d[0] == funcionario_filtro]
        folgas = [f for f in folgas if f["nome"] == funcionario_filtro]

    # ---------------- APLICAR FILTRO DE DATA ----------------
    dados = [d for d in dados if dentro_do_filtro(d[1], d[2])]
    folgas = [
        f for f in folgas
        if dentro_do_filtro(f["data_folga"], f["data_folga"])
    ]

    # =====================================================
    # GERAR LISTA DE TAREFAS (FÉRIAS + FOLGAS)
    # =====================================================
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
        d = f["data_folga"]

        dt_inicio = dt.datetime.strptime(d, "%Y-%m-%d")
        dt_fim = dt_inicio + dt.timedelta(days=1)

        tasks.append({
            "Funcionário": nome,
            "Inicio": dt_inicio.strftime("%Y-%m-%d"),
            "Fim": dt_fim.strftime("%Y-%m-%d"),
            "Tipo": "Folga"
        })

    # Caso não existam resultados com os filtros aplicados
    if not tasks:
        return render_template(
            "gantt.html",
            grafico_html="<h3>Sem dados com esses filtros</h3>",
            feriados={},
            funcionarios=funcionarios_unicos,
            anos=anos_unicos,
            ano_selecionado=ano_filtro
        )

    # =====================================================
    # GERAÇÃO DO GRÁFICO COM PLOTLY
    # =====================================================
    fig = px.timeline(
        tasks,
        x_start="Inicio",
        x_end="Fim",
        color="Tipo",
        color_discrete_map={
            "Férias": "#1e88e5",
            "Folga": "#ffa726"
        },
        y="Funcionário"
    )

    # Hover personalizado, mas mantendo a cor padrão de cada trace
    hovertemplate = (
        "<b>%{customdata[0]}</b><br>"   # Tipo (Férias / Folga)
        "Início: %{base|%b %d, %Y}<br>"
        "Fim: %{x|%b %d, %Y}<br>"
        "Funcionário: %{y}<br>"
        "<extra></extra>"
    )

    for i, trace in enumerate(fig.data):
        tipo = trace.name  # "Férias" ou "Folga"
        custom_data = [[tipo] for _ in trace.x]
        fig.data[i].customdata = custom_data
        fig.data[i].hovertemplate = hovertemplate

    fig.update_yaxes(autorange="reversed", tickfont=dict(size=18))

    shapes = []

    # =====================================================
    # DEFINIR QUAIS ANOS VÃO APARECER NO GRAFICO
    # =====================================================
    ano_atual = dt.datetime.now().year
    if ano_filtro:
        anos_para_grafico = [int(ano_filtro)]
    else:
        # Sem filtro: ano atual + próximo
        anos_para_grafico = [ano_atual, ano_atual + 1]

    # ---------------- FERIADOS (LINHAS VERMELHAS) ----------------
    for data, nome in feriados_dict.items():
        dt_data = dt.datetime.strptime(data, "%Y-%m-%d")
        if dt_data.year not in anos_para_grafico:
            continue

        shapes.append(dict(
            type="line",
            x0=dt_data, x1=dt_data,
            y0=-0.5, y1=len(tasks) - 0.5,
            line=dict(color="red", width=2, dash="dot"),
            xref="x", yref="y"
        ))

    # ---------------- FINAIS DE SEMANA ----------------
    for ano in anos_para_grafico:
        inicio_ano = dt.datetime(ano, 1, 1)
        fim_ano = dt.datetime(ano, 12, 31)
        dias_total = (fim_ano - inicio_ano).days + 1

        for i in range(dias_total):
            dia = inicio_ano + dt.timedelta(days=i)
            if dia.weekday() in (5, 6):  # sábado ou domingo
                shapes.append(dict(
                    type="rect",
                    x0=dia, x1=dia + dt.timedelta(days=1),
                    y0=-0.5, y1=len(tasks) - 0.5,
                    fillcolor=weekend_color,
                    line=dict(width=0),
                    layer="below"
                ))

    # =====================================================
    # LAYOUT E ESTILO
    # =====================================================
    fig.update_layout(
        shapes=shapes,
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=text_color),

        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            zeroline=False,
            tickfont=dict(color=text_color),
            linecolor=grid_color
        ),

        yaxis=dict(
            showgrid=False,
            tickfont=dict(color=text_color)
        ),

        legend=dict(
            bgcolor=legend_bg,
            font=dict(color=text_color)
        )
    )

    # ------- LEGENDA EXTRA (Feriado e Final de Semana) -------
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines",
        line=dict(color="red", width=2, dash="dot"),
        name="Feriados"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=15, color="rgba(200,200,200,0.6)"),
        name="Sábados e Domingos"
    ))

    grafico_html = fig.to_html(full_html=False)

    # =====================================================
    # FERIADOS ORDENADOS PARA A TABELA (MESMA LÓGICA DO GRÁFICO)
    # =====================================================
    feriados_filtrados = {}
    for data, nome in feriados_dict.items():
        ano_data = int(data[:4])
        if ano_data in anos_para_grafico:
            feriados_filtrados[data] = nome

    feriados_ordenados = dict(sorted(
        feriados_filtrados.items(),
        key=lambda x: x[0]
    ))

    return render_template(
        "gantt.html",
        grafico_html=grafico_html,
        feriados=feriados_ordenados,
        funcionarios=funcionarios_unicos,
        anos=anos_unicos,
        ano_selecionado=ano_filtro
    )
